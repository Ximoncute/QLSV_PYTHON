from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend1.db.session import get_db
from backend1.models.student import TotNghiep, SinhVien
from typing import Any

router = APIRouter()

REQUIRED_CREDITS = 120

@router.get("/", response_model=dict)
def list_graduation_review(db: Session = Depends(get_db)):
    """Bulk review of all students for administration"""
    from backend1.repositories.student_repository import StudentRepository
    repo = StudentRepository(db)
    students = db.query(SinhVien).all()
    
    review_data = []
    for s in students:
        results = repo.get_transcript(s.ma_sv)
        
        total_score = 0.0
        total_credits = 0
        for grade, mh in results:
            total_score += grade.diem * mh.so_tin_chi
            total_credits += mh.so_tin_chi
            
        gpa10 = total_score / total_credits if total_credits > 0 else 0.0
        gpa4 = round((gpa10 / 10) * 4, 2)
        
        review_data.append({
            "ma_sv": s.ma_sv,
            "ho_ten": s.ho_ten,
            "gpa": gpa4,
            "credits": total_credits,
            "required": REQUIRED_CREDITS,
            "status": "Đủ điều kiện" if total_credits >= REQUIRED_CREDITS else "Thiếu tín chỉ"
        })
        
    return {"success": True, "data": review_data}

@router.get("/status/{ma_sv}", response_model=dict)
def get_graduation_status(ma_sv: str, db: Session = Depends(get_db)):
    student = db.query(SinhVien).filter(SinhVien.ma_sv == ma_sv).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    tn = db.query(TotNghiep).filter(TotNghiep.ma_sv == ma_sv).first()
    
    if tn:
        return {
            "success": True,
            "data": {
                "ma_sv": ma_sv,
                "da_xet": True,
                "gpa": tn.gpa,
                "xep_loai": tn.xep_loai,
                "is_eligible": True
            }
        }
    else:
        # If not yet graduated, calculate current status
        from backend1.repositories.student_repository import StudentRepository
        repo = StudentRepository(db)
        results = repo.get_transcript(ma_sv)
        
        total_score = 0.0
        total_credits = 0
        for grade, mh in results:
            total_score += grade.diem * mh.so_tin_chi
            total_credits += mh.so_tin_chi
        
        gpa10 = total_score / total_credits if total_credits > 0 else 0.0
        gpa4 = (gpa10 / 10) * 4
        
        rank = "F"
        if gpa4 >= 3.6: rank = "Xuất sắc"
        elif gpa4 >= 3.2: rank = "Giỏi"
        elif gpa4 >= 2.5: rank = "Khá"
        elif gpa4 >= 2.0: rank = "Trung bình"
        
        return {
            "success": True,
            "data": {
                "ma_sv": ma_sv,
                "da_xet": False,
                "gpa_thang_4_hien_tai": round(gpa4, 2),
                "xep_loai_du_kien": rank,
                "tong_tin_chi": total_credits,
                "expected": REQUIRED_CREDITS,
                "is_eligible": total_credits >= REQUIRED_CREDITS
            }
        }
