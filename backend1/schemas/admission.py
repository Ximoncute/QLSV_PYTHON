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
