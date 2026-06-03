import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Cổng Học Tập Toán Học THCS", layout="wide")

# ==========================================
# HIỂN THỊ BANNER CHÍNH (THÊM MỚI TẠI ĐÂY)
# ==========================================
# BẠN HÃY DÁN ĐƯỜNG LINK ẢNH BANNER CÔNG KHAI CỦA BẠN VÀO TRONG DẤU NGOẶC KÉP:
# (Ví dụ: "https://raw.githubusercontent.com/user/repo/main/banner.png")
link_banner_anh = "https://raw.githubusercontent.com/lbphuoc83lapvo-bit/app.py/main/Back-to-School%20Math%20Educational%20Banner.png"

# Dùng cột để căn chỉnh Banner ra giữa trang (tùy chỉnh tỷ lệ 1:4:1)
col1, col_banner, col3 = st.columns([1, 4, 1])
with col_banner:
    # Hiển thị ảnh Banner, tự động điều chỉnh độ rộng theo màn hình
    st.image(link_banner_anh, use_column_width=True)

st.markdown("---") # Đường kẻ ngang phân cách
# ==========================================
# ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    user_df = conn.read(ttl=0) 
    
    # Khắc phục lỗi KeyError: Đọc dữ liệu theo thứ tự cột của Google Form
    # Cột số 1 là Tên đăng nhập, Cột số 2 là Mật khẩu (Cột 0 là Dấu thời gian)
    if len(user_df.columns) >= 3:
        user_db = dict(zip(user_df.iloc[:, 1].astype(str), user_df.iloc[:, 2].astype(str)))
    else:
        user_db = {}
except Exception as e:
    user_db = {}

# Khởi tạo trạng thái
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ==========================================
# GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
if not st.session_state.is_logged_in:
    st.title("📐 CỔNG HỌC TẬP TOÁN HỌC TRỰC TUYẾN")
    
    tab_login, tab_register = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký tài khoản"])
    
    with tab_login:
        st.write("Vui lòng đăng nhập để vào hệ thống bài học.")
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            btn_login = st.form_submit_button("Đăng nhập")
            
            if btn_login:
                if username in user_db and user_db[username] == password:
                    st.session_state.is_logged_in = True
                    st.session_state.current_user = username
                    st.success(f"Đăng nhập thành công! Xin chào {username}.")
                    st.rerun()
                else:
                    st.error("Sai thông tin! Nếu bạn vừa đăng ký, vui lòng đợi 5 giây để hệ thống đồng bộ rồi bấm Đăng nhập lại.")
                    
    with tab_register:
        st.write("Vui lòng điền thông tin vào biểu mẫu dưới đây để tạo tài khoản mới.")
        
        # BẠN HÃY DÁN LINK GOOGLE FORM (TỪ BIỂU TƯỢNG CON MẮT) VÀO TRONG DẤU NGOẶC KÉP DƯỚI ĐÂY:
        link_form = "https://docs.google.com/forms/d/e/1FAIpQLSeliSANMx280l6avDFe_NIrpXd2GUWC6ABE39su37JCZqYYRQ/viewform?usp=publish-editor"
        
        components.iframe(link_form, height=700, scrolling=True)
        st.info("💡 Lưu ý: Sau khi điền Form và bấm Gửi, hãy chuyển sang tab 'Đăng nhập' để vào học nhé!")

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
else:
    st.sidebar.title("🗂️ DANH MỤC MÔN HỌC")
    
    # 1. Chọn khối lớp
    grade_selection = st.sidebar.radio("Chọn khối lớp của bạn:", ["Toán 6", "Toán 7", "Toán 8", "Toán 9"])
    st.sidebar.markdown("---")
    
    # 2. Tạo cây thư mục (Menu con) dựa trên khối lớp
    chapter_selection = None
    if grade_selection == "Toán 6":
        st.sidebar.subheader("📖 Mục lục Toán 6")
        chapters_6 = [
            "Chương 1: TẬP HỢP CÁC SỐ TỰ NHIÊN",
            "Chương 2: TÍNH CHIA HẾT TRONG TẬP HỢP SỐ TỰ NHIÊN",
            "Chương 3: SỐ NGUYÊN",
            "Chương 4: MỘT SỐ HÌNH PHẲNG TRONG THỰC TIỄN",
            "Chương 5: TÍNH ĐỐI XỨNG CỦA HÌNH PHẲNG TRONG THỰC TIỄN",
            "Chương 6: PHÂN SỐ",
            "Chương 7: SỐ THẬP PHÂN",
            "Chương 8: NHỮNG HÌNH HÌNH HỌC CƠ BẢN",
            "Chương 9: DỮ LIỆU VÀ XÁC SUẤT THỰC NGHIỆM"
        ]
        chapter_selection = st.sidebar.selectbox("Chọn chương học:", chapters_6)

    # (Các khối lớp 7, 8, 9 sẽ được bổ sung mục lục sau)
    
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Tài khoản: **{st.session_state.current_user}**")
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    # 3. Hiển thị nội dung tương ứng với bài học được chọn
    st.title(f"📚 Hệ Thống Bài Học - {grade_selection}")
    
    if grade_selection == "Toán 6" and chapter_selection:
        if chapter_selection == "Chương 1: TẬP HỢP CÁC SỐ TỰ NHIÊN":
            st.header("CHƯƠNG 1: TẬP HỢP CÁC SỐ TỰ NHIÊN")
            
            # Danh sách các bài học dựa trên mục lục SGK
            danh_sach_bai = [
                "Bài 1. Tập hợp",
                "Bài 2. Cách ghi số tự nhiên",
                "Bài 3. Thứ tự trong tập hợp các số tự nhiên",
                "Bài 4. Phép cộng và phép trừ số tự nhiên",
                "Bài 5. Phép nhân và phép chia số tự nhiên",
                "Luyện tập chung (trang 20)",
                "Bài 6. Luỹ thừa với số mũ tự nhiên",
                "Bài 7. Thứ tự thực hiện các phép tính",
                "Luyện tập chung (trang 27)",
                "Bài tập cuối chương I"
            ]
            
            # Tạo hộp thoại chọn bài học
            bai_hoc_selection = st.selectbox("📌 Chọn bài học:", danh_sach_bai)
            st.markdown("---") # Đường kẻ ngang phân cách
            
            # Cấu trúc nội dung cho từng bài
            if bai_hoc_selection == "Bài 1. Tập hợp":
                tab_ly_thuyet, tab_bai_tap = st.tabs(["📚 Lý thuyết", "✍️ Bài tập trắc nghiệm"])
                
                with tab_ly_thuyet:
                    st.subheader("Tập hợp")
                    st.markdown("**1. Ký hiệu và cách viết:**")
                    st.write("Người ta thường đặt tên tập hợp bằng chữ cái in hoa: $A, B, C, X, Y...$")
                    st.write("Ví dụ: Gọi $A$ là tập hợp các số tự nhiên nhỏ hơn 5. Ta có thể viết:")
                    st.latex(r"A = \{0; 1; 2; 3; 4\}")
                    st.write("Các số $0, 1, 2, 3, 4$ được gọi là các **phần tử** của tập hợp $A$.")
                    
                    st.markdown("**2. Quan hệ thuộc và không thuộc:**")
                    st.write("- Ký hiệu $\in$ (thuộc): $3 \in A$ (Đọc là: 3 thuộc tập hợp A)")
                    st.write("- Ký hiệu $\notin$ (không thuộc): $7 \notin A$ (Đọc là: 7 không thuộc tập hợp A)")
                    
                    st.markdown("**3. Hai cách cho một tập hợp:**")
                    st.write("- **Cách 1:** Liệt kê các phần tử của tập hợp.")
                    st.write("- **Cách 2:** Chỉ ra tính chất đặc trưng cho các phần tử của tập hợp đó.")
                    st.latex(r"A = \{x \in \mathbb{N} \mid x < 5\}")
                    
                with tab_bai_tap:
                    st.subheader("Kiểm tra kiến thức nhanh")
                    st.info("Khu vực này sẽ chứa các câu hỏi trắc nghiệm tự động chấm điểm để học sinh luyện tập ngay sau khi học lý thuyết.")
            
            else:
                st.info(f"Giao diện chuẩn bị nội dung cho **{bai_hoc_selection}** đã sẵn sàng. Các em học sinh hãy đón chờ nhé!")
                
        else:
            st.subheader(chapter_selection)
            st.write("Nội dung chương này đang được biên soạn và sẽ sớm cập nhật. Các em đón chờ nhé!")
