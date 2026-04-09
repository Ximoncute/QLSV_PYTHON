from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend1.db.session import get_db
from backend1.models.administrative import QuanTri
from backend1.models.student import SinhVien
from backend1.models.admission import TK_XetTuyen
from backend1.core import security
from backend1.core.config import settings

print("DEBUG: Loading auth.py router...")
router = APIRouter()

@router.post("/login/admin")
def login_admin(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    print(f"DEBUG_AUTH: Admin Login Attempt - Email: '{form_data.username}', Pass length: {len(form_data.password)}")
    admin = db.query(QuanTri).filter(QuanTri.email == form_data.username).first()
    
    if not admin:
        print(f"DEBUG_AUTH: Admin not found for email: {form_data.username}")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    if not security.verify_password(form_data.password, admin.mat_khau):
        print(f"DEBUG_AUTH: Password mismatch for admin: {form_data.username}")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    print(f"DEBUG_AUTH: Admin Login SUCCESS: {admin.ma_qt}")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            admin.ma_qt, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": "admin",
        "user": {
            "ma_qt": admin.ma_qt,
            "ho_ten": admin.ho_ten,
            "email": admin.email
        }
    }

@router.post("/login/student")
def login_student(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    student = db.query(SinhVien).filter(SinhVien.ma_sv == form_data.username).first()
    if not student or not security.verify_password(form_data.password, student.mat_khau):
        raise HTTPException(status_code=400, detail="Incorrect Student ID or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    result = {
        "access_token": security.create_access_token(
            student.ma_sv, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": "student",
        "user": {
            "ma_sv": student.ma_sv,
            "ho_ten": student.ho_ten,
            "email": student.email
        }
    }
    print(f"DEBUG_BACKEND: Student Login Successful for {student.ma_sv}. User data: {result['user']}")
    return result
@router.post("/login/candidate")
def login_candidate(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    candidate = db.query(TK_XetTuyen).filter(TK_XetTuyen.email == form_data.username).first()
    if not candidate or not security.verify_password(form_data.password, candidate.mat_khau):
        raise HTTPException(status_code=400, detail="Incorrect Email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            candidate.ma_tk, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": "candidate",
        "user": {
            "ma_tk": candidate.ma_tk,
            "email": candidate.email,
            "ho_ten": candidate.hoso.ho_ten if candidate.hoso else "Thí sinh mới"
        }
    }

@router.post("/register/candidate")
def register_candidate(
    data: dict, db: Session = Depends(get_db)
) -> Any:
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
         raise HTTPException(status_code=400, detail="Email and password required")
    
    # Check exists
    if db.query(TK_XetTuyen).filter(TK_XetTuyen.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    import uuid
    from backend1.models.admission import HSO_XetTuyen
    ma_tk = "TK" + str(uuid.uuid4())[:8].upper()
    ma_hso = "HS" + str(uuid.uuid4())[:8].upper()
    
    new_acc = TK_XetTuyen(
        ma_tk=ma_tk,
        email=email,
        mat_khau=security.get_password_hash(password)
    )
    db.add(new_acc)
    
    # Auto-create placeholder profile to prevent dashboard crashes
    placeholder_name = email.split('@')[0].capitalize()
    new_hoso = HSO_XetTuyen(
        ma_hso=ma_hso,
        ma_tk=ma_tk,
        ho_ten=placeholder_name,
        cccd=f"CSB_{ma_tk}", # Cần bổ sung
        sdt=f"CSB_{ma_tk}"
    )
    db.add(new_hoso)
    
    db.commit()
    return {"success": True, "message": "Đăng ký thành công", "ma_tk": ma_tk}
