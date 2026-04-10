from pydantic import BaseModel
from typing import List, Optional

class GradeInput(BaseModel):
    ma_sv: str
    ma_mh: str
    hoc_ky: str
    diem: float

class ApproveResponse(BaseModel):
    ma_sv: str
    email: str
    ho_ten: str

class KhoaCreate(BaseModel):
    ma_khoa: str
    ten_khoa: str

class KhoaRead(KhoaCreate):
    model_config = {"from_attributes": True}

class NganhCreate(BaseModel):
    ma_nganh: str
    ten_nganh: str
    ma_khoa: Optional[str] = None

class NganhRead(NganhCreate):
    model_config = {"from_attributes": True}

class LopCreate(BaseModel):
    ma_lop: str
    ten_lop: str
    ma_nganh: Optional[str] = None

class LopRead(LopCreate):
    model_config = {"from_attributes": True}

class EnrollRequest(BaseModel):
    ma_hso: str
    ma_lop: Optional[str] = None

class MonHocCreate(BaseModel):
    ma_mh: str
    ten_mh: str
    so_tin_chi: int

class MonHocRead(MonHocCreate):
    model_config = {"from_attributes": True}
