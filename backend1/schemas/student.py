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
    anh_dai_dien: Optional[str] = None

class SinhVienUpdate(BaseModel):
    ho_ten: Optional[str] = None
    ngay_sinh: Optional[date] = None
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    cccd: Optional[str] = None
    anh_dai_dien: Optional[str] = None

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
    anh_dai_dien: Optional[str] = None

    model_config = {"from_attributes": True}
