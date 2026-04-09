from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend1.db.session import get_db
from backend1.models.administrative import ThongBao, TB_NguoiNhan, QuanTri
from backend1.models.student import SinhVien
from backend1.core import security
from typing import Any, List, Optional
import datetime

router = APIRouter()

# --- Student Endpoints ---

@router.get("/my", response_model=dict)
def get_my_notifications(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    payload = security.decode_access_token(token)
    ma_sv = payload.get("sub")
    
    # Simple logic: Global notifications + Student specific ones
    # For now, let's just fetch all global ones or those assigned to this student
    notifications = db.query(ThongBao).filter(
        (ThongBao.gui_den == "all")
    ).all()
    
    # Enrich with read status
    # This is a simplified implementation
    return {
        "success": True,
        "data": {
            "thong_bao": [
                {
                    "ma_tb": tb.ma_tb,
                    "tieu_de": tb.tieu_de,
                    "noi_dung": tb.noi_dung,
                    "created_at": tb.created_at,
                    "da_doc": db.query(TB_NguoiNhan).filter(
                        TB_NguoiNhan.ma_tb == tb.ma_tb, 
                        TB_NguoiNhan.ma_sv == ma_sv, 
                        TB_NguoiNhan.da_doc == 1
                    ).first() is not None
                } for tb in notifications
            ],
            "unread_count": 0 # Simplified
        }
    }

@router.post("/read/{ma_tb}", response_model=dict)
def mark_read(ma_tb: str, db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    payload = security.decode_access_token(token)
    ma_sv = payload.get("sub")
    
    # Check if record exists
    read_record = db.query(TB_NguoiNhan).filter(
        TB_NguoiNhan.ma_tb == ma_tb, 
        TB_NguoiNhan.ma_sv == ma_sv
    ).first()
    
    if not read_record:
        read_record = TB_NguoiNhan(
            ma_tb=ma_tb,
            ma_sv=ma_sv,
            da_doc=1,
            thoi_gian_doc=datetime.datetime.utcnow()
        )
        db.add(read_record)
    else:
        read_record.da_doc = 1
        read_record.thoi_gian_doc = datetime.datetime.utcnow()
    
    db.commit()
    return {"success": True}

# --- Admin Endpoints ---

@router.get("/", response_model=dict)
def list_all_notifications(db: Session = Depends(get_db)):
    items = db.query(ThongBao).order_by(ThongBao.created_at.desc()).all()
    data = []
    for i in items:
        admin = db.query(QuanTri).filter(QuanTri.ma_qt == i.ma_qt).first()
        data.append({
            "ma_tb": i.ma_tb,
            "tieu_de": i.tieu_de,
            "noi_dung": i.noi_dung,
            "created_at": i.created_at,
            "ten_admin": admin.ho_ten if admin else "N/A",
            "gui_den": i.gui_den
        })
    return {"success": True, "data": data}

@router.post("/", response_model=dict)
def create_notification(data: dict, db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    if not authorization:
         raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    payload = security.decode_access_token(token)
    ma_qt = payload.get("sub")

    import uuid
    ma_tb = str(uuid.uuid4())[:8]
    
    new_tb = ThongBao(
        ma_tb=ma_tb,
        tieu_de=data.get("tieu_de", "Thông báo mới"),
        noi_dung=data.get("noi_dung"),
        ma_qt=ma_qt,
        gui_den=data.get("gui_den", "all")
    )
    db.add(new_tb)
    db.commit()
    return {"success": True}
