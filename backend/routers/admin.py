import random
from datetime import date
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend1.db.session import get_db
from backend1.repositories.admission_repository import AdmissionRepository
from backend1.repositories.student_repository import StudentRepository
from backend1.models.academic import Lop
from backend1.models.student import SinhVien
from backend1.models.academic import Khoa, Nganh, Lop, MonHoc
from backend1.models.administrative import QuanTri
from backend1.models.student import SinhVien
from backend1.models.admission import HSO_XetTuyen, PT_XetTuyen, TK_XetTuyen
from backend1.schemas.admin import (
    GradeInput, ApproveResponse, KhoaCreate, NganhCreate, LopCreate, 
    KhoaRead, NganhRead, LopRead, EnrollRequest
)
from backend1.core import security

router = APIRouter()

# --- Academic CRUD ---

# --- Khoa CRUD ---
@router.get("/khoa/", response_model=dict)
def list_khoa(db: Session = Depends(get_db)):
    items = db.query(Khoa).all()
    return {"success": True, "data": [KhoaRead.model_validate(i) for i in items]}

@router.post("/khoa/", response_model=Any)
def create_khoa(item: KhoaCreate, db: Session = Depends(get_db)):
    db_item = Khoa(**item.dict())
    db.add(db_item)
    db.commit()
    return {"success": True, "message": "Created"}

@router.put("/khoa/{ma_khoa}", response_model=Any)
def update_khoa(ma_khoa: str, item: KhoaCreate, db: Session = Depends(get_db)):
    db_item = db.query(Khoa).filter(Khoa.ma_khoa == ma_khoa).first()
    if not db_item: raise HTTPException(404, "Not found")
    for k, v in item.dict().items(): setattr(db_item, k, v)
    db.commit()
    return {"success": True}

@router.delete("/khoa/{ma_khoa}", response_model=Any)
def delete_khoa(ma_khoa: str, db: Session = Depends(get_db)):
    db_item = db.query(Khoa).filter(Khoa.ma_khoa == ma_khoa).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"success": True}

# --- Nganh CRUD ---
@router.get("/nganh/", response_model=dict)
def list_nganh(db: Session = Depends(get_db)):
    items = db.query(Nganh).all()
    return {"success": True, "data": [NganhRead.model_validate(i) for i in items]}

@router.post("/nganh/", response_model=Any)
def create_nganh(item: NganhCreate, db: Session = Depends(get_db)):
    db_item = Nganh(**item.dict())
    db.add(db_item)
    db.commit()
    return {"success": True, "message": "Created"}

@router.put("/nganh/{ma_nganh}", response_model=Any)
def update_nganh(ma_nganh: str, item: NganhCreate, db: Session = Depends(get_db)):
    db_item = db.query(Nganh).filter(Nganh.ma_nganh == ma_nganh).first()
    if not db_item: raise HTTPException(404, "Not found")
    for k, v in item.dict().items(): setattr(db_item, k, v)
    db.commit()
    return {"success": True}

@router.delete("/nganh/{ma_nganh}", response_model=Any)
def delete_nganh(ma_nganh: str, db: Session = Depends(get_db)):
    db_item = db.query(Nganh).filter(Nganh.ma_nganh == ma_nganh).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"success": True}

# --- Lop CRUD ---
@router.get("/lop/", response_model=dict)
def list_lop(db: Session = Depends(get_db)):
    items = db.query(Lop).all()
    return {"success": True, "data": [LopRead.model_validate(i) for i in items]}

@router.post("/lop/", response_model=Any)
def create_lop(item: LopCreate, db: Session = Depends(get_db)):
    db_item = Lop(**item.dict())
    db.add(db_item)
    db.commit()
    return {"success": True, "message": "Created"}

@router.put("/lop/{ma_lop}", response_model=Any)
def update_lop(ma_lop: str, item: LopCreate, db: Session = Depends(get_db)):
    db_item = db.query(Lop).filter(Lop.ma_lop == ma_lop).first()
    if not db_item: raise HTTPException(404, "Not found")
    for k, v in item.dict().items(): setattr(db_item, k, v)
    db.commit()
    return {"success": True}

@router.delete("/lop/{ma_lop}", response_model=Any)
def delete_lop(ma_lop: str, db: Session = Depends(get_db)):
    db_item = db.query(Lop).filter(Lop.ma_lop == ma_lop).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"success": True}

# --- Admissions ---
@router.get("/applications", response_model=Any)
def get_all_applications(db: Session = Depends(get_db)):
    repo = AdmissionRepository(db)
    return {"success": True, "data": repo.get_all_applications()}

@router.post("/enroll", response_model=Any)
def enroll_candidate(request: EnrollRequest, db: Session = Depends(get_db)):
    """Convert approved candidate to student and assign class automatically"""
    # 1. Fetch Profile & Method
    hoso = db.query(HSO_XetTuyen).filter(HSO_XetTuyen.ma_hso == request.ma_hso).first()
    if not hoso:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ thí sinh")
    
    pt = db.query(PT_XetTuyen).filter(PT_XetTuyen.ma_hso == hoso.ma_hso).first()
    if not pt or pt.trang_thai != "Đã duyệt":
        raise HTTPException(status_code=400, detail="Hồ sơ chưa được duyệt hoặc không hợp lệ để nhập học")

    ma_nganh = pt.ma_nganh
    if not ma_nganh:
        raise HTTPException(status_code=400, detail="Hồ sơ chưa đăng ký ngành học")

    # 2. Check if already enrolled
    existing_sv = db.query(SinhVien).filter(SinhVien.ma_hso == hoso.ma_hso).first()
    if existing_sv:
        raise HTTPException(status_code=400, detail="Thí sinh này đã nhập học trước đó")

    # 3. Handle Automated Class Assignment
    current_year = date.today().year
    year_prefix = str(current_year)[2:] # e.g., "26" for 2026
    
    ma_lop = request.ma_lop
    if not ma_lop:
        # Default format: D{YY}{MA_NGANH}1 (e.g., D26CNPM1)
        ma_lop = f"D{year_prefix}{ma_nganh}1"
    
    lop = db.query(Lop).filter(Lop.ma_lop == ma_lop).first()
    if not lop:
        # Auto-create class if it doesn't exist
        nganh = pt.nganh
        ten_nganh = nganh.ten_nganh if nganh else ma_nganh
        new_lop = Lop(
            ma_lop=ma_lop,
            ten_lop=f"Lớp {ten_nganh} K{year_prefix}",
            ma_nganh=ma_nganh
        )
        db.add(new_lop)
        db.flush() # Ensure it's available for student creation
        lop = new_lop

    # 4. Generate Automated Student ID (MSSV)
    # Format: D{YY}{MA_NGANH}{SEQ} e.g., D26CNPM001
    prefix = f"D{year_prefix}{ma_nganh}"
    existing_count = db.query(SinhVien).filter(SinhVien.ma_sv.like(f"{prefix}%")).count()
    new_ma_sv = f"{prefix}{existing_count + 1:03d}"

    # 5. Create Student Record
    tk = hoso.tai_khoan
    if not tk:
        raise HTTPException(status_code=400, detail="Tài khoản thí sinh không tồn tại")

    new_student = SinhVien(
        ma_sv=new_ma_sv,
        ho_ten=hoso.ho_ten,
        ngay_sinh=date(2003, 1, 1), # Default
        email=tk.email,
        so_dien_thoai=hoso.sdt,
        cccd=hoso.cccd,
        mat_khau=security.get_password_hash("123456"), # Use default password
        ma_lop=ma_lop,
        ma_hso=hoso.ma_hso,
        trang_thai="active",
        ngay_nhap_hoc=date.today()
    )
    
    db.add(new_student)
    
    # 6. Update Admission Status
    pt.trang_thai = "Đã nhập học"
    
    db.commit()
    
    return {
        "success": True, 
        "message": f"Nhập học thành công cho sinh viên {hoso.ho_ten}",
        "data": {
            "ma_sv": new_ma_sv,
            "ho_ten": hoso.ho_ten,
            "lop": lop.ten_lop,
            "ma_lop": ma_lop
        }
    }

@router.post("/sinh-vien/{ma_sv}/reset-password", response_model=Any)
def reset_student_password(ma_sv: str, db: Session = Depends(get_db)):
    """Reset student password to default '123456'"""
    student = db.query(SinhVien).filter(SinhVien.ma_sv == ma_sv).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    
    student.mat_khau = security.get_password_hash("123456")
    db.commit()
    return {"success": True, "message": f"Đã reset mật khẩu cho sinh viên {ma_sv} về mặc định (123456)"}

# --- Admin Accounts ---
@router.get("/quan-tri/", response_model=Any)
def list_admins(db: Session = Depends(get_db)):
    items = db.query(QuanTri).all()
    data = [{"ma_qt": i.ma_qt, "ho_ten": i.ho_ten, "email": i.email} for i in items]
    return {"success": True, "data": data}

@router.post("/quan-tri/", response_model=Any)
def create_admin(data: dict, db: Session = Depends(get_db)):
    from backend1.core.security import get_password_hash
    db_item = QuanTri(
        ma_qt=data["ma_qt"],
        ho_ten=data["ho_ten"],
        email=data["email"],
        mat_khau=get_password_hash(data.get("password_hash", "admin123"))
    )
    db.add(db_item)
    db.commit()
    return {"success": True}

@router.put("/quan-tri/{ma_qt}", response_model=Any)
def update_admin(ma_qt: str, data: dict, db: Session = Depends(get_db)):
    db_item = db.query(QuanTri).filter(QuanTri.ma_qt == ma_qt).first()
    if not db_item: raise HTTPException(404, "Not found")
    db_item.ho_ten = data.get("ho_ten", db_item.ho_ten)
    db_item.email = data.get("email", db_item.email)
    if "password_hash" in data:
        from backend1.core.security import get_password_hash
        db_item.mat_khau = get_password_hash(data["password_hash"])
    db.commit()
    return {"success": True}

@router.delete("/quan-tri/{ma_qt}", response_model=Any)
def delete_admin(ma_qt: str, db: Session = Depends(get_db)):
    db_item = db.query(QuanTri).filter(QuanTri.ma_qt == ma_qt).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"success": True}
