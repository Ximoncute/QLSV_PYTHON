from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend1.db.session import get_db
from backend1.models.admission import HSO_XetTuyen, PT_XetTuyen
from backend1.schemas.admission import AdmissionProfileUpdate, AdmissionSubmit
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
        print(f"DEBUG_BACKEND: ma_hso {ma_hso} not found in PT_XetTuyen")
        # Return 400 instead of 404 to distinguish from 'route not found'
        raise HTTPException(
            status_code=400, 
            detail=f"Thí sinh {ma_hso} chưa đăng ký phương thức xét tuyển. Không thể duyệt."
        )
    
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
    from backend1.core.security import decode_access_token
    payload = decode_access_token(token)
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

@router.put("/profile", response_model=dict)
def update_admission_profile(
    data: AdmissionProfileUpdate, 
    db: Session = Depends(get_db), 
    authorization: str = Header(None)
):
    """Update profile of the authenticated candidate"""
    print(f"DEBUG_BACKEND: PUT /admission/profile received. Data: {data}")
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    from backend1.core.security import decode_access_token
    payload = decode_access_token(token)
    ma_tk = payload.get("sub")
    
    hoso = db.query(HSO_XetTuyen).filter(HSO_XetTuyen.ma_tk == ma_tk).first()
    if not hoso:
        print(f"DEBUG_BACKEND: Profile not found for ma_tk: {ma_tk}")
        raise HTTPException(status_code=404, detail="Hồ sơ không tồn tại")
    
    # Update fields if provided
    update_data = data.model_dump(exclude_unset=True)
    if "ho_ten" in update_data: hoso.ho_ten = update_data["ho_ten"]
    if "cccd" in update_data: hoso.cccd = update_data["cccd"]
    if "sdt" in update_data: hoso.sdt = update_data["sdt"]
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Lỗi cơ sở dữ liệu: {str(e)}"}
        
    return {"success": True, "message": "Cập nhật hồ sơ thành công"}

@router.post("/submit", response_model=dict)
def submit_admission(
    data: AdmissionSubmit, 
    db: Session = Depends(get_db), 
    authorization: str = Header(None)
):
    """Submit or update admission method/program selection"""
    print(f"DEBUG_BACKEND: POST /admission/submit received. Data: {data}")
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    from backend1.core.security import decode_access_token
    payload = decode_access_token(token)
    ma_tk = payload.get("sub")
    
    # 1. Ensure Profile Exists
    hoso = db.query(HSO_XetTuyen).filter(HSO_XetTuyen.ma_tk == ma_tk).first()
    if not hoso:
        print(f"DEBUG_BACKEND: Profile not found for ma_tk: {ma_tk}")
        raise HTTPException(status_code=400, detail="Vui lòng hoàn thiện hồ sơ cá nhân trước")
    
    # 2. Extract Data
    ma_nganh = data.ma_nganh
    phuong_thuc = data.phuong_thuc
    diem = str(data.diem or "0.0")
    
    # 3. Create or Update Method selection
    pt = db.query(PT_XetTuyen).filter(PT_XetTuyen.ma_hso == hoso.ma_hso).first()
    
    if pt:
        # Update existing
        pt.ma_nganh = ma_nganh
        pt.phuong_thuc = phuong_thuc
        pt.diem = diem
        pt.trang_thai = "Chờ duyệt" # Reset status on update
        print(f"DEBUG_BACKEND: Updated existing PT record for hoso: {hoso.ma_hso}")
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
        print(f"DEBUG_BACKEND: Created new PT record for hoso: {hoso.ma_hso}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Lỗi cơ sở dữ liệu: {str(e)}"}
        
    return {"success": True, "message": "Nộp hồ sơ thành công"}
