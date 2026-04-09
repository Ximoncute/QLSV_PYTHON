import os
import sys
from datetime import date

# Add root to sys.path at the very beginning
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend1.db.session import engine, Base, SessionLocal
from backend1.models.administrative import QuanTri, ThongBao
from backend1.models.academic import Khoa, Nganh, Lop, MonHoc
from backend1.models.student import SinhVien, KQ_HocTap, TotNghiep, HocPhi, HocPhiChiTiet
from backend1.models.admission import TK_XetTuyen, HSO_XetTuyen, PT_XetTuyen
from backend1.core.security import get_password_hash

def ensure_record(db, model, filter_dict, create_obj):
    """Additive seeding helper: find or create"""
    exists = db.query(model).filter_by(**filter_dict).first()
    if not exists:
        db.add(create_obj)
        db.commit()
        return True
    return False

def init_db():
    print("Database Synchronization...")
    # 1. CREATE ALL (Only creates if not exists)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check current student count
        student_count = db.query(SinhVien).count()
        if student_count >= 40:
            print(f"[OK] Database already has {student_count} students. Skipping seeding.")
            return

        print(f"Ensuring full academic sync (Current: {student_count}, Target: 40)...")
        # 1. Departments & Majors
        khoa_objs = [
            ("CNTT", "Công nghệ thông tin"),
            ("KTH", "Kinh tế - Quản trị"),
            ("NN", "Ngoại ngữ")
        ]
        for mid, name in khoa_objs:
            if not db.query(Khoa).filter_by(ma_khoa=mid).first():
                db.add(Khoa(ma_khoa=mid, ten_khoa=name))
        db.commit()

        nganh_objs = [
            ("CNPM", "Kỹ thuật phần mềm", "CNTT"),
            ("AI", "Trí tuệ nhân tạo", "CNTT"),
            ("KETO", "Kế toán công đức", "KTH"),
            ("QTKD", "Quản trị kinh doanh", "KTH"),
            ("NNA", "Ngôn ngữ Anh", "NN")
        ]
        for mid, name, kid in nganh_objs:
            if not db.query(Nganh).filter_by(ma_nganh=mid).first():
                db.add(Nganh(ma_nganh=mid, ten_nganh=name, ma_khoa=kid))
        db.commit()

        lop_objs = [
            ("D21CN01", "Lớp K21 CNTT 1", "CNPM"),
            ("D21AI01", "Lớp K21 AI", "AI"),
            ("D21KT01", "Lớp K21 Kế toán", "KETO")
        ]
        for mid, name, nid in lop_objs:
            if not db.query(Lop).filter_by(ma_lop=mid).first():
                db.add(Lop(ma_lop=mid, ten_lop=name, ma_nganh=nid))
        db.commit()

        # 2. Comprehensive Course Catalog (40+ Courses)
        course_data = [
            # CNTT - CNPM
            ("CS101", "Cấu trúc dữ liệu", 3), ("CS102", "Lập trình OOP", 4), ("CS103", "Cơ sở dữ liệu", 3),
            ("CS104", "Kiến trúc máy tính", 3), ("CS105", "Hệ điều hành", 3), ("CS106", "Mạng máy tính", 3),
            ("CS201", "Phân tích thiết kế HT", 3), ("CS202", "Kiểm thử phần mềm", 3), ("CS203", "Lập trình Web", 4),
            ("CS204", "Lập trình Di động", 4), ("CS301", "Quản lý dự án PM", 3), ("CS302", "Công nghệ Cloud", 3),
            # CNTT - AI
            ("AI101", "Cơ sở AI", 4), ("AI102", "Học máy cơ bản", 4), ("AI103", "Xử lý ảnh", 3),
            ("AI104", "Xử lý ngôn ngữ tự nhiên", 3), ("AI201", "Hệ chuyên gia", 3), ("AI202", "Thị giác máy tính", 3),
            ("AI301", "Big Data", 4), ("AI302", "Deep Learning", 4),
            # KTH - KETO
            ("KT101", "Nguyên lý kế toán", 3), ("KT102", "Kế toán tài chính 1", 4), ("KT103", "Kế toán tài chính 2", 4),
            ("KT201", "Kế toán quản trị", 3), ("KT202", "Thuế", 3), ("KT203", "Kiểm toán cơ bản", 3),
            ("KT301", "Phân tích tài chính", 3), ("KT302", "Kế toán quốc tế", 3),
            # General / Foundation
            ("MAT101", "Giải tích 1", 3), ("MAT102", "Giải tích 2", 3), ("MAT103", "Đại số tuyến tính", 3),
            ("PHY101", "Vật lý A1", 3), ("ENG101", "Tiếng Anh 1", 2), ("ENG102", "Tiếng Anh 2", 2),
            ("ENG201", "Tiếng Anh chuyên ngành", 3), ("POL101", "Triết học M-L", 3), ("POL102", "Kinh tế chính trị", 2),
            ("POL103", "Chủ nghĩa xã hội", 2), ("POL104", "Tư tưởng Hồ Chí Minh", 2), ("POL105", "Đường lối cách mạng", 3)
        ]
        
        for mid, name, creds in course_data:
            if not db.query(MonHoc).filter_by(ma_mh=mid).first():
                db.add(MonHoc(ma_mh=mid, ten_mh=name, so_tin_chi=creds))
        db.commit()

        # 3. Bulk Students (40+)
        last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ"]
        first_names = ["Văn A", "Thị B", "Hồng C", "Minh D", "Tuấn E", "Hoàng F", "Quốc G", "Mai H", "Lan I", "Dương K",
                       "Bảo L", "Chí M", "Dũng N", "Gia O", "Hải P", "Khánh Q", "Lâm R", "Nam S", "Phát T", "Quang U",
                       "Sơn V", "Trung X", "Uyên Y", "Việt Z", "An 1", "Bình 2", "Cường 3", "Đức 4", "Giang 5", "Hiếu 6",
                       "Tâm 7", "Đức 8", "Thắng 9", "Hòa 10"]
        
        courses = db.query(MonHoc).all()
        # Total available credits in seed: approx 122 credits
        total_seed_creds = sum(c.so_tin_chi for c in courses)
        print(f"Total credits available in catalog: {total_seed_creds}")

        import random
        for i in range(1, 41):
            sid = f"SV{i:03d}"
            # Skip if exists
            if db.query(SinhVien).filter_by(ma_sv=sid).first():
                continue
                
            name = f"{last_names[i%10]} {first_names[(i-1)%len(first_names)]}"
            major = "D21CN01"
            if 10 < i <= 20: major = "D21AI01"
            elif i > 20: major = "D21KT01"
            
            s = SinhVien(
                ma_sv=sid, ho_ten=name, ngay_sinh=date(2003, 1, 1),
                email=f"sv{i:03d}@university.edu.vn", 
                mat_khau=get_password_hash("123456"),
                ma_lop=major,
                trang_thai="active", ngay_nhap_hoc=date(2022, 9, 1) # Earlier intake to graduate soon
            )
            db.add(s)
            
            # Grades for new student
            for c in courses:
                # SV001 and SV002 pass ALL courses to demonstrate graduation review
                if sid in ["SV001", "SV002"]:
                    score = round(random.uniform(7.5, 9.5), 1)
                else:
                    # Others pass a random subset (approx 60-80% courses)
                    if random.random() < 0.7:
                        score = round(random.uniform(4.0, 8.0), 1)
                    else:
                        continue # Didn't take/finish this course

                db.add(KQ_HocTap(ma_sv=sid, ma_mh=c.ma_mh, diem=score, hoc_ky="HK 2023-2024"))
        
        db.commit()

        # 5. Admin Account
        if not db.query(QuanTri).filter_by(ma_qt="AD01").first():
            admin = QuanTri(
                ma_qt="AD01", ho_ten="Quản trị viên Hệ thống", 
                email="admin1", mat_khau=get_password_hash("admin123")
            )
            db.add(admin)
        
        # 6. Admissions (Candidates) - Comprehensive Seed (10+ Records)
        cands_data = [
            ("CAND_001", "candidate@gmail.com", "Lê Văn Candidate", "123000001", "0911000001", "AI", "Xét học bạ", "28.5", "Đã duyệt"),
            ("CAND_002", "nguyen_na@gmail.com", "Nguyễn Thị Na", "123000002", "0911000002", "CNPM", "Xét điểm thi THPT", "26.0", "Chờ duyệt"),
            ("CAND_003", "tran_duy@gmail.com", "Trần Quang Duy", "123000003", "0911000003", "KETO", "Xét tuyển thẳng", "30.0", "Đã duyệt"),
            ("CAND_004", "mai_hoa@gmail.com", "Lâm Mai Hoa", "123000004", "0911000004", "QTKD", "Xét học bạ", "24.5", "Cần bổ sung"),
            ("CAND_005", "hoang_an@gmail.com", "Hoàng Gia An", "123000005", "0911000005", "NNA", "Xét điểm IELTS", "7.5", "Chờ duyệt"),
            ("CAND_006", "vu_long@gmail.com", "Vũ Phi Long", "123000006", "0911000006", "AI", "Xét điểm thi THPT", "27.2", "Đã duyệt"),
            ("CAND_007", "pham_lan@gmail.com", "Phạm Ngọc Lan", "123000007", "0911000007", "CNPM", "Xét học bạ", "25.8", "Chờ duyệt"),
            ("CAND_008", "do_son@gmail.com", "Đỗ Thái Sơn", "123000008", "0911000008", "KETO", "Xét điểm thi THPT", "23.5", "Cần bổ sung"),
            ("CAND_009", "bui_minh@gmail.com", "Bùi Bình Minh", "123000009", "0911000009", "QTKD", "Xét điểm thi THPT", "25.5", "Chờ duyệt"),
            ("CAND_010", "ha_anh@gmail.com", "Ngô Hà Anh", "123000010", "0911000010", "NNA", "Xét học bạ", "29.0", "Đã duyệt"),
        ]
        
        for tid, email, name, cccd, sdt, nganh, ptxt, diem, status in cands_data:
            if not db.query(TK_XetTuyen).filter_by(ma_tk=tid).first():
                # Account
                db.add(TK_XetTuyen(ma_tk=tid, email=email, mat_khau=get_password_hash("candidate123")))
                # Profile
                hsid = "HS_" + tid[5:]
                db.add(HSO_XetTuyen(ma_hso=hsid, ma_tk=tid, ho_ten=name, cccd=cccd, sdt=sdt))
                # Method
                ptid = "PT_" + tid[5:]
                db.add(PT_XetTuyen(ma_ptxt=ptid, ma_hso=hsid, ma_nganh=nganh, phuong_thuc=ptxt, diem=diem, trang_thai=status))

        db.commit()
        print(f"[OK] Database sync complete. Total students: {db.query(SinhVien).count()}, Total Candidates: {db.query(TK_XetTuyen).count()}")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
