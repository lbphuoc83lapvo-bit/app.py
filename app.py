import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Cấu hình trang web
st.set_page_config(page_title="Cổng Học Tập Toán Học THCS", layout="wide")

# ==========================================
# KHỞI TẠO KẾT NỐI GOOGLE SHEETS
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Đọc dữ liệu tài khoản từ Google Sheets
    user_df = conn.read(ttl=0) # ttl=0 để luôn cập nhật dữ liệu mới nhất
except Exception as e:
    st.error("Chưa cấu hình kết nối Google Sheets. Vui lòng hoàn thành Bước 4.")
    user_df = pd.DataFrame(columns=["username", "password"])

# Chuyển đổi bảng dữ liệu thành từ điển để dễ kiểm tra đăng nhập
user_db = dict(zip(user_df['username'].astype(str), user_df['password'].astype(str)))

# Khởi tạo trạng thái đăng nhập trong phiên làm việc
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'passed_lessons' not in st.session_state:
    st.session_state.passed_lessons = set()

# ==========================================
# GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
if not st.session_state.is_logged_in:
    st.title("📐 CỔNG HỌC TẬP TOÁN HỌC TRỰC TUYẾN")
    st.write("Vui lòng đăng nhập để vào hệ thống bài học.")
    
    tab_login, tab_register = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký tài khoản"])
    
    with tab_login:
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
                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")
                    
    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input("Tạo tên đăng nhập")
            new_password = st.text_input("Tạo mật khẩu", type="password")
            confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
            btn_register = st.form_submit_button("Đăng ký hoàn tất")
            
            if btn_register:
                if not new_username or not new_password:
                    st.warning("Vui lòng điền đầy đủ thông tin.")
                elif new_username in user_db:
                    st.error("Tên đăng nhập này đã tồn tại trên hệ thống.")
                elif new_password != confirm_password:
                    st.error("Mật khẩu xác nhận không khớp.")
                else:
                    # Tạo dòng dữ liệu mới và thêm vào file Google Sheets
                    new_data = pd.DataFrame([{"username": new_username, "password": new_password}])
                    updated_df = pd.concat([user_df, new_data], ignore_index=True)
                    
                    # Ghi đè bảng tính đã cập nhật lên Google Sheets
                    conn.update(data=updated_df)
                    st.success("🎉 Đăng ký thành công! Thông tin của bạn đã được lưu vĩnh viễn. Hãy chuyển sang tab Đăng nhập.")

# ==========================================
# GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP THÀNH CÔNG)
# ==========================================
else:
    st.sidebar.title("🗂️ DANH MỤC MÔN HỌC")
    grade_selection = st.sidebar.radio("Chọn khối lớp của bạn:", ["Toán 6", "Toán 7", "Toán 8", "Toán 9"])
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Tài khoản: **{st.session_state.current_user}**")
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    st.title(f"📚 Hệ Thống Bài Học - {grade_selection}")
    st.write(f"Chào mừng bạn đến với không gian học tập trực tuyến.")
    
    if grade_selection == "Toán 9":
        st.header("Chương 1: Phương trình và hệ phương trình bậc nhất")
        st.subheader("📖 Bài 1: Khái niệm về phương trình bậc nhất hai ẩn")
        st.markdown("Nội dung bài học và công thức toán dạng LaTeX: $ax + by = c$")
