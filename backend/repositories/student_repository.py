from backend1.repositories.base import BaseRepository
from backend1.models.student import SinhVien, KQ_HocTap, TotNghiep
from backend1.models.academic import MonHoc

class StudentRepository(BaseRepository):
    def get_by_id(self, ma_sv: str):
        return self.db.query(SinhVien).filter(SinhVien.ma_sv == ma_sv).first()

    def get_transcript(self, ma_sv: str):
        return self.db.query(KQ_HocTap, MonHoc).join(
            MonHoc, KQ_HocTap.ma_mh == MonHoc.ma_mh
        ).filter(KQ_HocTap.ma_sv == ma_sv).all()

    def update_tot_nghiep(self, ma_sv: str, gpa: float, rank: str):
        tn = self.db.query(TotNghiep).filter(TotNghiep.ma_sv == ma_sv).first()
        if not tn:
            tn = TotNghiep(ma_sv=ma_sv, gpa=gpa, xep_loai=rank)
            self.db.add(tn)
        else:
            tn.gpa = gpa
            tn.xep_loai = rank
        self.db.commit()
