import streamlit as st

# Cấu hình trang web
st.set_page_config(page_title="Cổng Học Tập Toán Học THCS", layout="wide")

# ==========================================
# 1. KHỞI TẠO BỘ NHỚ TẠM (SESSION STATE)
# ==========================================
# Khởi tạo danh sách tài khoản mẫu (Tên đăng nhập: hocsinh, Mật khẩu: 123)
if 'user_db' not in st.session_state:
    st.session_state.user_db = {"hocsinh": "123"}

# Khởi tạo trạng thái đăng nhập
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# Khởi tạo tiến độ học tập cho tài khoản hiện tại
if 'passed_lessons' not in st.session_state:
    st.session_state.passed_lessons = set()

# ==========================================
# 2. GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
if not st.session_state.is_logged_in:
    st.title("📐 CỔNG HỌC TẬP TOÁN HỌC TRỰC TUYẾN")
    st.write("Vui lòng đăng nhập để vào hệ thống bài học.")
    
    # Tạo 2 tab: Đăng nhập và Đăng ký
    tab_login, tab_register = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký tài khoản"])
    
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            btn_login = st.form_submit_button("Đăng nhập")
            
            if btn_login:
                if username in st.session_state.user_db and st.session_state.user_db[username] == password:
                    st.session_state.is_logged_in = True
                    st.session_state.current_user = username
                    st.success(f"Đăng nhập thành công! Xin chào {username}.")
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")
                    
    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input("Tạo tên đăng nhập")
            new_password = st.text_input("Tạo mật khẩu", type="password")
            confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
            btn_register = st.form_submit_button("Đăng ký")
            
            if btn_register:
                if not new_username or not new_password:
                    st.warning("Vui lòng điền đầy đủ thông tin.")
                elif new_username in st.session_state.user_db:
                    st.error("Tên đăng nhập này đã tồn tại.")
                elif new_password != confirm_password:
                    st.error("Mật khẩu xác nhận không khớp.")
                else:
                    st.session_state.user_db[new_username] = new_password
                    st.success("Đăng ký thành công! Hãy chuyển sang tab Đăng nhập.")

# ==========================================
# 3. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP)
# ==========================================
else:
    # --- THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR) ---
    st.sidebar.title("🗂️ DANH MỤC MÔN HỌC")
    
    # 4 danh mục khối lớp cho học sinh lựa chọn
    grade_selection = st.sidebar.radio(
        "Chọn khối lớp của bạn:",
        ["Toán 6", "Toán 7", "Toán 8", "Toán 9"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Tài khoản: **{st.session_state.current_user}**")
    
    # Nút đăng xuất
    if st.sidebar.button("Đăng xuất"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    # --- NỘI DUNG HIỂN THỊ THEO KHỐI LỚP ---
    st.title(f"📚 Hệ Thống Bài Học - {grade_selection}")
    st.write(f"Chào mừng bạn đến với không gian học tập của lớp {grade_selection[-1]}.")

    if grade_selection == "Toán 6":
        st.header("Chương 1: Số tự nhiên")
        st.write("Nội dung bài học, video và bài tập trắc nghiệm Toán 6 sẽ được cập nhật tại đây.")
        
    elif grade_selection == "Toán 7":
        st.header("Chương 1: Số hữu tỉ")
        st.write("Nội dung bài học, video và bài tập trắc nghiệm Toán 7 sẽ được cập nhật tại đây.")
        
    elif grade_selection == "Toán 8":
        st.header("Chương 1: Đa thức")
        
        # Ví dụ mẫu về cấu trúc Mastery Learning (Khóa/Mở bài cũ)
        st.subheader("📖 Bài 1: Đơn thức và đa thức nhiều biến")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        st.markdown("""
        Biểu thức toán học hiển thị chuẩn mã LaTeX:
        $$A = 2x^2y + 3xy^2 - 5$$
        """)
        
        with st.form("quiz_t8_b1"):
            q1 = st.radio("Đâu là đơn thức?", ["A) $2x + y$", "B) $3x^2y$", "C) $\frac{x}{y}$"])
            submit_q = st.form_submit_button("Nộp bài")
            
            if submit_q:
                if "B)" in q1:
                    st.session_state.passed_lessons.add("t8_b1")
                    st.success("🎉 Xuất sắc! Bạn được 10/10 điểm. Bài tiếp theo đã được mở khóa.")
                else:
                    st.error("❌ Kết quả chưa đạt 5 điểm. Vui lòng ôn lại lý thuyết và làm lại.")
                    
        st.markdown("---")
        st.subheader("🔒 Bài 2: Các phép tính với đa thức")
        if "t8_b1" in st.session_state.passed_lessons:
            st.info("🔓 Bài học đã mở khóa!")
            st.write("Nội dung chi tiết của Bài 2...")
        else:
            st.warning("Bài học này đang khóa. Bạn cần vượt qua bài tập trắc nghiệm Bài 1 với số điểm $\ge 5$ để mở khóa.")

    elif grade_selection == "Toán 9":
        st.header("Chương 1: Phương trình và hệ phương trình bậc nhất")
        st.write("Nội dung bài học, video và bài tập trắc nghiệm Toán 9 sẽ được cập nhật tại đây.")
