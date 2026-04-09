from pydantic import BaseModel
from datetime import date
from typing import Optional

class SinhVienCreate(BaseModel):
    ma_sv: str
    ho_ten: str
    ngay_sinh: date
    email: str
    mat_khau: str
    ma_lop: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    cccd: Optional[str] = None

class SinhVienRead(BaseModel):
    ma_sv: str
    ho_ten: str
    ngay_sinh: date
    email: str
    ma_lop: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    cccd: Optional[str] = None
    trang_thai: Optional[str] = "active"
    ngay_nhap_hoc: Optional[date] = None

    model_config = {"from_attributes": True}
