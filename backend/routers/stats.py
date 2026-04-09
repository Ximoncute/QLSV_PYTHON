from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend1.db.session import get_db
from backend1.models.academic import Khoa, Nganh, Lop
from backend1.models.student import SinhVien

router = APIRouter()

@router.get("/v4/stats") # Keeping alias for verification
@router.get("/stats")
@router.get("/dashboard-stats")
@router.get("/dashboard-data")
def get_admin_stats_final(db: Session = Depends(get_db)):
    """The consolidated and verified statistics handler for the Admin Dashboard"""
    
    # 1. Base Counts
    total_sinh_vien = db.query(func.count(SinhVien.ma_sv)).scalar() or 0
    total_lop = db.query(func.count(Lop.ma_lop)).scalar() or 0
    total_khoa = db.query(func.count(Khoa.ma_khoa)).scalar() or 0
    total_nganh = db.query(func.count(Nganh.ma_nganh)).scalar() or 0
    
    # 2. Admissions Summary
    from backend1.models.admission import PT_XetTuyen
    total_pending = db.query(func.count(PT_XetTuyen.ma_ptxt)).filter(PT_XetTuyen.trang_thai.ilike("Ch%")).scalar() or 0

    # 3. System Snapshot
    from backend1.models.administrative import ThongBao
    total_tb = db.query(func.count(ThongBao.ma_tb)).scalar() or 0

    # 4. DB Infrastructure Info
    import os
    db_size_str = "0.0 KB"
    try:
        db_path = "university.db"
        if not os.path.exists(db_path):
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "university.db")
            
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            if size < 1024 * 1024:
                db_size_str = f"{size / 1024:.1f} KB"
            else:
                db_size_str = f"{size / (1024 * 1024):.1f} MB"
    except: pass

    # 5. Faculty Distribution (Analytics for Chart)
    distribution = db.query(Khoa.ten_khoa, func.count(SinhVien.ma_sv)).\
        join(Lop, SinhVien.ma_lop == Lop.ma_lop).\
        join(Nganh, Lop.ma_nganh == Nganh.ma_nganh).\
        join(Khoa, Nganh.ma_khoa == Khoa.ma_khoa).\
        group_by(Khoa.ten_khoa).all()

    return {
        "success": True,
        "VERSION": "STAT_FINAL_CONSOLIDATED_V1",
        "data": {
            "total_sinh_vien": total_sinh_vien,
            "total_lop": total_lop,
            "total_khoa": total_khoa,
            "total_nganh": total_nganh,
            "total_pending_admissions": total_pending,
            "total_notifications": total_tb,
            "db_size": db_size_str,
            "system_status": "Ổn định",
            "faculty_distribution": [
                {"name": str(d[0]), "count": int(d[1])} for d in distribution
            ]
        }
    }
