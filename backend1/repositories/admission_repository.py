from backend1.repositories.base import BaseRepository
from backend1.models.admission import PT_XetTuyen, HSO_XetTuyen

class AdmissionRepository(BaseRepository):
    def get_all_applications(self):
        return self.db.query(PT_XetTuyen).all()

    def get_application(self, ma_ptxt: str):
        return self.db.query(PT_XetTuyen).filter(PT_XetTuyen.MaPTXT == ma_ptxt).first()

    def get_profile(self, ma_hso: str):
        return self.db.query(HSO_XetTuyen).filter(HSO_XetTuyen.MaHSO == ma_hso).first()
