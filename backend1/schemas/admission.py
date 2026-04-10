from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class TKCreate(BaseModel):
    MaTK: str
    Email: EmailStr
    MatKhau: str

class HSOCreate(BaseModel):
    MaHSO: str
    HoTen: str
    CCCD: str = Field(..., min_length=10, max_length=10)
    SDT: str = Field(..., min_length=10, max_length=10)

class PTXTCreate(BaseModel):
    MaPTXT: str
    MaNganh: str
    PhuongThuc: str
    Diem: float

class AdmissionProfileUpdate(BaseModel):
    ho_ten: Optional[str] = None
    cccd: Optional[str] = None
    sdt: Optional[str] = None

class AdmissionSubmit(BaseModel):
    ma_nganh: str
    phuong_thuc: str
    diem: Optional[str] = "0.0"
