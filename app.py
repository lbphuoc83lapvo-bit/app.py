import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Cổng Học Tập Toán Học THCS", layout="wide")

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
        link_form = "https://docs.google.com/forms/d/e/1FAIpQLScwFF84a5b7-QdhmQrTgpUczUfbgkczoa7rjeIj7v8pVe9cKw/viewform?usp=preview"
        
        components.iframe(link_form, height=700, scrolling=True)
        st.info("💡 Lưu ý: Sau khi điền Form và bấm Gửi, hãy chuyển sang tab 'Đăng nhập' để vào học nhé!")

# ==========================================
# GIAO DIỆN CHÍNH
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
    st.write("Chúc mừng bạn đã đăng nhập thành công vào hệ thống học tập!")
