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
link_banner_anh = "https://raw.githubusercontent.com/lbphuoc83lapvo-bit/app.py/main/Back-to-School%20Math%20Educational%20Banner.png"
col1, col_banner, col3 = st.columns([1, 4, 1])
with col_banner:
    st.image(link_banner_anh, use_column_width=True)
st.markdown("---")

# ==========================================
# 2. ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS
# ==========================================
# ==========================================
# 2. ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Tự động đọc Tab ngoài cùng bên trái
    user_df = conn.read(ttl=0) 
    
    if len(user_df.columns) >= 4:
        # TỌA ĐỘ MỚI KHỚP VỚI GOOGLE SHEETS CỦA BẠN:
        # Cột B (1): Email | Cột C (2): Tên đăng nhập | Cột D (3): Mật khẩu
        email_hs = user_df.iloc[:, 1].astype(str).str.strip()
        ten_dang_nhap = user_df.iloc[:, 2].astype(str).str.strip()
        mat_khau = user_df.iloc[:, 3].astype(str).str.strip()
        
        user_db = dict(zip(ten_dang_nhap, mat_khau))
        email_db = dict(zip(email_hs, mat_khau))
        
    elif len(user_df.columns) >= 3:
        # Đề phòng trường hợp đọc nhầm tab biểu mẫu 1 cũ
        ten_dang_nhap = user_df.iloc[:, 1].astype(str).str.strip()
        mat_khau = user_df.iloc[:, 2].astype(str).str.strip()
        
        user_db = dict(zip(ten_dang_nhap, mat_khau))
        email_db = {}
    else:
        user_db, email_db = {}, {}
except Exception as e:
    user_db, email_db = {}, {}
# Khởi tạo trạng thái đăng nhập
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
    
    # --- TAB ĐĂNG NHẬP ---
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
                    st.error(f"❌ Tài khoản '{_user}' chưa xuất hiện trong dữ liệu!")
                elif str(user_db[_user]) != _pass:
                    st.error("❌ Mật khẩu không khớp!")
                else:
                    st.session_state.is_logged_in = True
                    st.session_state.current_user = _user
                    st.success(f"Đăng nhập thành công! Xin chào {_user}.")
                    st.rerun()
                    
    # --- TAB ĐĂNG KÝ ---
    with tab_register:
        st.write("Vui lòng điền thông tin vào biểu mẫu dưới đây để tạo tài khoản mới.")
        link_form = "https://docs.google.com/forms/d/e/1FAIpQLSeliSANMx280l6avDFe_NIrpXd2GUWC6ABE39su37JCZqYYRQ/viewform?usp=publish-editor"
        components.iframe(link_form, height=700, scrolling=True)
        st.info("💡 Lưu ý: Sau khi điền Form và bấm Gửi, hãy chuyển sang tab 'Đăng nhập' để vào học nhé!")
        
    # --- TAB QUÊN MẬT KHẨU ---
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
    
    grade_selection = st.sidebar.radio("Chọn khối lớp của bạn:", ["Toán 6", "Toán 7", "Toán 8", "Toán 9"])
    st.sidebar.markdown("---")
    
    chapter_selection = None
    if grade_selection == "Toán 6":
        st.sidebar.subheader("📖 Mục lục Toán 6")
        chapters_6 = [
            "Chương 1: TẬP HỢP CÁC SỐ TỰ NHIÊN",
            "Chương 2: TÍNH CHIA HẾT TRONG TẬP HỢP SỐ TỰ NHIÊN",
            "Chương 3: SỐ NGUYÊN",
            "Chương 4: MỘT SỐ HÌNH PHẲNG TRONG THỰC TIỄN",
            "Chương 5: TÍNH ĐỐI XỨNG CỦA HÌNH PHẲNG TRONG THỰC TIỄN"
        ]
        chapter_selection = st.sidebar.selectbox("Chọn chương học:", chapters_6)

    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Tài khoản: **{st.session_state.current_user}**")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    st.title(f"📚 Hệ Thống Bài Học - {grade_selection}")
    
    if grade_selection == "Toán 6" and chapter_selection:
        if chapter_selection == "Chương 1: TẬP HỢP CÁC SỐ TỰ NHIÊN":
            st.header("CHƯƠNG 1: TẬP HỢP CÁC SỐ TỰ NHIÊN")
            
            danh_sach_bai = [
                "Bài 1. Tập hợp",
                "Bài 2. Cách ghi số tự nhiên",
                "Bài 3. Thứ tự trong tập hợp các số tự nhiên"
            ]
            
            bai_hoc_selection = st.selectbox("📌 Chọn bài học:", danh_sach_bai)
            st.markdown("---") 
            
            # ---------------- BÀI 1 ----------------
            if bai_hoc_selection == "Bài 1. Tập hợp":
                tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                
                with tab_ly_thuyet:
                    st.markdown("**🎥 Video bài giảng trực tuyến**")
                    st.video("https://youtu.be/beV0JRiJLvQ")
                    st.markdown("---")
                    
                    st.subheader("1. Tập hợp và phần tử của tập hợp")
                    st.write("Một **tập hợp** (gọi tắt là **tập**) bao gồm những đối tượng nhất định. Các đối tượng ấy được gọi là những **phần tử** của tập hợp.")
                    st.write(r"Xét tập hợp $M$ gồm các số: 4; 1; 9; 8. Ta ký hiệu các mối quan hệ như sau:")
                    st.write(r"- $4 \in M$ (đọc là: 4 thuộc M).")
                    st.write(r"- $7 \notin M$ (đọc là: 7 không thuộc M).")
                    
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
                    st.write(r"- Kí hiệu $\mathbb{N}$ là tập hợp gồm tất cả các số tự nhiên: $\mathbb{N} = \{0; 1; 2; 3; ...\}$")
                    st.write(r"- Kí hiệu $\mathbb{N}^*$ là tập hợp các số tự nhiên **khác 0**: $\mathbb{N}^* = \{1; 2; 3; ...\}$")

                with tab_bai_tap:
                    st.subheader("✍️ Đánh giá năng lực - Bài 1")
                    st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA:** Em cần trả lời đúng ít nhất **7/10 câu** để hệ thống mở khóa Bài 2 nhé!")
                    
                    with st.form("quiz_bai_1"):
                        st.markdown("### I. Mức độ Nhận biết")
                        st.markdown(r"**Câu 1:** Cho tập hợp $A = \{2; 4; 6; 8\}$. Khẳng định nào sau đây là **đúng**?")
                        q1 = st.radio("Đáp án Câu 1:", ["-- Chọn --", r"$2 \notin A$", r"$4 \in A$", r"$5 \in A$", r"$8 \notin A$"], key="q_1")
                        
                        st.markdown(r"**Câu 2:** Tập hợp các số tự nhiên **khác 0** được kí hiệu là gì?")
                        q2 = st.radio("Đáp án Câu 2:", ["-- Chọn --", r"$\mathbb{N}$", r"$\mathbb{N}^*$", r"$\mathbb{Z}$", r"$\mathbb{N}^* = \{0; 1; 2; \dots\}$"], key="q_2")
                        
                        st.markdown(r"**Câu 3:** Cho tập hợp $M = \{a; b; c\}$. Số phần tử của tập hợp $M$ là bao nhiêu?")
                        q3 = st.radio("Đáp án Câu 3:", ["-- Chọn --", "1 phần tử", "2 phần tử", "3 phần tử", "4 phần tử"], key="q_3")
                        
                        st.markdown("---")
                        st.markdown("### II. Mức độ Thông hiểu")
                        st.markdown(r"**Câu 4:** Viết tập hợp $P$ các số tự nhiên nhỏ hơn 4 bằng cách liệt kê:")
                        q4 = st.radio("Đáp án Câu 4:", ["-- Chọn --", r"$P = \{1; 2; 3; 4\}$", r"$P = \{0; 1; 2; 3; 4\}$", r"$P = \{0; 1; 2; 3\}$", r"$P = \{1; 2; 3\}$"], key="q_4")
                        
                        st.markdown(r"**Câu 5:** Cho tập hợp $X = \{x \in \mathbb{N} \mid 3 < x \le 6\}$. Tập hợp $X$ được viết dưới dạng liệt kê là:")
                        q5 = st.radio("Đáp án Câu 5:", ["-- Chọn --", r"$X = \{3; 4; 5; 6\}$", r"$X = \{4; 5; 6\}$", r"$X = \{4; 5\}$", r"$X = \{3; 4; 5\}$"], key="q_5")
                        
                        st.markdown(r"**Câu 6:** Cho tập hợp $U = \{x \in \mathbb{N} \mid x \text{ chia hết cho } 2\}$. Số nào dưới đây **KHÔNG** thuộc tập $U$?")
                        q6 = st.radio("Đáp án Câu 6:", ["-- Chọn --", "4", "10", "7", "22"], key="q_6")
                        
                        st.markdown(r"**Câu 7:** Cho tập hợp $E = \{x \in \mathbb{N}^* \mid x < 5\}$. Khẳng định nào sau đây là **SAI**?")
                        q7 = st.radio("Đáp án Câu 7:", ["-- Chọn --", r"$0 \in E$", r"$1 \in E$", r"$4 \in E$", "Tập $E$ có 4 phần tử"], key="q_7")
                        
                        st.markdown("---")
                        st.markdown("### III. Mức độ Vận dụng")
                        st.markdown(r"**Câu 8:** Gọi $T$ là tập hợp các chữ cái xuất hiện trong cụm từ 'AN GIANG'. Cách viết nào sau đây đúng?")
                        q8 = st.radio("Đáp án Câu 8:", ["-- Chọn --", r"$T = \{A; N; G; I; A; N; G\}$", r"$T = \{A; N; G; I\}$", r"$T = \{A; N; G; I; C\}$", r"$T = \{A; N; G\}$"], key="q_8")
                        
                        st.markdown(r"**Câu 9:** Gọi $K$ là tập hợp các tháng (dương lịch) có 30 ngày trong năm. Tập hợp $K$ là:")
                        q9 = st.radio("Đáp án Câu 9:", ["-- Chọn --", r"$K = \{4; 6; 9; 11\}$", r"$K = \{2; 4; 6; 9; 11\}$", r"$K = \{4; 6; 8; 9; 11\}$", r"$K = \{1; 3; 5; 7; 8; 10; 12\}$"], key="q_9")
                        
                        st.markdown(r"**Câu 10:** Một khu vườn có 3 loại cây: xoài, ổi, mít. Gọi $V$ là tập hợp các loại cây trong vườn. Khẳng định nào ĐÚNG?")
                        q10 = st.radio("Đáp án Câu 10:", ["-- Chọn --", r"$V = \{xoài; ổi; mít\}$", "Tập $V$ có 3 phần tử", r"Sầu riêng $\notin V$", "Tất cả đều đúng"], key="q_10")
                        
                        submit_button = st.form_submit_button("Lưu & Nộp bài")
                    
                    if submit_button:
                        diem = 0
                        if q1 == r"$4 \in A$": diem += 1
                        if q2 == r"$\mathbb{N}^*$": diem += 1
                        if q3 == "3 phần tử": diem += 1
                        if q4 == r"$P = \{0; 1; 2; 3\}$": diem += 1
                        if q5 == r"$X = \{4; 5; 6\}$": diem += 1
                        if q6 == "7": diem += 1
                        if q7 == r"$0 \in E$": diem += 1
                        if q8 == r"$T = \{A; N; G; I\}$": diem += 1
                        if q9 == r"$K = \{4; 6; 9; 11\}$": diem += 1
                        if q10 == "Tất cả đều đúng": diem += 1
                        
                        if diem >= 7:
                            st.success(f"🎉 TUYỆT VỜI! Em đạt **{diem}/10** điểm. Bài học số 2 đã được mở khóa!")
                            st.balloons()
                            st.session_state.hoan_thanh_bai_1 = True
                        else:
                            st.error(f"⚠️ Em mới đạt **{diem}/10** điểm. Chưa đủ 7.0 điểm để qua cửa rồi. Hãy làm lại nhé!")
                            st.session_state.hoan_thanh_bai_1 = False

                with tab_mo_rong:
                    st.subheader("👨‍🔬 Nhà toán học Georg Cantor (1845 - 1918)")
                    st.write("Lí thuyết tập hợp được phát triển nhờ các nghiên cứu của nhà toán học Cantor, người Đức, và đã trở thành nền tảng của Toán học hiện đại.")
                    
            # ---------------- BÀI 2 ----------------
            elif bai_hoc_selection == "Bài 2. Cách ghi số tự nhiên":
                if st.session_state.get("hoan_thanh_bai_1", False) == True:
                    st.header("BÀI 2: CÁCH GHI SỐ TỰ NHIÊN")
                    st.success("🔓 Chào mừng em đến với Bài 2!")
                    st.write("Nội dung bài học đang được biên soạn...")
                else:
                    st.warning("🔒 **BÀI HỌC BỊ KHÓA**")
                    st.info("Em cần quay lại **Bài 1. Tập hợp** và hoàn thành bài Đánh giá năng lực (đạt từ 7.0 điểm trở lên) để mở khóa bài học này nhé!")
            else:
                st.info("Nội dung đang được cập nhật...")
