from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend1.db.session import get_db
from backend1.repositories.student_repository import StudentRepository
from backend1.schemas.student import SinhVienRead
from backend1.models.student import SinhVien
from backend1.models.academic import Lop, Nganh, Khoa

router = APIRouter()

def get_scale4(diem10: float) -> float:
    if diem10 >= 8.5: return 4.0
    if diem10 >= 7.0: return 3.0
    if diem10 >= 5.5: return 2.0
    if diem10 >= 4.0: return 1.0
    return 0.0

@router.get("/{ma_sv}/transcript", response_model=Any)
@router.get("/diem/{ma_sv}", response_model=Any)
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

@router.get("/gpa/{ma_sv}", response_model=dict)
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

@router.get("/{ma_sv}", response_model=dict)
@router.get("/{ma_sv}/profile", response_model=dict)
def get_student_profile(ma_sv: str, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    # Ensure we get the latest student data from DB
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

@router.get("/tuition/{ma_sv}", response_model=dict)
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

@router.get("/", response_model=dict)
def list_students(db: Session = Depends(get_db)):
    items = db.query(SinhVien).order_by(SinhVien.ma_sv.desc()).all()
    return {"success": True, "data": [SinhVienRead.model_validate(i) for i in items]}
