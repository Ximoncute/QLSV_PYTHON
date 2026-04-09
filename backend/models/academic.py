from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from backend1.db.session import Base

class Khoa(Base):
    __tablename__ = "khoa"
    ma_khoa = Column(String(5), primary_key=True)
    ten_khoa = Column(String(100), unique=True, nullable=False)
    
    nganhs = relationship("Nganh", back_populates="khoa")

class Nganh(Base):
    __tablename__ = "nganh"
    ma_nganh = Column(String(10), primary_key=True)
    ten_nganh = Column(String(100), nullable=False)
    ma_khoa = Column(String(5), ForeignKey("khoa.ma_khoa"))
    
    khoa = relationship("Khoa", back_populates="nganhs")
    lops = relationship("Lop", back_populates="nganh")
    pt_xet_tuyens = relationship("PT_XetTuyen", back_populates="nganh")

class Lop(Base):
    __tablename__ = "lop"
    ma_lop = Column(String(15), primary_key=True)
    ten_lop = Column(String(100), unique=True, nullable=False)
    ma_nganh = Column(String(10), ForeignKey("nganh.ma_nganh"))
    
    nganh = relationship("Nganh", back_populates="lops")
    sinh_viens = relationship("SinhVien", back_populates="lop")

class MonHoc(Base):
    __tablename__ = "mon_hoc"
    ma_mh = Column(String(10), primary_key=True)
    ten_mh = Column(String(100), nullable=False)
    so_tin_chi = Column(Integer, nullable=False)
    
    __table_args__ = (
        CheckConstraint("so_tin_chi > 0", name="check_sotinchi_positive"),
    )
    
    kq_hoc_taps = relationship("KQ_HocTap", back_populates="mon_hoc")
