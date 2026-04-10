from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend1.db.session import get_db
from backend1.repositories.student_repository import StudentRepository
from backend1.schemas.student import SinhVienRead, SinhVienUpdate
from backend1.models.student import SinhVien, KQ_HocTap
from backend1.models.academic import Lop, Nganh, Khoa, MonHoc
from backend1.schemas.admin import GradeInput
from fastapi.responses import Response
import io
import os
from datetime import datetime

# Optional: Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

student_router = APIRouter()
academic_router = APIRouter()

def get_scale4(diem10: float) -> float:
    if diem10 >= 8.5: return 4.0
    if diem10 >= 7.0: return 3.0
    if diem10 >= 5.5: return 2.0
    if diem10 >= 4.0: return 1.0
    return 0.0

@academic_router.get("/{ma_sv}/transcript", response_model=Any)
@academic_router.get("/diem/{ma_sv}", response_model=Any)
def get_transcript(ma_sv: str, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    results = repo.get_transcript(ma_sv)
    
    if not results:
        return {"success": True, "ma_sv": ma_sv, "grades": [], "data": [], "grouped_data": {}, "gpa10": 0.0, "gpa4": 0.0, "rank": "None"}
    
    total_score10 = 0.0
    total_score4 = 0.0
    total_credits = 0
    grade_list = []
    grouped_data = {}
    
    for grade_obj, mh in results:
        g10 = grade_obj.diem
        g4 = get_scale4(g10)
        credits = mh.so_tin_chi
        # Ensure we have a string for hoc_ky
        hk_name = str(grade_obj.hoc_ky) if grade_obj.hoc_ky else "Chưa xác định"
        
        total_score10 += g10 * credits
        total_score4 += g4 * credits
        total_credits += credits
        
        item = {
            "ma_mh": mh.ma_mh, 
            "ten_mh": mh.ten_mh, 
            "so_tin_chi": credits, 
            "diem": g10,
            "diem4": g4,
            "hoc_ky": hk_name
        }
        grade_list.append(item)
        
        # Explicit grouping
        if hk_name not in grouped_data:
            grouped_data[hk_name] = []
        grouped_data[hk_name].append(item)
    
    # Fallback to ensure grouped_data is NEVER empty if we have results
    if results and not grouped_data:
        grouped_data["Học kỳ hiện tại"] = grade_list

    gpa10 = round(total_score10 / total_credits, 2) if total_credits > 0 else 0.0
    gpa4 = round(total_score4 / total_credits, 2) if total_credits > 0 else 0.0
    
    # Calculate Rank based on GPA 4.0
    rank = "F"
    if gpa4 >= 3.6: rank = "Xuất sắc"
    elif gpa4 >= 3.2: rank = "Giỏi"
    elif gpa4 >= 2.5: rank = "Khá"
    elif gpa4 >= 2.0: rank = "Trung bình"
    
    try:
        repo.update_tot_nghiep(ma_sv, gpa4, rank)
    except Exception as e:
        print(f"WARNING: Could not update graduation status: {e}")
    
    
    return {
        "success": True, 
        "ma_sv": ma_sv, 
        "grades": grade_list, 
        "data": grade_list, 
        "grouped_data": grouped_data,
        "gpa10": gpa10, 
        "gpa4": gpa4, 
        "rank": rank
    }

@academic_router.get("/gpa/{ma_sv}", response_model=dict)
def get_gpa(ma_sv: str, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    results = repo.get_transcript(ma_sv)
    
    total_score = 0.0
    total_credits = 0
    for grade, mh in results:
        total_score += grade.diem * mh.so_tin_chi
        total_credits += mh.so_tin_chi
    
    gpa10 = round(total_score / total_credits, 2) if total_credits > 0 else 0.0
    gpa4 = round((gpa10 / 10) * 4, 2)
    
    return {
        "success": True,
        "data": {
            "ma_sv": ma_sv,
            "gpa_thang_10": gpa10,
            "gpa_thang_4": gpa4,
            "tong_tin_chi": total_credits,
            "so_mon": len(results)
        }
    }

@student_router.get("/{ma_sv}", response_model=dict)
@student_router.get("/{ma_sv}/profile", response_model=dict)
def get_student_profile(ma_sv: str, db: Session = Depends(get_db)):
    student = db.query(SinhVien).filter(SinhVien.ma_sv == ma_sv).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    lop = None
    nganh = None
    khoa = None
    if student.ma_lop:
        lop = db.query(Lop).filter(Lop.ma_lop == student.ma_lop).first()
        if lop:
            nganh = db.query(Nganh).filter(Nganh.ma_nganh == lop.ma_nganh).first()
            if nganh:
                khoa = db.query(Khoa).filter(Khoa.ma_khoa == nganh.ma_khoa).first()
    
    return {
        "success": True, 
        "data": {
            "sinh_vien": SinhVienRead.model_validate(student),
            "lop": {"ma_lop": lop.ma_lop, "ten_lop": lop.ten_lop} if lop else None,
            "nganh": {"ma_nganh": nganh.ma_nganh, "ten_nganh": nganh.ten_nganh} if nganh else None,
            "khoa": {"ma_khoa": khoa.ma_khoa, "ten_khoa": khoa.ten_khoa} if khoa else None
        }
    }

@student_router.put("/{ma_sv}", response_model=dict)
def update_student_profile(ma_sv: str, data: SinhVienUpdate, db: Session = Depends(get_db)):
    student = db.query(SinhVien).filter(SinhVien.ma_sv == ma_sv).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return {"success": True, "message": "No changes detected"}

    for key, value in update_data.items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    return {"success": True, "message": "Profile updated successfully"}

@academic_router.get("/tuition/{ma_sv}", response_model=dict)
def get_tuition(ma_sv: str, db: Session = Depends(get_db)):
    # Fetch tuition records for the student
    from backend1.models.student import HocPhi
    
    hoc_phis = db.query(HocPhi).filter(HocPhi.ma_sv == ma_sv).all()
    
    if not hoc_phis:
        return {
            "success": True,
            "data": {
                "overall_status": "Chưa có thông tin học phí",
                "semesters": []
            }
        }
    
    semesters = []
    for hp in hoc_phis:
        details = []
        for detail in hp.chi_tiets:
            details.append({
                "name": detail.ten_khoan_muc,
                "amount": detail.so_tien,
                "status": detail.trang_thai
            })
            
        semesters.append({
            "semester_name": hp.ten_hoc_ky,
            "total_tuition": hp.tong_tien,
            "paid": hp.da_dong,
            "remaining": hp.con_no,
            "status": hp.trang_thai,
            "deadline": str(hp.han_nop) if hp.han_nop else "N/A",
            "details": details
        })
    
    return {
        "success": True,
        "data": {
            "overall_status": "Đang trong quá trình hoàn thành học phí" if any(s["remaining"] > 0 for s in semesters) else "Đã hoàn thành học phí",
            "semesters": semesters
        }
    }


@academic_router.get("/tuition/{ma_sv}/export")
def export_invoice(ma_sv: str, db: Session = Depends(get_db)):
    from backend1.models.student import HocPhi
    student = db.query(SinhVien).filter(SinhVien.ma_sv == ma_sv).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    hoc_phis = db.query(HocPhi).filter(HocPhi.ma_sv == ma_sv).all()
    if not hoc_phis:
        raise HTTPException(status_code=404, detail="No tuition data found")

    if not HAS_REPORTLAB:
        # Fallback to plain text if reportlab is missing
        output = io.StringIO()
        output.write(f"HOA DON HOC PHI - SINH VIEN: {student.ho_ten} ({student.ma_sv})\n")
        output.write("-" * 50 + "\n")
        for hp in hoc_phis:
            output.write(f"Hoc ky: {hp.ten_hoc_ky}\n")
            output.write(f"Tong tien: {hp.tong_tien:,.0f} VND\n")
            output.write(f"Da dong: {hp.da_dong:,.0f} VND\n")
            output.write(f"Con no: {hp.con_no:,.0f} VND\n")
            output.write("-" * 20 + "\n")
        
        return Response(
            content=output.getvalue(),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=invoice_{ma_sv}.txt"}
        )

    # Generate PDF using reportlab
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width/2, height - 50, "HOA DON HOC PHI")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Sinh vien: {student.ho_ten}")
    p.drawString(50, height - 120, f"MSSV: {student.ma_sv}")
    p.drawString(50, height - 140, f"Ngay xuat: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    y = height - 180
    for hp in hoc_phis:
        if y < 100: # New page if needed
            p.showPage()
            y = height - 50
            
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Hoc ky: {hp.ten_hoc_ky}")
        y -= 25
        
        p.setFont("Helvetica", 12)
        p.drawString(70, y, f"Tong tien hoc phi: {hp.tong_tien:,.0f} VND")
        y -= 20
        p.drawString(70, y, f"Da thanh toan: {hp.da_dong:,.0f} VND")
        y -= 20
        p.drawString(70, y, f"Con no: {hp.con_no:,.0f} VND")
        y -= 20
        p.drawString(70, y, f"Han nop: {hp.han_nop if hp.han_nop else 'N/A'}")
        y -= 30
        p.line(50, y+10, width-50, y+10)
        y -= 20

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{ma_sv}.pdf"}
    )

@student_router.get("/", response_model=dict)
def list_students(db: Session = Depends(get_db)):
    items = db.query(SinhVien).order_by(SinhVien.ma_sv.desc()).all()
    return {"success": True, "data": [SinhVienRead.model_validate(i) for i in items]}

@academic_router.post("/save-grade", response_model=dict)
def post_grade(data: GradeInput, db: Session = Depends(get_db)):
    """Add or update a student's grade for a subject"""
    # 1. Verify student exists
    student = db.query(SinhVien).filter(SinhVien.ma_sv == data.ma_sv).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sinh viên {data.ma_sv}")
    
    # 2. Verify subject exists
    subject = db.query(MonHoc).filter(MonHoc.ma_mh == data.ma_mh).first()
    if not subject:
        # Fallback: Search by name if ID lookup fails
        subject = db.query(MonHoc).filter(MonHoc.ten_mh.ilike(f"%{data.ma_mh}%")).first()
        
    if not subject:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy môn học có mã hoặc tên là '{data.ma_mh}'")
    
    # 3. Create or update the grade record
    # Check if a grade for this student, subject, and semester already exists
    grade_obj = db.query(KQ_HocTap).filter(
        KQ_HocTap.ma_sv == data.ma_sv,
        KQ_HocTap.ma_mh == subject.ma_mh,
        KQ_HocTap.hoc_ky == data.hoc_ky
    ).first()
    
    if grade_obj:
        grade_obj.diem = data.diem
        # print(f"DEBUG_BACKEND: Updated grade for {data.ma_sv} - {data.ma_mh}")
    else:
        grade_obj = KQ_HocTap(
            ma_sv=data.ma_sv,
            ma_mh=subject.ma_mh,
            hoc_ky=data.hoc_ky,
            diem=data.diem
        )
        db.add(grade_obj)
        # print(f"DEBUG_BACKEND: Created new grade for {data.ma_sv} - {data.ma_mh}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
        
    return {"success": True, "message": "Đã lưu kết quả học tập thành công"}
