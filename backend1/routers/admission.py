from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend1.db.session import get_db
from backend1.models.admission import HSO_XetTuyen, PT_XetTuyen
from typing import List

router = APIRouter()

@router.get("/hoso/", response_model=dict)
def list_hoso(db: Session = Depends(get_db)):
    """Fetch all admission profiles with their status"""
    profiles = db.query(HSO_XetTuyen).all()
    results = []
    for p in profiles:
        # Get the primary status from PT_XetTuyen (simplified for list)
        pt = db.query(PT_XetTuyen).filter(PT_XetTuyen.ma_hso == p.ma_hso).first()
        results.append({
            "ma_hso": p.ma_hso,
            "ho_ten": p.ho_ten,
            "cccd": p.cccd,
            "sdt": p.sdt,
            "status": pt.trang_thai if pt else "Chưa đăng ký PT"
        })
    return {"success": True, "data": results}

@router.post("/approve/{ma_hso}", response_model=dict)
def approve_hoso(ma_hso: str, db: Session = Depends(get_db)):
    """Approve candidate status"""
    pt = db.query(PT_XetTuyen).filter(PT_XetTuyen.ma_hso == ma_hso).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Hồ sơ không có phương thức xét tuyển")
    
    pt.trang_thai = "Đã duyệt"
    db.commit()
    return {"success": True, "message": f"Đã duyệt hồ sơ {ma_hso}"}

@router.post("/revoke/{ma_hso}", response_model=dict)
def revoke_hoso(ma_hso: str, db: Session = Depends(get_db)):
    """Revoke candidate approval"""
    pt = db.query(PT_XetTuyen).filter(PT_XetTuyen.ma_hso == ma_hso).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Hồ sơ không tìm thấy")
    
    pt.trang_thai = "Chờ duyệt"
    db.commit()
    return {"success": True, "message": f"Đã thu hồi hồ sơ {ma_hso}"}
@router.get("/my", response_model=dict)
def get_my_admission_profile(db: Session = Depends(get_db), authorization: str = Header(None)):
    """Fetch profile of the authenticated candidate"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    from backend1.core import security
    payload = security.decode_access_token(token)
    ma_tk = payload.get("sub")
    
    hoso = db.query(HSO_XetTuyen).filter(HSO_XetTuyen.ma_tk == ma_tk).first()
    if not hoso:
         return {"success": True, "data": {"status": "Chưa hoàn thiện hồ sơ", "ma_tk": ma_tk}}
    
    pt = db.query(PT_XetTuyen).filter(PT_XetTuyen.ma_hso == hoso.ma_hso).first()
    
    return {
        "success": True,
        "data": {
            "ma_hso": hoso.ma_hso,
            "ho_ten": hoso.ho_ten,
            "cccd": hoso.cccd,
            "sdt": hoso.sdt,
            "ma_tk": ma_tk,
            "method": {
                "ma_ptxt": pt.ma_ptxt if pt else "N/A",
                "phuong_thuc": pt.phuong_thuc if pt else "Chưa đăng ký",
                "diem": pt.diem if pt else "0.0",
                "ma_nganh": pt.ma_nganh if pt else "N/A",
                "trang_thai": pt.trang_thai if pt else "Chờ đăng ký",
                "ten_nganh": pt.nganh.ten_nganh if pt and pt.nganh else "Chưa chọn ngành"
            },
            "status": pt.trang_thai if pt else "Chờ đăng ký phương thức"
        }
    }

@router.post("/submit", response_model=dict)
def submit_admission(data: dict, db: Session = Depends(get_db), authorization: str = Header(None)):
    """Submit or update admission method/program selection"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    from backend1.core import security
    payload = security.decode_access_token(token)
    ma_tk = payload.get("sub")
    
    # 1. Ensure Profile Exists
    hoso = db.query(HSO_XetTuyen).filter(HSO_XetTuyen.ma_tk == ma_tk).first()
    if not hoso:
        raise HTTPException(status_code=400, detail="Vui lòng hoàn thiện hồ sơ cá nhân trước")
    
    # 2. Extract Data
    ma_nganh = data.get("ma_nganh")
    phuong_thuc = data.get("phuong_thuc")
    diem = str(data.get("diem", "0.0"))
    
    if not ma_nganh or not phuong_thuc:
        raise HTTPException(status_code=400, detail="Thiếu thông tin ngành hoặc phương thức")
    
    # 3. Create or Update Method selection
    pt = db.query(PT_XetTuyen).filter(PT_XetTuyen.ma_hso == hoso.ma_hso).first()
    
    if pt:
        # Update existing
        pt.ma_nganh = ma_nganh
        pt.phuong_thuc = phuong_thuc
        pt.diem = diem
        pt.trang_thai = "Chờ duyệt" # Reset status on update
    else:
        # Create new
        import uuid
        ma_ptxt = "PT" + str(uuid.uuid4())[:8].upper()
        new_pt = PT_XetTuyen(
            ma_ptxt=ma_ptxt,
            ma_hso=hoso.ma_hso,
            ma_nganh=ma_nganh,
            phuong_thuc=phuong_thuc,
            diem=diem,
            trang_thai="Chờ duyệt"
        )
        db.add(new_pt)
    
    db.commit()
    return {"success": True, "message": "Nộp hồ sơ thành công"}
