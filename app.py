import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Cổng Học Tập Toán Học THCS", layout="wide")

# ==========================================
# 1. HIỂN THỊ BANNER
# ==========================================
# THAY LINK BANNER CỦA BẠN VÀO ĐÂY:
link_banner_anh = "https://raw.githubusercontent.com/lbphuoc83lapvo-bit/app.py/main/Back-to-School%20Math%20Educational%20Banner.png"

col1, col_banner, col3 = st.columns([1, 4, 1])
with col_banner:
    st.image(link_banner_anh, use_column_width=True)
st.markdown("---")

# ==========================================
# 2. ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS MỚI
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Đọc đích danh tab mới tạo
    # Tự động đọc tab đầu tiên
    user_df = conn.read(ttl=0) 
    
    # Lọc bỏ dòng trống
    user_df = user_df.dropna(subset=[user_df.columns[1], user_df.columns[2], user_df.columns[3]], how='all')
    
    if len(user_df.columns) >= 4:
        # Cột B(1): Email | Cột C(2): Tên đăng nhập | Cột D(3): Mật khẩu
        email_hs = user_df.iloc[:, 1].astype(str).str.strip()
        ten_dang_nhap = user_df.iloc[:, 2].astype(str).str.strip()
        mat_khau = user_df.iloc[:, 3].astype(str).str.strip()
        
        user_db = dict(zip(ten_dang_nhap, mat_khau))
        email_db = dict(zip(email_hs, mat_khau))
    else:
        user_db, email_db = {}, {}
except Exception as e:
    st.error(f"⚠️ Lỗi kết nối dữ liệu: {e}")
    user_db, email_db = {}, {}

# Khởi tạo trạng thái
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ==========================================
# 3. GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
if not st.session_state.is_logged_in:
    st.title("📐 CỔNG HỌC TẬP TOÁN HỌC TRỰC TUYẾN")
    tab_login, tab_register, tab_quen_mk = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký tài khoản", "🔑 Quên mật khẩu"])
    
    # --- ĐĂNG NHẬP ---
    with tab_login:
        st.write("Vui lòng đăng nhập để vào hệ thống bài học.")
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            btn_login = st.form_submit_button("Đăng nhập")
            
            if btn_login:
                _user = username.strip()
                _pass = password.strip()
                
                if _user == "":
                    st.warning("Vui lòng nhập tên đăng nhập!")
                elif _user not in user_db:
                    st.error(f"❌ Tài khoản '{_user}' chưa xuất hiện trong hệ thống! (Hãy thử bấm Clear Cache trên trình duyệt)")
                elif str(user_db[_user]) != _pass:
                    st.error("❌ Mật khẩu không khớp!")
                else:
                    st.session_state.is_logged_in = True
                    st.session_state.current_user = _user
                    st.success(f"Đăng nhập thành công! Xin chào {_user}.")
                    st.rerun()
                    
    # --- ĐĂNG KÝ ---
    with tab_register:
        st.write("Vui lòng điền thông tin vào biểu mẫu dưới đây để tạo tài khoản mới.")
        # THAY LINK GOOGLE FORM MỚI CỦA BẠN VÀO ĐÂY:
        link_form = "DÁN_LINK_FORM_MỚI_VÀO_ĐÂY"
        components.iframe(link_form, height=700, scrolling=True)
        st.info("💡 Lưu ý: Sau khi điền Form và bấm Gửi, hãy chuyển sang tab 'Đăng nhập' để vào học nhé!")
        
    # --- QUÊN MẬT KHẨU ---
    with tab_quen_mk:
        st.subheader("Khôi phục mật khẩu")
        st.write("Em hãy nhập email đã dùng để đăng ký tài khoản.")
        email_khoi_phuc = st.text_input("📧 Nhập Email của em:")
        
        if st.button("Gửi mật khẩu"):
            if email_khoi_phuc:
                email_can_tim = email_khoi_phuc.strip()
                if email_can_tim in email_db:
                    try:
                        sender_email = st.secrets["email_nguoi_gui"]
                        sender_password = st.secrets["mat_khau_email"]
                        
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = email_khoi_phuc
                        msg['Subject'] = "Khôi phục mật khẩu - Cổng học tập Toán"
                        
                        body = f"Chào em,\n\nHệ thống nhận được yêu cầu khôi phục mật khẩu của em.\n🔑 Mật khẩu của em là: {email_db[email_can_tim]}\n\nChúc em học tốt nhé!"
                        msg.attach(MIMEText(body, 'plain'))
                        
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                        server.quit()
                        
                        st.success("✅ Gửi thành công! Em hãy kiểm tra hộp thư đến (hoặc Thư rác/Spam) nhé.")
                    except Exception as e:
                        st.error(f"❌ Có lỗi xảy ra trong quá trình gửi mail: {e}")
                else:
                    st.error("⚠️ Email này chưa được đăng ký trong hệ thống!")
            else:
                st.warning("Em chưa nhập địa chỉ email.")

# ==========================================
# 4. GIAO DIỆN HỌC TẬP CHÍNH
# ==========================================
else:
    st.sidebar.title("🗂️ DANH MỤC MÔN HỌC")
    
    grade_selection = st.sidebar.radio("Chọn khối lớp của bạn:", ["Toán 6", "Toán 7 (Chân trời sáng tạo)", "Toán 8", "Toán 9 (Chân trời sáng tạo)"])
    st.sidebar.markdown("---")
    
    chapter_selection = None
    if grade_selection == "Toán 6":
        st.sidebar.subheader("📖 Mục lục Toán 6")
        chapters_6 = [
            "Chương 1: TẬP HỢP CÁC SỐ TỰ NHIÊN",
            "Chương 2: TÍNH CHIA HẾT TRONG TẬP HỢP SỐ TỰ NHIÊN",
        ]
        chapter_selection = st.sidebar.selectbox("Chọn chương học:", chapters_6)
        
    elif grade_selection == "Toán 7 (Chân trời sáng tạo)":
        st.sidebar.subheader("📖 Mục lục Toán 7")
        chapters_7 = [
            "Chương 1: SỐ HỮU TỈ",
            "Chương 2: SỐ THỰC",
        ]
        chapter_selection = st.sidebar.selectbox("Chọn chương học:", chapters_7)

    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Tài khoản: **{st.session_state.current_user}**")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    st.title(f"📚 Hệ Thống Bài Học - {grade_selection}")
    
    # ---------------- NỘI DUNG TOÁN 6 ----------------
    if grade_selection == "Toán 6" and chapter_selection:
        if chapter_selection == "Chương 1: TẬP HỢP CÁC SỐ TỰ NHIÊN":
            st.header("CHƯƠNG 1: TẬP HỢP CÁC SỐ TỰ NHIÊN")
            danh_sach_bai = ["Bài 1. Tập hợp", "Bài 2. Cách ghi số tự nhiên"]
            bai_hoc_selection = st.selectbox("📌 Chọn bài học:", danh_sach_bai)
            st.markdown("---") 
            
            if bai_hoc_selection == "Bài 1. Tập hợp":
                tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                
                with tab_ly_thuyet:
                    st.markdown("**🎥 Video bài giảng trực tuyến**")
                    st.video("https://youtu.be/beV0JRiJLvQ")
                    st.markdown("---")
                    
                    st.subheader("1. Tập hợp và phần tử của tập hợp")
                    st.write(r"Xét tập hợp $M$ gồm các số: 4; 1; 9; 8. Ta ký hiệu các mối quan hệ như sau:")
                    st.write(r"- $4 \in M$ (đọc là: 4 thuộc $M$).")
                    st.write(r"- $7 \notin M$ (đọc là: 7 không thuộc $M$).")
                    
                    st.markdown("---")
                    st.subheader("2. Cách mô tả một tập hợp")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.markdown("**Cách 1: Liệt kê các phần tử**")
                        st.latex(r"P = \{0; 1; 2; 3; 4; 5\}")
                    with col_c2:
                        st.markdown("**Cách 2: Nêu dấu hiệu đặc trưng**")
                        st.latex(r"P = \{n \mid n \text{ là số tự nhiên nhỏ hơn } 6\}")
                        
                    st.markdown("---")
                    st.subheader(r"3. Tập hợp các số tự nhiên $\mathbb{N}$ và $\mathbb{N}^*$")
                    st.write(r"- Kí hiệu $\mathbb{N}$ là tập hợp gồm tất cả các số tự nhiên: $\mathbb{N} = \{0; 1; 2; 3; \dots\}$")
                    st.write(r"- Kí hiệu $\mathbb{N}^*$ là tập hợp các số tự nhiên **khác 0**: $\mathbb{N}^* = \{1; 2; 3; \dots\}$")

                with tab_bai_tap:
                    st.subheader("✍️ Đánh giá năng lực - Bài 1")
                    st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA:** Em cần trả lời đúng ít nhất **7/10 câu** để hệ thống mở khóa Bài 2 nhé!")
                    
                    with st.form("quiz_bai_1"):
                        st.markdown(r"**Câu 1:** Cho tập hợp $A = \{2; 4; 6; 8\}$. Khẳng định nào sau đây là **đúng**?")
                        q1 = st.radio("Đáp án Câu 1:", ["-- Chọn --", r"$2 \notin A$", r"$4 \in A$", r"$5 \in A$", r"$8 \notin A$"], key="q_1")
                        
                        st.markdown(r"**Câu 2:** Tập hợp các số tự nhiên **khác 0** được kí hiệu là gì?")
                        q2 = st.radio("Đáp án Câu 2:", ["-- Chọn --", r"$\mathbb{N}$", r"$\mathbb{N}^*$", r"$\mathbb{Z}$", r"$\mathbb{N}^* = \{0; 1; 2; \dots\}$"], key="q_2")
                        
                        submit_button = st.form_submit_button("Lưu & Nộp bài")
                    
                    if submit_button:
                        diem = 0
                        if q1 == r"$4 \in A$": diem += 1
                        if q2 == r"$\mathbb{N}^*$": diem += 1
                        
                        if diem >= 2: # Điểm ví dụ
                            st.success(f"🎉 TUYỆT VỜI! Em đạt điểm tối đa. Bài học số 2 đã được mở khóa!")
                            st.balloons()
                            st.session_state.hoan_thanh_bai_1 = True
                        else:
                            st.error(f"⚠️ Em chưa đủ điểm. Hãy ôn lại lý thuyết và làm lại nhé!")
                            st.session_state.hoan_thanh_bai_1 = False

                with tab_mo_rong:
                    st.subheader("👨‍🔬 Kiến thức mở rộng")
                    st.write(r"Giao của hai tập hợp $A$ và $B$ được kí hiệu là $C = A \cap B$.")
                    
            elif bai_hoc_selection == "Bài 2. Cách ghi số tự nhiên":
                if st.session_state.get("hoan_thanh_bai_1", False) == True:
                    st.header("BÀI 2: CÁCH GHI SỐ TỰ NHIÊN")
                    st.success("🔓 Chào mừng em đến với Bài 2!")
                else:
                    st.warning("🔒 **BÀI HỌC BỊ KHÓA**")
                    st.info("Em cần hoàn thành Bài 1 để mở khóa nhé!")

    # ---------------- NỘI DUNG TOÁN 7, 8, 9 ----------------
    else:
        st.info("Nội dung bài học đang được thầy cô tiếp tục biên soạn và cập nhật. Các em hãy đón chờ nhé!")
