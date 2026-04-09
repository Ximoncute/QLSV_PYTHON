# Modern UniMS - University Management System

Hệ thống quản lý sinh viên hiện đại với Backend FastAPI và Frontend Tkinter (Modular Design). Được tối ưu hóa cho hệ điều hành Windows.

## 🚀 Tính năng chính
- **Dashboard quản trị**: Thống kê thời gian thực, biểu đồ phân bổ sinh viên, và quản lý tình trạng hệ thống.
- **Quản lý học thuật**: Khoa, Ngành, Lớp, và hồ sơ Sinh viên.
- **Cổng tuyển sinh**: Tiếp nhận và duyệt hồ sơ thí sinh, tự động xếp lớp và cấp MSSV.
- **Cổng sinh viên**: Xem điểm số (thanh điểm 10/4), bảng điểm, học phí và thông báo.
- **Bảo mật**: Xác thực OAuth2 với mã hóa mật khẩu Bcrypt.

## 🛠 Yêu cầu hệ thống (Windows)
- **Python**: Phiên bản 3.10 trở lên.
- **Thư viện**: Danh sách các thư viện cần thiết có trong `requirements.txt`.

## 📦 Cài đặt
1. Mở Terminal (PowerShell hoặc CMD) tại thư mục dự án.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Cách chạy ứng dụng
Chỉ cần nhấp đúp vào file:
- `run_app.bat`

File này sẽ tự động:
1. Đồng bộ hóa Database (SQLite).
2. Khởi chạy Backend API (Cổng 8000).
3. Khởi chạy Giao diện (Tkinter).

## 🔑 Tài khoản thử nghiệm
| Vai trò | Tên đăng nhập | Mật khẩu |
| :--- | :--- | :--- |
| **Quản trị viên** | `admin1` | `admin123` |
| **Sinh viên** | `SV001` | `123456` |

## 📂 Cấu trúc dự án
- `backend1/`: Chứa API FastAPI, Models, Routers và Business Logic.
- `frontend/`: Chứa giao diện Tkinter được chia theo module (Views, Core, Styles).
- `university.db`: File cơ sở dữ liệu SQLite của ứng dụng.

---
*Phát triển bởi Đội ngũ UniMS (Modern Edition)*
