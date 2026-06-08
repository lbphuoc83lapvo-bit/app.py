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
# 2. ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS
# ==========================================
# ==========================================
# 2. ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    user_df = conn.read(worksheet="Câu trả lời biểu mẫu 1", ttl=0) 
    
    # Lọc bỏ dòng trống
    user_df = user_df.dropna(subset=[user_df.columns[1], user_df.columns[2], user_df.columns[3]], how='all')
    
    # Đảm bảo có đủ 5 cột (thêm cột Tiến độ nếu chưa có)
    while len(user_df.columns) < 5:
        user_df[f"Cột mới {len(user_df.columns)}"] = ""

    # MÀNG LỌC KIM CƯƠNG: Đổi tất cả ô trống thành rỗng và ép toàn bộ bảng thành kiểu Chữ
    user_df = user_df.fillna("").astype(str)

    if len(user_df.columns) >= 4:
        email_hs = user_df.iloc[:, 1].str.strip()
        ten_dang_nhap = user_df.iloc[:, 2].str.strip()
        
        # Đọc mật khẩu và XÓA SẠCH đuôi .0 nếu hệ thống tự sinh ra
        mat_khau = user_df.iloc[:, 3].str.strip()
        mat_khau = mat_khau.str.replace(r'\.0$', '', regex=True)
        
        tien_do = user_df.iloc[:, 4].str.strip() # Đọc Cột E (Tiến độ)
        
        user_db = dict(zip(ten_dang_nhap, mat_khau))
        email_db = dict(zip(email_hs, mat_khau))
        progress_db = dict(zip(ten_dang_nhap, tien_do))
    else:
        user_db, email_db, progress_db = {}, {}, {}
except Exception as e:
    st.error(f"⚠️ Lỗi kết nối dữ liệu: {e}")
    user_db, email_db, progress_db = {}, {}, {}# Khởi tạo trạng thái
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
                    
                    # TỰ ĐỘNG KHÔI PHỤC TIẾN ĐỘ TỪ SHEET XUỐNG BỘ NHỚ
                    # Dùng str() để ép kiểu, xử lý triệt để lỗi TypeError khi ô Sheet bị trống
                    tien_do_hien_tai = str(progress_db.get(_user, ""))
                    
                    if "Pass_Bai_1" in tien_do_hien_tai:
                        st.session_state.hoan_thanh_bai_1 = True
                    else:
                        st.session_state.hoan_thanh_bai_1 = False
                        
                    if "Pass_Bai_2" in tien_do_hien_tai:
                        st.session_state.hoan_thanh_bai_2 = True
                    else:
                        st.session_state.hoan_thanh_bai_2 = False
                        
                    st.success(f"Đăng nhập thành công! Xin chào {_user}.")
                    st.rerun()
                    
    # --- ĐĂNG KÝ ---
    with tab_register:
        st.write("Vui lòng điền thông tin vào biểu mẫu dưới đây để tạo tài khoản mới.")
        # THAY LINK GOOGLE FORM MỚI CỦA BẠN VÀO ĐÂY:
        link_form = "https://docs.google.com/forms/d/e/1FAIpQLSf7iu4VKmLegqRKqCg6PahJprCNAEhfDZkfEo6fcje7BgJK4g/viewform?usp=preview"
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
            "Chương 5: TÍNH ĐỐI XỨNG CỦA HÌNH PHẲNG TRONG THỰC TIỄN",
            "Chương 6: PHÂN SỐ",
            "Chương 7: SỐ THẬP PHÂN",
            "Chương 8: NHỮNG HÌNH HÌNH HỌC CƠ BẢN",
            "Chương 9: DỮ LIỆU VÀ XÁC SUẤT THỰC NGHIỆM"
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
            danh_sach_bai = [
                "Bài 1. Tập hợp",
                "Bài 2. Cách ghi số tự nhiên",
                "Bài 3. Thứ tự trong tập hợp các số tự nhiên",
                "Bài 4. Phép cộng và phép trừ số tự nhiên",
                "Bài 5. Phép nhân và phép chia số tự nhiên",
                "Luyện tập chung",
                "Bài 6. Luỹ thừa với số mũ tự nhiên",
                "Bài 7. Thứ tự thực hiện các phép tính",
                "Luyện tập chung (trang 27)",
                "Bài tập cuối chương I"
            ]
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

                    # ==================================================
                    # THẦY DÁN ĐOẠN CODE LUYỆN TẬP VÀO BẮT ĐẦU TỪ ĐÂY:
                    # ==================================================
                    st.markdown("---")
                    st.subheader("🎯 Thử thách Luyện tập")
                    
                    # 1. Thử thách nhỏ (Vận dụng)
                    st.success(r"📝 **Thử thách Vận dụng:** Khi viết tập hợp $L$ các chữ cái trong từ 'NHA TRANG' bằng cách liệt kê, bạn Nam viết: $L = \{N; H; A; T; R; A; N; G\}$. Theo em bạn Nam viết đúng hay sai?")
                    chose_nam = st.radio("Câu trả lời của bạn:", ["Chưa chọn", "Nam viết ĐÚNG", "Nam viết SAI"], key="quiz_nam")
                    
                    if chose_nam == "Nam viết SAI":
                        st.success(r"🎉 Chính xác! Mỗi phần tử chỉ được viết 1 lần. Chữ N và chữ A xuất hiện 2 lần nên chỉ viết lại 1 lần. Cách viết đúng là: $L = \{N; H; A; T; R; G\}$.")
                    elif chose_nam == "Nam viết ĐÚNG":
                        st.error("❌ Chưa chính xác rồi! Em hãy nhớ quy tắc: Mỗi phần tử chỉ được liệt kê duy nhất một lần nhé.")

                    # 2. Luyện tập 2
                    st.info(r"**Luyện tập 2:** Viết các tập hợp sau bằng cách liệt kê các phần tử: $A=\{x \in \mathbb{N} \mid x<5\}$ và $B=\{x \in \mathbb{N}^* \mid x<5\}$. Hãy chọn đáp án đúng nhất:")
                    lt2 = st.radio("Chọn đáp án cho Luyện tập 2:", [
                        "Chưa chọn", 
                        r"$A = \{1; 2; 3; 4\}$ và $B = \{0; 1; 2; 3; 4\}$", 
                        r"$A = \{0; 1; 2; 3; 4\}$ và $B = \{1; 2; 3; 4\}$", 
                        r"$A = \{0; 1; 2; 3; 4; 5\}$ và $B = \{1; 2; 3; 4; 5\}$"
                    ], key="lt2")
                    
                    if lt2 == r"$A = \{0; 1; 2; 3; 4\}$ và $B = \{1; 2; 3; 4\}$":
                        st.success(r"🎉 Rất xuất sắc! $\mathbb{N}$ bắt đầu từ số 0, còn $\mathbb{N}^*$ bắt đầu từ số 1. Cả hai tập hợp đều lấy các số nhỏ hơn 5 (tức là không lấy số 5).")
                    elif lt2 != "Chưa chọn":
                        st.error(r"❌ Hãy cẩn thận! Tập $\mathbb{N}$ có chứa số 0, còn tập $\mathbb{N}^*$ thì không chứa số 0. Và nhớ điều kiện là $x < 5$ nhé.")

                    # 3. Luyện tập 3
                    st.info(r"**Luyện tập 3:** Gọi $M$ là tập hợp các số tự nhiên lớn hơn 6 và nhỏ hơn 10. Khẳng định nào dưới đây mô tả **ĐÚNG** nhất về tập hợp $M$?")
                    lt3 = st.radio("Chọn đáp án cho Luyện tập 3:", [
                        "Chưa chọn", 
                        r"$5 \in M$, $9 \in M$ và $M = \{7; 8; 9\}$", 
                        r"$5 \notin M$, $9 \in M$ và $M = \{7; 8; 9\}$", 
                        r"$5 \notin M$, $9 \notin M$ và $M = \{6; 7; 8; 9; 10\}$"
                    ], key="lt3")
                    
                    if lt3 == r"$5 \notin M$, $9 \in M$ và $M = \{7; 8; 9\}$":
                        st.success(r"🎉 Chính xác! Vì $M$ gồm các số lớn hơn 6 và nhỏ hơn 10 nên $M = \{7; 8; 9\}$. Do đó số 5 không thuộc $M$, còn số 9 thuộc $M$.")
                    elif lt3 != "Chưa chọn":
                        st.error("❌ Chưa đúng rồi! Em hãy liệt kê các số tự nhiên nằm giữa 6 và 10 trước, sau đó xét xem số 5 và số 9 có nằm trong tập hợp đó không nhé.")

                with tab_bai_tap:
                    st.subheader("✍️ Đánh giá năng lực - Bài 1")
                    st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA:** Em cần trả lời đúng ít nhất **7/10 câu** (Đạt từ 7.0 điểm) để hệ thống mở khóa Bài 2 nhé!")
                    
                    # Dùng form để học sinh chọn hết rồi mới nộp bài
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
                        
                        # Nút nộp bài
                        submit_button = st.form_submit_button("Lưu & Nộp bài")
                    
                    # Logic chấm điểm sau khi bấm nộp
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
                        
                        if diem >= 7: # Điểm ví dụ
                            st.success(f"🎉 TUYỆT VỜI! Em đạt điểm tối đa. Bài học số 2 đã được mở khóa!")
                            st.balloons()
                            
                            # CHỈ GHI LÊN SHEET NẾU HỌC SINH CHƯA PASS BÀI 1
                            if not st.session_state.get("hoan_thanh_bai_1", False):
                                st.session_state.hoan_thanh_bai_1 = True
                                current_user = st.session_state.current_user
                                user_idx = user_df[user_df.iloc[:, 2].astype(str).str.strip() == current_user].index
                                
                                if not user_idx.empty:
                                    tien_do_cu = str(user_df.loc[user_idx[0], user_df.columns[4]])
                                    
                                    # Ghi nối thêm chữ Pass_Bai_1
                                    if "Pass_Bai_1" not in tien_do_cu:
                                        tien_do_moi = tien_do_cu + ", Pass_Bai_1" if tien_do_cu.strip() and tien_do_cu != "nan" else "Pass_Bai_1"
                                        
                                        # Cập nhật vào df trong bộ nhớ
                                        user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                        
                                        try:
                                            import gspread
                                            # Lấy chìa khóa từ Két sắt
                                            kh = st.secrets["connections"]["gsheets"]
                                            creds = {
                                                "type": kh["type"],
                                                "project_id": kh["project_id"],
                                                "private_key_id": kh["private_key_id"],
                                                "private_key": kh["private_key"],
                                                "client_email": kh["client_email"],
                                                "client_id": kh["client_id"],
                                                "auth_uri": kh["auth_uri"],
                                                "token_uri": kh["token_uri"],
                                                "auth_provider_x509_cert_url": kh["auth_provider_x509_cert_url"],
                                                "client_x509_cert_url": kh["client_x509_cert_url"]
                                            }
                                            # Đăng nhập trực tiếp bằng thư viện gốc gspread
                                            gc = gspread.service_account_from_dict(creds)
                                            sheet_goc = gc.open_by_url(kh["spreadsheet"]).worksheet("Câu trả lời biểu mẫu 1")
                                            
                                            # Bắn tỉa: Ghi vào đúng 1 ô
                                            dong_sheet = int(user_idx[0]) + 2 
                                            o_can_ghi = f"E{dong_sheet}" 
                                            sheet_goc.update_acell(o_can_ghi, tien_do_moi)
                                            
                                            st.cache_data.clear()
                                        except Exception as e:
                                            st.error(f"❌ Lỗi ghi dữ liệu: {e}")
                        else:
                            st.error(f"⚠️ Em chưa đủ điểm. Hãy ôn lại lý thuyết và làm lại nhé!")
                            st.session_state.hoan_thanh_bai_1 = False

                with tab_mo_rong:
                    st.subheader("👨‍🔬 Kiến thức mở rộng")
                    st.write(r"Giao của hai tập hợp $A$ và $B$ được kí hiệu là $C = A \cap B$.")
                    
            # ---------------- BÀI 2 ----------------
            elif bai_hoc_selection == "Bài 2. Cách ghi số tự nhiên":
                if st.session_state.get("hoan_thanh_bai_1", False) == True:
                    st.header("BÀI 2: CÁCH GHI SỐ TỰ NHIÊN")
                    
                    tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                    
                    with tab_ly_thuyet:
                        st.markdown("**🎥 Video bài giảng trực tuyến**")
                        st.video("https://youtu.be/1hegILoKiGI")
                        st.markdown("---")
                        
                        st.subheader("1. Hệ thập phân")
                        st.markdown("**a) Cách ghi số tự nhiên trong hệ thập phân**")
                        st.write(r"- Mỗi số tự nhiên được viết dưới dạng một dãy những chữ số lấy trong 10 chữ số: $0, 1, 2, 3, 4, 5, 6, 7, 8, 9$.")
                        st.write("- Vị trí của các chữ số trong dãy gọi là **hàng**.")
                        st.write("- Cứ 10 đơn vị ở một hàng thì bằng 1 đơn vị ở hàng liền trước nó (Ví dụ: 10 chục = 1 trăm).")
                        
                        st.info("💡 **Chú ý:** Với các số tự nhiên khác 0, chữ số đầu tiên (từ trái sang phải) phải khác 0. Để dễ đọc, với các số có từ 4 chữ số trở lên, ta viết tách riêng từng lớp, mỗi lớp 3 chữ số từ phải sang trái.")
                        
                        st.markdown("**b) Giá trị các chữ số của một số tự nhiên**")
                        st.write("Mỗi số tự nhiên viết trong hệ thập phân đều biểu diễn được thành tổng giá trị các chữ số của nó.")
                        st.latex(r"\overline{ab} = (a \times 10) + b \quad (a \neq 0)")
                        st.latex(r"\overline{abc} = (a \times 100) + (b \times 10) + c \quad (a \neq 0)")
                        st.write("Ví dụ:")
                        st.latex(r"236 = (2 \times 100) + (3 \times 10) + 6")

                        st.markdown("---")
                        st.subheader("2. Số La Mã")
                        st.write("Để viết các số La Mã không quá 30, ta dùng các thành phần sau:")
                        st.markdown("""
                        | Kí hiệu | I | V | X | IV | IX |
                        | :---: | :---: | :---: | :---: | :---: | :---: |
                        | **Giá trị** | 1 | 5 | 10 | 4 | 9 |
                        """)
                        st.write(r"- **Từ 11 đến 20:** Thêm **X** vào bên trái các số từ 1 đến 10 (Ví dụ: $\text{XIV} = 14$, $\text{XVI} = 16$).")
                        st.write(r"- **Từ 21 đến 30:** Thêm **XX** vào bên trái các số từ 1 đến 10 (Ví dụ: $\text{XXIV} = 24$, $\text{XXVII} = 27$).")
                        st.success("📝 **Nhận xét:** Mỗi số La Mã biểu diễn một số tự nhiên bằng tổng giá trị của các thành phần viết nên số đó. **Không có số La Mã nào biểu diễn số 0.**")

                        # ==========================================
                        # PHẦN THỬ THÁCH TƯƠNG TÁC (TỪ SGK)
                        # ==========================================
                        st.markdown("---")
                        st.subheader("🎯 Thử thách Luyện tập & Vận dụng")
                        
                        st.info(r"**Thử thách 1 (Luyện tập):** Viết số $34~604$ thành tổng giá trị các chữ số của nó.")
                        tt1 = st.radio("Chọn cách viết đúng nhất:", [
                            "Chưa chọn",
                            r"$(3 \times 10~000) + (4 \times 1~000) + (6 \times 10) + 4$",
                            r"$(3 \times 10~000) + (4 \times 1~000) + (6 \times 100) + 4$",
                            r"$(3 \times 1~000) + (4 \times 100) + (6 \times 10) + 4$"
                        ], key="b2_tt1")
                        if tt1 == r"$(3 \times 10~000) + (4 \times 1~000) + (6 \times 100) + 4$":
                            st.success("🎉 Rất chính xác! Số 6 nằm ở hàng trăm nên phải nhân với 100, và hàng chục là số 0 nên ta có thể bỏ qua.")
                        elif tt1 != "Chưa chọn":
                            st.error("❌ Chưa đúng rồi! Em hãy chú ý vị trí của chữ số 6 nằm ở hàng nào nhé.")

                        st.info(r"**Thử thách 2 (Luyện tập):** Số tự nhiên $27$ được viết bằng số La Mã là:")
                        tt2 = st.radio("Chọn đáp án đúng:", [
                            "Chưa chọn", "XXV", "XXVII", "XXIIV"
                        ], key="b2_tt2")
                        if tt2 == "XXVII":
                            st.success(r"🎉 Chính xác! $27 = 20 + 7$, biểu diễn là $\text{XX}$ ghép với $\text{VII}$ thành $\text{XXVII}$.")
                        elif tt2 != "Chưa chọn":
                            st.error(r"❌ Hãy xem lại bảng số La Mã! Nhớ rằng chữ số V không bao giờ đứng sau II nhé.")

                        st.success(r"**Thử thách 3 (Vận dụng):** Bác Hoa đi chợ mang 3 loại tiền: 1 nghìn, 10 nghìn và 100 nghìn đồng. Tổng số tiền phải trả là 492 nghìn đồng. Nếu mỗi loại tiền mang không quá 9 tờ, bác phải trả mỗi loại bao nhiêu tờ để không cần nhận tiền thừa?")
                        tt3 = st.radio("Phương án trả tiền của bác Hoa:", [
                            "Chưa chọn",
                            "4 tờ 100 nghìn, 9 tờ 10 nghìn, 2 tờ 1 nghìn",
                            "4 tờ 100 nghìn, 8 tờ 10 nghìn, 12 tờ 1 nghìn",
                            "5 tờ 100 nghìn, không dùng tiền 10 nghìn, nhận lại 8 nghìn"
                        ], key="b2_tt3")
                        if tt3 == "4 tờ 100 nghìn, 9 tờ 10 nghìn, 2 tờ 1 nghìn":
                            st.success(r"🎉 Xuất sắc! Đây chính là cấu trúc phân tích số thập phân: $492 = (4 \times 100) + (9 \times 10) + 2$.")
                        elif tt3 != "Chưa chọn":
                            st.error("❌ Chưa đúng! Đề bài yêu cầu không cần tiền thừa và mỗi loại không quá 9 tờ. Hãy sử dụng phân tích cấu trúc số thập phân để giải nhé!")

                    with tab_bai_tap:
                        st.subheader("✍️ Đánh giá năng lực - Bài 2")
                        st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA BÀI 3:** Em cần đạt tối thiểu **7.0/10 điểm** trong bài kiểm tra này.")
                        
                        with st.form("quiz_bai_2"):
                            st.markdown("### I. Mức độ Nhận biết (3 điểm)")
                            st.markdown(r"**Câu 1:** Chữ số $4$ đứng ở hàng nào trong một số tự nhiên nếu nó có giá trị bằng $40$?")
                            q1 = st.radio("Đáp án Câu 1:", ["-- Chọn --", "Hàng đơn vị", "Hàng chục", "Hàng trăm", "Hàng nghìn"], key="b2_q1")
                            
                            st.markdown(r"**Câu 2:** Số La Mã $\text{XXIV}$ tương ứng với số tự nhiên nào?")
                            q2 = st.radio("Đáp án Câu 2:", ["-- Chọn --", "24", "26", "14", "214"], key="b2_q2")
                            
                            st.markdown(r"**Câu 3:** Khẳng định nào sau đây là **SAI** khi nói về số tự nhiên trong hệ thập phân?")
                            q3 = st.radio("Đáp án Câu 3:", ["-- Chọn --", "Có 10 chữ số để ghi mọi số tự nhiên.", "Giá trị của chữ số phụ thuộc vào vị trí (hàng) của nó.", "Cứ 10 đơn vị ở một hàng thì bằng 1 đơn vị ở hàng liền sau nó.", "Số tự nhiên khác 0 luôn có chữ số đầu tiên bên trái khác 0."], key="b2_q3")
                            
                            st.markdown("---")
                            st.markdown("### II. Mức độ Thông hiểu (4 điểm)")
                            st.markdown(r"**Câu 4:** Viết số $18$ bằng số La Mã:")
                            q4 = st.radio("Đáp án Câu 4:", ["-- Chọn --", "XVII", "XVIII", "XIVV", "XIIX"], key="b2_q4")
                            
                            st.markdown(r"**Câu 5:** Trong số $106~712$, chữ số $7$ có giá trị là bao nhiêu?")
                            q5 = st.radio("Đáp án Câu 5:", ["-- Chọn --", "7", "70", "700", "7000"], key="b2_q5")
                            
                            st.markdown(r"**Câu 6:** Cách biểu diễn số $2~023$ thành tổng các giá trị chữ số nào sau đây là **ĐÚNG**?")
                            q6 = st.radio("Đáp án Câu 6:", ["-- Chọn --", r"$(2 \times 1~000) + (2 \times 100) + 3$", r"$(2 \times 1~000) + (2 \times 10) + 3$", r"$(2 \times 1~000) + (20 \times 10) + 3$", r"$2 + 0 + 2 + 3$"], key="b2_q6")
                            
                            st.markdown(r"**Câu 7:** Số chẵn lớn nhất có $3$ chữ số khác nhau trong hệ thập phân là số nào?")
                            q7 = st.radio("Đáp án Câu 7:", ["-- Chọn --", "998", "986", "987", "988"], key="b2_q7")
                            
                            st.markdown("---")
                            st.markdown("### III. Mức độ Vận dụng (3 điểm)")
                            st.markdown(r"**Câu 8:** Dùng các chữ số $0, 3, 5$, em hãy viết một số tự nhiên có ba chữ số khác nhau sao cho chữ số $5$ có giá trị là $50$.")
                            q8 = st.radio("Đáp án Câu 8:", ["-- Chọn --", "305", "530", "350", "503"], key="b2_q8")
                            
                            st.markdown(r"**Câu 9:** Một số tự nhiên được viết bởi ba chữ số $0$ và ba chữ số $9$ nằm xen kẽ nhau. Đó là số nào?")
                            q9 = st.radio("Đáp án Câu 9:", ["-- Chọn --", "909 090", "90 909", "900 099", "999 000"], key="b2_q9")
                            
                            st.markdown(r"**Câu 10:** Trong một cửa hàng, người ta đóng gói: 1 gói = 10 cái; 1 hộp = 10 gói; 1 thùng = 10 hộp. Một người mua 9 thùng, 9 hộp và 9 gói kẹo. Hỏi người đó mua tất cả bao nhiêu cái kẹo?")
                            q10 = st.radio("Đáp án Câu 10:", ["-- Chọn --", "999 cái", "9 990 cái", "9 099 cái", "9 900 cái"], key="b2_q10")
                            
                            submit_b2 = st.form_submit_button("Lưu & Nộp bài")
                            
                        if submit_b2:
                            diem = 0
                            if q1 == "Hàng chục": diem += 1
                            if q2 == "24": diem += 1
                            if q3 == "Cứ 10 đơn vị ở một hàng thì bằng 1 đơn vị ở hàng liền sau nó.": diem += 1
                            if q4 == "XVIII": diem += 1
                            if q5 == "700": diem += 1
                            if q6 == r"$(2 \times 1~000) + (2 \times 10) + 3$": diem += 1
                            if q7 == "986": diem += 1
                            if q8 == "350": diem += 1
                            if q9 == "909 090": diem += 1
                            if q10 == "9 990 cái": diem += 1
                            
                            if diem >= 7:
                                st.success(f"🎉 RẤT XUẤT SẮC! Em đạt **{diem}/10** điểm. Bài học số 3 đã được mở khóa!")
                                st.balloons()
                                
                                # GHI LÊN SHEET NẾU HỌC SINH CHƯA PASS BÀI 2
                                if not st.session_state.get("hoan_thanh_bai_2", False):
                                    st.session_state.hoan_thanh_bai_2 = True
                                    current_user = st.session_state.current_user
                                    user_idx = user_df[user_df.iloc[:, 2].astype(str).str.strip() == current_user].index
                                    
                                    if not user_idx.empty:
                                        tien_do_cu = str(user_df.loc[user_idx[0], user_df.columns[4]])
                                        if "Pass_Bai_2" not in tien_do_cu:
                                            tien_do_moi = tien_do_cu + ", Pass_Bai_2" if tien_do_cu.strip() and tien_do_cu != "nan" else "Pass_Bai_2"
                                            
                                            # Cập nhật vào df trong bộ nhớ
                                            user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                            
                                            try:
                                                import gspread
                                                kh = st.secrets["connections"]["gsheets"]
                                                creds = {
                                                    "type": kh["type"],
                                                    "project_id": kh["project_id"],
                                                    "private_key_id": kh["private_key_id"],
                                                    "private_key": kh["private_key"],
                                                    "client_email": kh["client_email"],
                                                    "client_id": kh["client_id"],
                                                    "auth_uri": kh["auth_uri"],
                                                    "token_uri": kh["token_uri"],
                                                    "auth_provider_x509_cert_url": kh["auth_provider_x509_cert_url"],
                                                    "client_x509_cert_url": kh["client_x509_cert_url"]
                                                }
                                                gc = gspread.service_account_from_dict(creds)
                                                sheet_goc = gc.open_by_url(kh["spreadsheet"]).worksheet("Câu trả lời biểu mẫu 1")
                                                
                                                dong_sheet = int(user_idx[0]) + 2 
                                                o_can_ghi = f"E{dong_sheet}" 
                                                sheet_goc.update_acell(o_can_ghi, tien_do_moi)
                                                
                                                st.cache_data.clear()
                                            except Exception as e:
                                                st.error(f"❌ Lỗi ghi dữ liệu: {e}")
                            else:
                                st.error(f"⚠️ Em mới đạt **{diem}/10** điểm. Chưa đủ 7.0 điểm để qua cửa rồi. Hãy ôn lại bài và làm lại nhé!")
                                st.session_state.hoan_thanh_bai_2 = False

                    with tab_mo_rong:
                        st.subheader("🏛️ Mở rộng: Hệ La Mã")
                        st.write("Ngoài các chữ số cơ bản, hệ La Mã còn dùng các chữ số lớn hơn:")
                        st.markdown("""
                        - **L** = 50
                        - **C** = 100
                        - **D** = 500
                        - **M** = 1000
                        """)
                        st.write("Quy tắc: Chữ số I, X, C, M không lặp lại quá 3 lần liên tiếp. Chữ số V, L, D có mặt không quá 1 lần.")
                        st.info(r"Ví dụ: **MMXIX** biểu diễn số $1000 + 1000 + 10 + 9 = 2019$.")
                        
                        st.markdown("---")
                        st.subheader("💻 Hệ nhị phân với cuộc sống")
                        st.write("Để ghi số trong **hệ nhị phân**, ta chỉ dùng hai chữ số là **0** và **1**. Hai chữ số này tương ứng với hai trạng thái 'đóng' và 'mở' của mạch điện, nên được ứng dụng cốt lõi trong **Khoa học máy tính**.")
                        st.write(r"Chẳng hạn, số **4** trong hệ thập phân được viết là **100** trong hệ nhị phân!")
                # ---------------- BÀI 3 ----------------
            elif bai_hoc_selection == "Bài 3. Thứ tự trong tập hợp các số tự nhiên":
                if st.session_state.get("hoan_thanh_bai_2", False) == True:
                    st.header("BÀI 3: THỨ TỰ TRONG TẬP HỢP CÁC SỐ TỰ NHIÊN")
                    
                    tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                    
                    with tab_ly_thuyet:
                        st.markdown("**🎥 Video bài giảng trực tuyến**")
                        st.video("https://youtu.be/m1jVUeC8s7c") 
                        st.markdown("---")
                        
                        st.subheader("1. Thứ tự của các số tự nhiên trên tia số")
                        st.write(r"- Tập hợp các số tự nhiên $\mathbb{N} = \{0; 1; 2; 3; \dots\}$ được biểu diễn trên một **tia số**.")
                        
                        # CHÈN ẢNH TỪ FILE TRONG GITHUB TẠI ĐÂY:
                        st.image("tiaso.png", caption="Hình 1.5: Điểm biểu diễn số tự nhiên trên tia số", use_container_width=True)
                        
                        st.write(r"- Mỗi số tự nhiên được biểu diễn bởi một điểm...")
                        
                        st.write(r"- Mỗi số tự nhiên được biểu diễn bởi một điểm. Điểm biểu diễn số tự nhiên $a$ gọi là điểm $a$.")
                        st.write(r"- Trong hai số tự nhiên khác nhau, luôn có một số nhỏ hơn số kia. Nếu $a$ nhỏ hơn $b$ (kí hiệu $a < b$), thì trên tia số nằm ngang, **điểm $a$ nằm bên trái điểm $b$**.")
                        
                        st.markdown("---")
                        st.subheader("2. Số liền trước, số liền sau và tính chất bắc cầu")
                        st.write("- Mỗi số tự nhiên có đúng một **số liền sau**. Hai số tự nhiên liên tiếp hơn kém nhau 1 đơn vị.")
                        st.write(r"*(Ví dụ: 9 là số liền sau của 8; 8 là số liền trước của 9. Hai số 8 và 9 là hai số tự nhiên liên tiếp).*")
                        st.write(r"- **Tính chất bắc cầu:** Nếu $a < b$ và $b < c$ thì $a < c$.")
                        st.warning("🚨 **Chú ý quan trọng:** Số 0 là số tự nhiên nhỏ nhất và **không có** số tự nhiên liền trước.")

                        st.markdown("---")
                        st.subheader(r"3. Các kí hiệu $\le$ và $\ge$")
                        st.write(r"- Kí hiệu $a \le b$ (đọc là: $a$ nhỏ hơn hoặc bằng $b$) nghĩa là $a < b$ hoặc $a = b$.")
                        st.write(r"- Kí hiệu $a \ge b$ (đọc là: $a$ lớn hơn hoặc bằng $b$) nghĩa là $a > b$ hoặc $a = b$.")
                        st.info(r"💡 **Ví dụ:** Tập hợp $\{x \in \mathbb{N} \mid x \le 4\} = \{0; 1; 2; 3; 4\}$. Khác với $\{x \in \mathbb{N} \mid x < 4\} = \{0; 1; 2; 3\}$.")

                        # ==========================================
                        # PHẦN THỬ THÁCH TƯƠNG TÁC (TỪ SGK)
                        # ==========================================
                        st.markdown("---")
                        st.subheader("🎯 Thử thách Luyện tập & Vận dụng")
                        
                        st.success(r"📝 **Thử thách 1 (Luyện tập):** Hãy so sánh hai số $m = 12~036~001$ và $n = 12~035~987$. Trên tia số nằm ngang, điểm nào sẽ nằm trước (nằm bên trái)?")
                        tt1 = st.radio("Lựa chọn của em:", [
                            "Chưa chọn",
                            r"$m < n$ và điểm $m$ nằm trước",
                            r"$m > n$ và điểm $n$ nằm trước",
                            r"$m > n$ và điểm $m$ nằm trước"
                        ], key="b3_tt1")
                        
                        if tt1 == r"$m > n$ và điểm $n$ nằm trước":
                            st.success(r"🎉 Rất chính xác! Ở hàng nghìn, số $m$ có chữ số 6 lớn hơn chữ số 5 của số $n$, nên $m > n$. Do đó số $n$ nhỏ hơn sẽ nằm bên trái (nằm trước).")
                        elif tt1 != "Chưa chọn":
                            st.error("❌ Em hãy so sánh từ trái sang phải nhé. Chữ số ở hàng nghìn của hai số khác nhau đấy!")

                        st.info(r"📝 **Thử thách 2 (Vận dụng):** Theo dõi bán hàng, người ta nhận thấy: Số tiền thu được buổi sáng NHIỀU HƠN buổi chiều; Số tiền buổi tối ÍT HƠN buổi chiều. Hãy so sánh số tiền thu được của buổi sáng và buổi tối?")
                        tt2 = st.radio("Kết quả so sánh:", [
                            "Chưa chọn", 
                            "Buổi sáng thu được nhiều tiền hơn buổi tối", 
                            "Buổi tối thu được nhiều tiền hơn buổi sáng",
                            "Hai buổi thu được bằng nhau"
                        ], key="b3_tt2")
                        
                        if tt2 == "Buổi sáng thu được nhiều tiền hơn buổi tối":
                            st.success(r"🎉 Xuất sắc! Đây chính là ứng dụng của **tính chất bắc cầu**. Gọi số tiền sáng, chiều, tối là S, C, T. Ta có: $S > C$ và $C > T$, suy ra $S > T$.")
                        elif tt2 != "Chưa chọn":
                            st.error("❌ Em hãy thử dùng tính chất bắc cầu: Sáng > Chiều, mà Chiều lại > Tối. Vậy Sáng và Tối cái nào lớn hơn?")

                    with tab_bai_tap:
                        st.subheader("✍️ Đánh giá năng lực - Bài 3")
                        st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA BÀI 4:** Em cần đạt tối thiểu **7.0/10 điểm** trong bài kiểm tra này.")
                        
                        with st.form("quiz_bai_3"):
                            st.markdown("### I. Mức độ Nhận biết (3 điểm)")
                            st.markdown(r"**Câu 1:** Số tự nhiên nhỏ nhất là số nào?")
                            q1 = st.radio("Đáp án Câu 1:", ["-- Chọn --", "1", "0", "Không có số nhỏ nhất", "10"], key="b3_q1")
                            
                            st.markdown(r"**Câu 2:** Kí hiệu $\ge$ được đọc là gì?")
                            q2 = st.radio("Đáp án Câu 2:", ["-- Chọn --", "Nhỏ hơn hoặc bằng", "Lớn hơn", "Lớn hơn hoặc bằng", "Bằng nhau"], key="b3_q2")
                            
                            st.markdown(r"**Câu 3:** Số tự nhiên liền sau của số $2025$ là số nào?")
                            q3 = st.radio("Đáp án Câu 3:", ["-- Chọn --", "2024", "2026", "2027", "Không có"], key="b3_q3")
                            
                            st.markdown("---")
                            st.markdown("### II. Mức độ Thông hiểu (4 điểm)")
                            st.markdown(r"**Câu 4:** Viết tập hợp $A = \{x \in \mathbb{N} \mid x \le 3\}$ bằng cách liệt kê:")
                            q4 = st.radio("Đáp án Câu 4:", ["-- Chọn --", r"$\{0; 1; 2\}$", r"$\{1; 2; 3\}$", r"$\{0; 1; 2; 3\}$", r"$\{1; 2; 3; 4\}$"], key="b3_q4")
                            
                            st.markdown(r"**Câu 5:** Cho ba số tự nhiên $a, b, c$ trong đó $a$ là số nhỏ nhất. Biết điểm $b$ nằm giữa hai điểm $a$ và $c$ trên tia số. Dùng kí hiệu biểu diễn đúng nhất là:")
                            q5 = st.radio("Đáp án Câu 5:", ["-- Chọn --", r"$a < c < b$", r"$a < b < c$", r"$b < a < c$", r"$c < b < a$"], key="b3_q5")
                            
                            st.markdown(r"**Câu 6:** Trong các số 3; 5; 8; 9. Có bao nhiêu số thuộc tập hợp $B = \{x \in \mathbb{N} \mid x \ge 5\}$?")
                            q6 = st.radio("Đáp án Câu 6:", ["-- Chọn --", "1 số", "2 số", "3 số", "4 số"], key="b3_q6")
                            
                            st.markdown(r"**Câu 7:** Sắp xếp các số $3532; 3529; 3531; 3530$ theo thứ tự từ bé đến lớn:")
                            q7 = st.radio("Đáp án Câu 7:", ["-- Chọn --", "3529; 3530; 3531; 3532", "3532; 3531; 3530; 3529", "3529; 3531; 3530; 3532", "3530; 3529; 3531; 3532"], key="b3_q7")
                            
                            st.markdown("---")
                            st.markdown("### III. Mức độ Vận dụng (3 điểm)")
                            st.markdown(r"**Câu 8:** Ba bạn An, Bắc, Cường đo chiều cao. An cao 150cm, Bắc cao 153cm, Cường cao 148cm. Đánh dấu trên một cây sào từ dưới lên trên (từ thấp đến cao) thì thứ tự các bạn là:")
                            q8 = st.radio("Đáp án Câu 8:", ["-- Chọn --", "An, Bắc, Cường", "Cường, An, Bắc", "Bắc, An, Cường", "Cường, Bắc, An"], key="b3_q8")
                            
                            st.markdown(r"**Câu 9:** Liệt kê các phần tử của tập hợp $M = \{x \in \mathbb{N} \mid 10 \le x < 13\}$:")
                            q9 = st.radio("Đáp án Câu 9:", ["-- Chọn --", r"$\{11; 12\}$", r"$\{10; 11; 12\}$", r"$\{10; 11; 12; 13\}$", r"$\{11; 12; 13\}$"], key="b3_q9")
                            
                            st.markdown(r"**Câu 10:** Số tự nhiên lớn nhất có 3 chữ số khác nhau là:")
                            q10 = st.radio("Đáp án Câu 10:", ["-- Chọn --", "999", "987", "989", "789"], key="b3_q10")
                            
                            submit_b3 = st.form_submit_button("Lưu & Nộp bài")
                            
                        if submit_b3:
                            diem = 0
                            if q1 == "0": diem += 1
                            if q2 == "Lớn hơn hoặc bằng": diem += 1
                            if q3 == "2026": diem += 1
                            if q4 == r"$\{0; 1; 2; 3\}$": diem += 1
                            if q5 == r"$a < b < c$": diem += 1
                            if q6 == "3 số": diem += 1
                            if q7 == "3529; 3530; 3531; 3532": diem += 1
                            if q8 == "Cường, An, Bắc": diem += 1
                            if q9 == r"$\{10; 11; 12\}$": diem += 1
                            if q10 == "987": diem += 1
                            
                            if diem >= 7:
                                st.success(f"🎉 RẤT XUẤT SẮC! Em đạt **{diem}/10** điểm. Bài học số 4 đã được mở khóa!")
                                st.balloons()
                                
                                # GHI LÊN SHEET NẾU HỌC SINH CHƯA PASS BÀI 3
                                if not st.session_state.get("hoan_thanh_bai_3", False):
                                    st.session_state.hoan_thanh_bai_3 = True
                                    current_user = st.session_state.current_user
                                    user_idx = user_df[user_df.iloc[:, 2].astype(str).str.strip() == current_user].index
                                    
                                    if not user_idx.empty:
                                        tien_do_cu = str(user_df.loc[user_idx[0], user_df.columns[4]])
                                        if "Pass_Bai_3" not in tien_do_cu:
                                            tien_do_moi = tien_do_cu + ", Pass_Bai_3" if tien_do_cu.strip() and tien_do_cu != "nan" else "Pass_Bai_3"
                                            
                                            # Cập nhật vào df trong bộ nhớ
                                            user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                            
                                            try:
                                                import gspread
                                                kh = st.secrets["connections"]["gsheets"]
                                                creds = {
                                                    "type": kh["type"],
                                                    "project_id": kh["project_id"],
                                                    "private_key_id": kh["private_key_id"],
                                                    "private_key": kh["private_key"],
                                                    "client_email": kh["client_email"],
                                                    "client_id": kh["client_id"],
                                                    "auth_uri": kh["auth_uri"],
                                                    "token_uri": kh["token_uri"],
                                                    "auth_provider_x509_cert_url": kh["auth_provider_x509_cert_url"],
                                                    "client_x509_cert_url": kh["client_x509_cert_url"]
                                                }
                                                gc = gspread.service_account_from_dict(creds)
                                                sheet_goc = gc.open_by_url(kh["spreadsheet"]).worksheet("Câu trả lời biểu mẫu 1")
                                                
                                                dong_sheet = int(user_idx[0]) + 2 
                                                o_can_ghi = f"E{dong_sheet}" 
                                                sheet_goc.update_acell(o_can_ghi, tien_do_moi)
                                                
                                                st.cache_data.clear()
                                            except Exception as e:
                                                st.error(f"❌ Lỗi ghi dữ liệu: {e}")
                            else:
                                st.error(f"⚠️ Em mới đạt **{diem}/10** điểm. Chưa đủ 7.0 điểm để qua cửa rồi. Hãy ôn lại bài và làm lại nhé!")
                                st.session_state.hoan_thanh_bai_3 = False

                    with tab_mo_rong:
                        st.subheader("🚀 Em có biết: Tại sao không có số tự nhiên lớn nhất?")
                        st.write("Vì tập hợp các số tự nhiên $\mathbb{N}$ là **vô hạn**. Cứ với bất kỳ một số tự nhiên nào em nghĩ ra, ta chỉ cần cộng thêm 1 là sẽ luôn tìm được số liền sau lớn hơn nó. Quá kì diệu phải không nào!")

                else:
                    st.warning("🔒 **BÀI HỌC BỊ KHÓA**")
                    st.info("Em cần quay lại **Bài 2. Cách ghi số tự nhiên** và hoàn thành Đánh giá năng lực (đạt từ 7.0 điểm trở lên) để mở khóa bài học này nhé!")
            # ---------------- BÀI 4 ----------------
            elif bai_hoc_selection == "Bài 4. Phép cộng và phép trừ số tự nhiên":
                if st.session_state.get("hoan_thanh_bai_3", False) == True:
                    st.header("BÀI 4: PHÉP CỘNG VÀ PHÉP TRỪ SỐ TỰ NHIÊN")
                    
                    tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                    
                    with tab_ly_thuyet:
                        st.markdown("**🎥 Video bài giảng trực tuyến**")
                        st.video("https://youtu.be/cdFTVZluTsk")
                        st.markdown("---")
                        
                        st.subheader("1. Phép cộng số tự nhiên")
                        st.write(r"- Phép cộng hai số tự nhiên $a$ và $b$ cho ta một số tự nhiên gọi là tổng của chúng, kí hiệu là $a + b$.")
                        st.latex(r"a \text{ (Số hạng)} + b \text{ (Số hạng)} = c \text{ (Tổng)}")
                        
                        st.write("**Tính chất của phép cộng:**")
                        st.write(r"- **Giao hoán:** $a + b = b + a$.")
                        st.markdown(r"> *Ví dụ:* $28 + 34 = 34 + 28 = 62$.")
                        
                        st.write(r"- **Kết hợp:** $(a + b) + c = a + (b + c)$.")
                        st.markdown(r"> *Ví dụ:* $(17 + 21) + 35 = 17 + (21 + 35) = 17 + 56 = 73$.")
                        
                        st.write(r"- **Cộng với 0:** $a + 0 = 0 + a = a$.")
                        
                        st.info(r"""💡 **Mẹo nhỏ (Tính một cách hợp lí):** Khi cộng nhiều số, ta nên dùng tính chất giao hoán và kết hợp để nhóm những số hạng có tổng là số tròn chục, tròn trăm... giúp tính nhẩm nhanh hơn.
                        
**Ví dụ:** Tính $66 + 289 + 134 + 311$
Ta thấy $66+134=200$ và $289+311=600$, nên ta nhóm lại:
$= (66 + 134) + (289 + 311)$
$= 200 + 600 = 800$""")

                        st.markdown("---")
                        st.subheader("2. Phép trừ số tự nhiên")
                        st.write(r"- Với hai số tự nhiên $a, b$ đã cho, nếu có số tự nhiên $c$ sao cho $a = b + c$ thì ta có phép trừ $a - b = c$.")
                        st.latex(r"a \text{ (Số bị trừ)} - b \text{ (Số trừ)} = c \text{ (Hiệu)}")
                        st.markdown(r"> *Ví dụ:* $7 - 4 = 3$ (vì $4 + 3 = 7$).")
                        
                        st.warning(r"""🚨 **Chú ý:** Trong tập hợp $\mathbb{N}$, phép trừ $a - b$ chỉ thực hiện được nếu $a \ge b$.
                        
**Ví dụ:** Ta thực hiện được $7 - 4 = 3$ (vì $7 \ge 4$). Nhưng ta **không thể** thực hiện phép trừ $7 - 8$ trong tập hợp số tự nhiên (vì $7 < 8$).""")

                        # ==========================================
                        # PHẦN THỬ THÁCH TƯƠNG TÁC
                        # ==========================================
                        st.markdown("---")
                        st.subheader("🎯 Thử thách Luyện tập & Vận dụng")
                        
                        st.success("📝 **Thử thách 1 (Bài toán đi chợ):** Bạn Mai đi chợ mua cà tím hết 18 nghìn đồng, cà chua hết 21 nghìn đồng và rau cải hết 30 nghìn đồng. Mai đưa cho cô bán hàng tờ 100 nghìn đồng thì được trả lại bao nhiêu tiền?")
                        tt1 = st.radio("Em hãy chọn số tiền cô bán hàng trả lại Mai:", [
                            "Chưa chọn",
                            "21 nghìn đồng",
                            "31 nghìn đồng",
                            "41 nghìn đồng"
                        ], key="b4_tt1")
                        
                        if tt1 == "31 nghìn đồng":
                            st.success(r"🎉 Rất xuất sắc! Tổng tiền Mai mua đồ là: $18 + 21 + 30 = 69$ (nghìn đồng). Số tiền được trả lại là: $100 - 69 = 31$ (nghìn đồng).")
                        elif tt1 != "Chưa chọn":
                            st.error("❌ Chưa đúng rồi! Em hãy tính tổng số tiền Mai đã mua trước, sau đó lấy 100 trừ đi tổng đó nhé.")

                        st.info(r"📝 **Thử thách 2 (Tính hợp lí):** Hãy tính một cách hợp lí biểu thức sau: $117 + 68 + 23$.")
                        tt2 = st.radio("Kết quả của biểu thức là:", [
                            "Chưa chọn", 
                            "208", 
                            "198",
                            "218"
                        ], key="b4_tt2")
                        
                        if tt2 == "208":
                            st.success(r"🎉 Chính xác! Áp dụng tính chất giao hoán và kết hợp: $(117 + 23) + 68 = 140 + 68 = 208$.")
                        elif tt2 != "Chưa chọn":
                            st.error(r"❌ Em tính lại nhé. Mẹo nhỏ: Hãy nhóm số $117$ và $23$ lại với nhau trước vì $7 + 3 = 10$.")

                    with tab_bai_tap:
                        st.subheader("✍️ Đánh giá năng lực - Bài 4")
                        st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA BÀI TIẾP THEO:** Em cần đạt tối thiểu **7.0/10 điểm** trong bài kiểm tra này.")
                        
                        with st.form("quiz_bai_4"):
                            st.markdown("### I. Mức độ Nhận biết (3 điểm)")
                            
                            st.markdown(r"**Câu 1:** Trong phép trừ $a - b = c$, số $a$ được gọi là gì?")
                            q1 = st.radio("Đáp án Câu 1:", ["-- Chọn --", "Số bị trừ", "Số trừ", "Hiệu", "Số hạng"], key="b4_q1")
                            
                            st.markdown(r"**Câu 2:** Tính chất $(a + b) + c = a + (b + c)$ gọi là tính chất gì của phép cộng?")
                            q2 = st.radio("Đáp án Câu 2:", ["-- Chọn --", "Tính chất giao hoán", "Tính chất kết hợp", "Tính chất phân phối", "Cộng với 0"], key="b4_q2")
                            
                            st.markdown(r"**Câu 3:** Điều kiện để thực hiện được phép trừ $a - b$ trong tập hợp các số tự nhiên $\mathbb{N}$ là gì?")
                            q3 = st.radio("Đáp án Câu 3:", ["-- Chọn --", r"$a > b$", r"$a < b$", r"$a \ge b$", r"$a \le b$"], key="b4_q3")
                            
                            st.markdown("---")
                            st.markdown("### II. Mức độ Thông hiểu (4 điểm)")
                            
                            st.markdown(r"**Câu 4:** Kết quả của phép tính $63~548 + 19~256$ là:")
                            q4 = st.radio("Đáp án Câu 4:", ["-- Chọn --", "82 704", "82 804", "83 804", "81 804"], key="b4_q4")
                            
                            st.markdown(r"**Câu 5:** Kết quả của phép tính $129~107 - 34~693$ là:")
                            q5 = st.radio("Đáp án Câu 5:", ["-- Chọn --", "94 414", "95 414", "94 514", "93 414"], key="b4_q5")
                            
                            st.markdown(r"**Câu 6:** Thay \"?\" bằng số thích hợp: $? + 2~895 = 2~895 + 6~789$.")
                            q6 = st.radio("Đáp án Câu 6:", ["-- Chọn --", "2 895", "9 684", "6 789", "0"], key="b4_q6")
                            
                            st.markdown(r"**Câu 7:** Tính một cách hợp lí: $285 + 470 + 115 + 230$.")
                            q7 = st.radio("Đáp án Câu 7:", ["-- Chọn --", "1 000", "1 100", "1 200", "1 150"], key="b4_q7")
                            
                            st.markdown("---")
                            st.markdown("### III. Mức độ Vận dụng (3 điểm)")
                            
                            st.markdown(r"**Câu 8:** Tìm số tự nhiên $x$ thoả mãn: $7 + x = 362$.")
                            q8 = st.radio("Đáp án Câu 8:", ["-- Chọn --", "369", "350", "355", "357"], key="b4_q8")
                            
                            st.markdown(r"**Câu 9:** Dân số Việt Nam năm 2019 là 96 462 106 người. Năm 2020, dân số Việt Nam tăng 876 473 người so với năm 2019. Tính dân số Việt Nam năm 2020.")
                            q9 = st.radio("Đáp án Câu 9:", ["-- Chọn --", "97 338 579 người", "95 585 633 người", "97 438 579 người", "96 338 579 người"], key="b4_q9")
                            
                            st.markdown(r"**Câu 10:** Nhà ga số 1 và nhà ga số 2 của một sân bay có thể tiếp nhận tương ứng 6 526 300 và 3 514 500 lượt hành khách mỗi năm. Nhờ đưa vào sử dụng nhà ga số 3 mà mỗi năm sân bay có thể tiếp nhận 22 851 200 lượt khách. Tính số lượt khách ga số 3 có thể tiếp nhận?")
                            q10 = st.radio("Đáp án Câu 10:", ["-- Chọn --", "10 040 800 lượt", "12 810 400 lượt", "32 892 000 lượt", "13 810 400 lượt"], key="b4_q10")
                            
                            submit_b4 = st.form_submit_button("Lưu & Nộp bài")
                            
                        if submit_b4:
                            diem = 0
                            if q1 == "Số bị trừ": diem += 1
                            if q2 == "Tính chất kết hợp": diem += 1
                            if q3 == r"$a \ge b$": diem += 1
                            if q4 == "82 804": diem += 1
                            if q5 == "94 414": diem += 1
                            if q6 == "6 789": diem += 1
                            if q7 == "1 100": diem += 1
                            if q8 == "355": diem += 1
                            if q9 == "97 338 579 người": diem += 1
                            if q10 == "12 810 400 lượt": diem += 1
                            
                            if diem >= 7:
                                st.success(f"🎉 RẤT XUẤT SẮC! Em đạt **{diem}/10** điểm. Em đã chinh phục thành công Bài 4!")
                                st.balloons()
                                
                                # GHI LÊN SHEET NẾU HỌC SINH CHƯA PASS BÀI 4
                                if not st.session_state.get("hoan_thanh_bai_4", False):
                                    st.session_state.hoan_thanh_bai_4 = True
                                    current_user = st.session_state.current_user
                                    user_idx = user_df[user_df.iloc[:, 2].astype(str).str.strip() == current_user].index
                                    
                                    if not user_idx.empty:
                                        tien_do_cu = str(user_df.loc[user_idx[0], user_df.columns[4]])
                                        if "Pass_Bai_4" not in tien_do_cu:
                                            tien_do_moi = tien_do_cu + ", Pass_Bai_4" if tien_do_cu.strip() and tien_do_cu != "nan" else "Pass_Bai_4"
                                            
                                            # Cập nhật vào df trong bộ nhớ
                                            user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                            
                                            try:
                                                import gspread
                                                kh = st.secrets["connections"]["gsheets"]
                                                creds = {
                                                    "type": kh["type"],
                                                    "project_id": kh["project_id"],
                                                    "private_key_id": kh["private_key_id"],
                                                    "private_key": kh["private_key"],
                                                    "client_email": kh["client_email"],
                                                    "client_id": kh["client_id"],
                                                    "auth_uri": kh["auth_uri"],
                                                    "token_uri": kh["token_uri"],
                                                    "auth_provider_x509_cert_url": kh["auth_provider_x509_cert_url"],
                                                    "client_x509_cert_url": kh["client_x509_cert_url"]
                                                }
                                                gc = gspread.service_account_from_dict(creds)
                                                sheet_goc = gc.open_by_url(kh["spreadsheet"]).worksheet("Câu trả lời biểu mẫu 1")
                                                
                                                dong_sheet = int(user_idx[0]) + 2 
                                                o_can_ghi = f"E{dong_sheet}" 
                                                sheet_goc.update_acell(o_can_ghi, tien_do_moi)
                                                
                                                st.cache_data.clear()
                                            except Exception as e:
                                                st.error(f"❌ Lỗi ghi dữ liệu: {e}")
                            else:
                                st.error(f"⚠️ Em mới đạt **{diem}/10** điểm. Chưa đủ 7.0 điểm để qua cửa rồi. Hãy ôn lại bài và làm lại nhé!")
                                st.session_state.hoan_thanh_bai_4 = False

                    with tab_mo_rong:
                        st.subheader("💡 Em có biết?")
                        st.write("Ngày xưa, trước khi có máy tính và điện thoại thông minh, con người đã phát minh ra **Bàn tính gảy** (như bàn tính Soroban của Nhật Bản hay Suanpan của Trung Quốc) để thực hiện các phép cộng trừ những con số lên tới hàng triệu một cách nhanh chóng và chính xác như máy vi tính đấy!")
            
                else:
                    st.warning("🔒 **BÀI HỌC BỊ KHÓA**")
                    st.info("Em cần quay lại **Bài 3. Thứ tự trong tập hợp các số tự nhiên** và hoàn thành bài Đánh giá năng lực (đạt từ 7.0 điểm trở lên) để mở khóa bài học này nhé!")
            # ---------------- BÀI 5 ----------------
            elif bai_hoc_selection == "Bài 5. Phép nhân và phép chia số tự nhiên":
                if st.session_state.get("hoan_thanh_bai_4", False) == True:
                    st.header("BÀI 5: PHÉP NHÂN VÀ PHÉP CHIA SỐ TỰ NHIÊN")
                    
                    tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                    
                    with tab_ly_thuyet:
                        st.markdown("**🎥 Video bài giảng trực tuyến**")
                        st.video("https://youtu.be/oB12eNdEpHQ") # Thầy thay link YouTube vào đây nhé
                        st.markdown("---")
                        
                        st.subheader("1. Phép nhân số tự nhiên")
                        st.write(r"- Phép nhân hai số tự nhiên $a$ và $b$ cho ta một số tự nhiên gọi là tích của $a$ và $b$, kí hiệu là $a \times b$ hoặc $a \cdot b$.")
                        st.latex(r"a \text{ (Thừa số)} \cdot b \text{ (Thừa số)} = c \text{ (Tích)}")
                        st.info(r"💡 **Chú ý:** Nếu các thừa số đều bằng chữ, hoặc chỉ có một thừa số bằng số thì ta có thể không viết dấu nhân. Ví dụ: $a \cdot b = ab$; $2 \cdot m = 2m$.")
                        
                        st.write("**Tính chất của phép nhân:**")
                        st.write(r"- **Giao hoán:** $ab = ba$.")
                        st.write(r"- **Kết hợp:** $(ab)c = a(bc)$.")
                        st.write(r"- **Phân phối đối với phép cộng:** $a(b + c) = ab + ac$.")
                        st.write(r"- **Đặc biệt:** $a \cdot 1 = a$; $a \cdot 0 = 0$.")
                        
                        st.warning(r"""🚀 **Mẹo tính nhẩm (Thường dùng):** $2 \cdot 5 = 10$
                        $4 \cdot 25 = 100$
                        $8 \cdot 125 = 1000$
                        
> *Ví dụ tính hợp lí:* $24 \cdot 25 = (6 \cdot 4) \cdot 25 = 6 \cdot (4 \cdot 25) = 6 \cdot 100 = 600$""")

                        st.markdown("---")
                        st.subheader("2. Phép chia hết và phép chia có dư")
                        st.write(r"- Với hai số tự nhiên $a$ và $b$ đã cho ($b \ne 0$), ta luôn tìm được đúng hai số tự nhiên $q$ và $r$ sao cho:")
                        st.latex(r"a = b \cdot q + r \quad (0 \le r < b)")
                        st.write(r"Trong đó: $a$ (Số bị chia), $b$ (Số chia), $q$ (Thương), $r$ (Số dư).")
                        
                        st.write(r"- **Phép chia hết:** Nếu $r = 0$, ta có $a : b = q$.")
                        st.markdown(r"> *Ví dụ:* $196 : 7 = 28$ (dư 0).")
                        
                        st.write(r"- **Phép chia có dư:** Nếu $r \ne 0$, ta có $a : b = q$ (dư $r$).")
                        st.markdown(r"> *Ví dụ:* $215 : 18 = 11$ (dư 17).")
                        st.error(r"🚨 **Lưu ý quan trọng:** Trong phép chia có dư, **số dư bao giờ cũng nhỏ hơn số chia** ($r < b$).")

                        # ==========================================
                        # PHẦN THỬ THÁCH TƯƠNG TÁC
                        # ==========================================
                        st.markdown("---")
                        st.subheader("🎯 Thử thách Luyện tập & Vận dụng")
                        
                        st.success("📝 **Thử thách 1 (Bài toán mua gạo):** Mẹ em mua một túi 10 kg gạo ngon loại 20 nghìn đồng một kilôgam. Hỏi mẹ em phải đưa cho cô bán hàng bao nhiêu tờ 50 nghìn đồng để trả tiền gạo?")
                        tt1 = st.radio("Lựa chọn của em:", [
                            "Chưa chọn",
                            "2 tờ",
                            "4 tờ",
                            "5 tờ"
                        ], key="b5_tt1")
                        
                        if tt1 == "4 tờ":
                            st.success(r"🎉 Chính xác! Số tiền mua gạo là: $10 \cdot 20 = 200$ (nghìn đồng). Số tờ 50 nghìn cần đưa là: $200 : 50 = 4$ (tờ).")
                        elif tt1 != "Chưa chọn":
                            st.error("❌ Em hãy tính tổng số tiền mua gạo trước (10 kg x 20 nghìn), sau đó chia cho 50 nghìn nhé!")

                        st.info(r"📝 **Thử thách 2 (Xếp xe ô tô):** Phải dùng ít nhất bao nhiêu xe ô tô 45 chỗ ngồi để chở hết 487 cổ động viên của một đội bóng?")
                        tt2 = st.radio("Số xe ô tô cần dùng ít nhất là:", [
                            "Chưa chọn", 
                            "10 xe", 
                            "11 xe",
                            "12 xe"
                        ], key="b5_tt2")
                        
                        if tt2 == "11 xe":
                            st.success(r"🎉 Rất thông minh! Ta có $487 : 45 = 10$ (dư 37). Xếp đủ 10 xe thì còn thừa 37 người, nên bắt buộc phải dùng thêm 1 xe nữa. Tổng cộng là 11 xe.")
                        elif tt2 != "Chưa chọn":
                            st.error(r"❌ Em tính lại nhé! $487 : 45$ dư bao nhiêu người? Những người dư ra đó cũng cần xe để đi mà đúng không?")

                    with tab_bai_tap:
                        st.subheader("✍️ Đánh giá năng lực - Bài 5")
                        st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA BÀI 6:** Em cần đạt tối thiểu **7.0/10 điểm** trong bài kiểm tra này.")
                        
                        with st.form("quiz_bai_5"):
                            st.markdown("### I. Mức độ Nhận biết (3 điểm)")
                            
                            st.markdown(r"**Câu 1:** Trong phép nhân $a \cdot b = c$, $a$ và $b$ được gọi là gì?")
                            q1 = st.radio("Đáp án Câu 1:", ["-- Chọn --", "Số hạng", "Thừa số", "Tích", "Thương"], key="b5_q1")
                            
                            st.markdown(r"**Câu 2:** Tính chất $a(b + c) = ab + ac$ được gọi là tính chất gì?")
                            q2 = st.radio("Đáp án Câu 2:", ["-- Chọn --", "Giao hoán", "Kết hợp", "Phân phối của phép nhân đối với phép cộng", "Giao hoán của phép nhân"], key="b5_q2")
                            
                            st.markdown(r"**Câu 3:** Trong phép chia có dư $a = b \cdot q + r$ ($b \ne 0$), số dư $r$ phải thoả mãn điều kiện nào?")
                            q3 = st.radio("Đáp án Câu 3:", ["-- Chọn --", r"$0 \le r < b$", r"$r = b$", r"$r > b$", r"$0 < r < b$"], key="b5_q3")
                            
                            st.markdown("---")
                            st.markdown("### II. Mức độ Thông hiểu (4 điểm)")
                            
                            st.markdown(r"**Câu 4:** Kết quả của phép tính hợp lí $125 \cdot 8001 \cdot 8$ là:")
                            q4 = st.radio("Đáp án Câu 4:", ["-- Chọn --", "8 001 000", "8 000 100", "1 000 000", "8 010 000"], key="b5_q4")
                            
                            st.markdown(r"**Câu 5:** Để tính nhẩm $125 \cdot 101$, cách phân tích nào sau đây là đúng?")
                            q5 = st.radio("Đáp án Câu 5:", ["-- Chọn --", r"$125 \cdot (100 - 1)$", r"$125 \cdot (100 + 1)$", r"$125 \cdot 100 + 1$", r"$125 + 100 \cdot 1$"], key="b5_q5")
                            
                            st.markdown(r"**Câu 6:** Kết quả của phép chia $1~092 : 91$ là:")
                            q6 = st.radio("Đáp án Câu 6:", ["-- Chọn --", "12 (dư 0)", "11 (dư 1)", "12 (dư 2)", "13"], key="b5_q6")
                            
                            st.markdown(r"**Câu 7:** Phép chia $2~059 : 17$ có số dư là bao nhiêu?")
                            q7 = st.radio("Đáp án Câu 7:", ["-- Chọn --", "1", "2", "3", "0"], key="b5_q7")
                            
                            st.markdown("---")
                            st.markdown("### III. Mức độ Vận dụng (3 điểm)")
                            
                            st.markdown(r"**Câu 8:** Một trường THCS có 50 phòng học, mỗi phòng có 11 bộ bàn ghế, mỗi bộ bàn ghế có thể xếp cho 4 học sinh ngồi. Trường có thể nhận nhiều nhất bao nhiêu học sinh?")
                            q8 = st.radio("Đáp án Câu 8:", ["-- Chọn --", "2 000 học sinh", "2 200 học sinh", "2 400 học sinh", "2 500 học sinh"], key="b5_q8")
                            
                            st.markdown(r"**Câu 9:** Một trường có 997 học sinh dự lễ tổng kết. Ban tổ chức chuẩn bị ghế băng 5 chỗ ngồi. Cần ít nhất bao nhiêu ghế băng để tất cả đều có chỗ ngồi?")
                            q9 = st.radio("Đáp án Câu 9:", ["-- Chọn --", "199 ghế", "200 ghế", "198 ghế", "201 ghế"], key="b5_q9")
                            
                            st.markdown(r"**Câu 10:** Một nhà máy dùng ô tô chuyển 1 290 kiện hàng. Nếu mỗi xe chở được 45 kiện thì phải cần ít nhất bao nhiêu chuyến xe để chở hết hàng?")
                            q10 = st.radio("Đáp án Câu 10:", ["-- Chọn --", "28 chuyến", "29 chuyến", "30 chuyến", "31 chuyến"], key="b5_q10")
                            
                            submit_b5 = st.form_submit_button("Lưu & Nộp bài")
                            
                        if submit_b5:
                            diem = 0
                            if q1 == "Thừa số": diem += 1
                            if q2 == "Phân phối của phép nhân đối với phép cộng": diem += 1
                            if q3 == r"$0 \le r < b$": diem += 1
                            if q4 == "8 001 000": diem += 1
                            if q5 == r"$125 \cdot (100 + 1)$": diem += 1
                            if q6 == "12 (dư 0)": diem += 1
                            if q7 == "2": diem += 1
                            if q8 == "2 200 học sinh": diem += 1
                            if q9 == "200 ghế": diem += 1
                            if q10 == "29 chuyến": diem += 1
                            
                            if diem >= 7:
                                st.success(f"🎉 RẤT XUẤT SẮC! Em đạt **{diem}/10** điểm. Em đã chinh phục thành công Bài 5!")
                                st.balloons()
                                
                                # GHI LÊN SHEET NẾU HỌC SINH CHƯA PASS BÀI 5
                                if not st.session_state.get("hoan_thanh_bai_5", False):
                                    st.session_state.hoan_thanh_bai_5 = True
                                    current_user = st.session_state.current_user
                                    user_idx = user_df[user_df.iloc[:, 2].astype(str).str.strip() == current_user].index
                                    
                                    if not user_idx.empty:
                                        tien_do_cu = str(user_df.loc[user_idx[0], user_df.columns[4]])
                                        if "Pass_Bai_5" not in tien_do_cu:
                                            tien_do_moi = tien_do_cu + ", Pass_Bai_5" if tien_do_cu.strip() and tien_do_cu != "nan" else "Pass_Bai_5"
                                            
                                            user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                            
                                            try:
                                                import gspread
                                                kh = st.secrets["connections"]["gsheets"]
                                                creds = {
                                                    "type": kh["type"],
                                                    "project_id": kh["project_id"],
                                                    "private_key_id": kh["private_key_id"],
                                                    "private_key": kh["private_key"],
                                                    "client_email": kh["client_email"],
                                                    "client_id": kh["client_id"],
                                                    "auth_uri": kh["auth_uri"],
                                                    "token_uri": kh["token_uri"],
                                                    "auth_provider_x509_cert_url": kh["auth_provider_x509_cert_url"],
                                                    "client_x509_cert_url": kh["client_x509_cert_url"]
                                                }
                                                gc = gspread.service_account_from_dict(creds)
                                                sheet_goc = gc.open_by_url(kh["spreadsheet"]).worksheet("Câu trả lời biểu mẫu 1")
                                                
                                                dong_sheet = int(user_idx[0]) + 2 
                                                o_can_ghi = f"E{dong_sheet}" 
                                                sheet_goc.update_acell(o_can_ghi, tien_do_moi)
                                                
                                                st.cache_data.clear()
                                            except Exception as e:
                                                st.error(f"❌ Lỗi ghi dữ liệu: {e}")
                            else:
                                st.error(f"⚠️ Em mới đạt **{diem}/10** điểm. Chưa đủ 7.0 điểm để qua cửa rồi. Hãy ôn lại bài và làm lại nhé!")
                                st.session_state.hoan_thanh_bai_5 = False

                    with tab_mo_rong:
                        st.subheader("💡 Em có biết: Tên gọi \"Dấu nhân\" bắt nguồn từ đâu?")
                        st.write("Dấu nhân ($\times$) được nhà toán học người Anh William Oughtred sử dụng lần đầu tiên vào năm 1631. Sau đó, để tránh nhầm lẫn với chữ cái $x$ trong đại số, nhà toán học người Đức Gottfried Leibniz đã đề xuất sử dụng dấu chấm ($\cdot$) để thay thế. Ngày nay, chúng ta sử dụng cả hai kí hiệu này!")

                else:
                    st.warning("🔒 **BÀI HỌC BỊ KHÓA**")
                    st.info("Em cần quay lại **Bài 4. Phép cộng và phép trừ số tự nhiên** và hoàn thành bài Đánh giá năng lực (đạt từ 7.0 điểm trở lên) để mở khóa bài học này nhé!")
           
            # ---------------- LUYỆN TẬP CHUNG ----------------
            elif bai_hoc_selection == "Luyện tập chung":
                if st.session_state.get("hoan_thanh_bai_5", False) == True:
                    st.header("LUYỆN TẬP CHUNG (TỪ BÀI 1 ĐẾN BÀI 5)")
                    
                    tab_ly_thuyet, tab_bai_tap = st.tabs(["📚 Ôn tập lý thuyết", "⏳ Bài kiểm tra (90 phút)"])
                    
                    with tab_ly_thuyet:
                        st.subheader("Bảng tóm tắt kiến thức trọng tâm")
                        st.markdown(r"""
**1. Tập hợp và Phần tử:**
- Kí hiệu thuộc ($\in$), không thuộc ($\notin$).
- Tập hợp số tự nhiên: $\mathbb{N} = \{0; 1; 2; \dots\}$
- Tập hợp số tự nhiên khác 0: $\mathbb{N}^* = \{1; 2; 3; \dots\}$
- Hai cách mô tả: Liệt kê các phần tử và Nêu dấu hiệu đặc trưng.

**2. Cách ghi số tự nhiên:**
- Hệ thập phân: Cứ 10 đơn vị ở một hàng thì làm thành 1 đơn vị ở hàng liền trước nó.
- Chữ số La Mã: Dùng các kí tự $I (1), V (5), X (10)...$ để ghi số.

**3. Thứ tự trong tập hợp số tự nhiên:**
- Mỗi điểm trên tia số biểu diễn một số. Điểm bên trái luôn nhỏ hơn điểm bên phải.
- Tính chất bắc cầu: Nếu $a < b$ và $b < c$ thì $a < c$.

**4. Phép cộng và Phép trừ:**
- Phép cộng: Giao hoán ($a+b=b+a$), Kết hợp ($(a+b)+c = a+(b+c)$).
- Phép trừ $a - b$: Chỉ thực hiện được trong $\mathbb{N}$ khi Số bị trừ $\ge$ Số trừ ($a \ge b$).

**5. Phép nhân và Phép chia:**
- Phép nhân: Phân phối đối với phép cộng ($a(b+c) = ab+ac$).
- Phép chia có dư: $a = b \cdot q + r$ (với điều kiện $0 \le r < b$). Nếu $r=0$ là phép chia hết.
                        """)
                        
                    with tab_bai_tap:
                        st.subheader("Đánh giá tổng hợp năng lực")
                        st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA BÀI 6:** Em cần hoàn thành bài thi trong 90 phút và đạt tối thiểu **7.0/10 điểm** (Đúng 35/50 câu).")
                        
                        # --- CÔNG TẮC: NÚT BẮT ĐẦU LÀM BÀI ---
                        if not st.session_state.get("bat_dau_ltc", False):
                            st.warning("⚠️ **Lưu ý:** Bài thi có giới hạn thời gian 90 phút. Đồng hồ sẽ bắt đầu đếm ngược ngay khi em bấm nút. Hãy chuẩn bị sẵn sàng giấy nháp và bút nhé!")
                            
                            # Nút bấm to, màu nổi bật
                            if st.button("🚀 BẮT ĐẦU LÀM BÀI", type="primary", use_container_width=True):
                                st.session_state.bat_dau_ltc = True
                                st.rerun() # Tải lại trang để hiện câu hỏi
                        else:
                            # --- NẾU ĐÃ BẤM NÚT, HIỂN THỊ ĐỒNG HỒ VÀ CÂU HỎI ---
                            
                            # Tích hợp đồng hồ đếm ngược bằng Javascript (Không bị reset khi click)
                            timer_html = """
                            <div id="clock" style="font-size: 24px; font-weight: bold; color: #D32F2F; text-align: center; padding: 10px; border: 2px dashed #D32F2F; border-radius: 10px; background-color: #ffebee;">
                                Đang tải đồng hồ...
                            </div>
                            <script>
                                var timerKey = "countdown_timer_ltc";
                                var timeLimit = 90 * 60; 
                                var storedTime = sessionStorage.getItem(timerKey);
                                var timeRemaining = storedTime ? parseInt(storedTime) : timeLimit;

                                var x = setInterval(function() {
                                    timeRemaining--;
                                    sessionStorage.setItem(timerKey, timeRemaining);
                                    var minutes = Math.floor(timeRemaining / 60);
                                    var seconds = timeRemaining % 60;
                                    document.getElementById("clock").innerHTML = "⏳ THỜI GIAN CÒN LẠI: " + minutes + " phút " + (seconds < 10 ? "0" : "") + seconds + " giây";
                                    if (timeRemaining < 0) {
                                        clearInterval(x);
                                        document.getElementById("clock").innerHTML = "🚨 ĐÃ HẾT GIỜ LÀM BÀI!";
                                    }
                                }, 1000);
                            </script>
                            """
                            st.components.v1.html(timer_html, height=70)
                            
                            # --- KHO DỮ LIỆU CÂU HỎI ---
                            cau_hoi_mcq = [
                                # 15 Câu Nhận biết
                                {"q": r"**Câu 1 (NB):** Kí hiệu của tập hợp các số tự nhiên là gì?", "opts": [r"$\mathbb{N}^*$", r"$\mathbb{N}$", r"$\mathbb{Z}$", r"$\mathbb{Q}$"], "ans": r"$\mathbb{N}$"},
                                {"q": r"**Câu 2 (NB):** Kí hiệu của tập hợp các số tự nhiên khác 0 là?", "opts": [r"$\mathbb{N}^*$", r"$\mathbb{N}$", r"$\mathbb{Z}$", r"$\mathbb{Q}$"], "ans": r"$\mathbb{N}^*$"},
                                {"q": r"**Câu 3 (NB):** Để chỉ $a$ là một phần tử của tập hợp $A$, ta dùng kí hiệu nào?", "opts": [r"$\notin$", r"$\subset$", r"$=$", r"$\in$"], "ans": r"$\in$"},
                                {"q": r"**Câu 4 (NB):** Số tự nhiên liền sau của số 99 là:", "opts": ["98", "100", "990", "101"], "ans": "100"},
                                {"q": r"**Câu 5 (NB):** Số tự nhiên liền trước của số 1 là:", "opts": ["0", "2", "Không có", "10"], "ans": "0"},
                                {"q": r"**Câu 6 (NB):** Trong hệ thập phân, chữ số 5 trong số 254 có giá trị là:", "opts": ["5", "50", "500", "54"], "ans": "50"},
                                {"q": r"**Câu 7 (NB):** Kí hiệu La Mã $V$ có giá trị trong hệ thập phân là:", "opts": ["1", "5", "10", "50"], "ans": "5"},
                                {"q": r"**Câu 8 (NB):** Trong phép trừ $a - b = c$, số $a$ được gọi là:", "opts": ["Số trừ", "Hiệu", "Số bị trừ", "Số hạng"], "ans": "Số bị trừ"},
                                {"q": r"**Câu 9 (NB):** Trong phép nhân $a \cdot b = c$, số $b$ được gọi là:", "opts": ["Thương", "Tích", "Thừa số", "Số hạng"], "ans": "Thừa số"},
                                {"q": r"**Câu 10 (NB):** Phép cộng số tự nhiên KHÔNG có tính chất nào sau đây?", "opts": ["Giao hoán", "Kết hợp", "Cộng với 0", "Phân phối"], "ans": "Phân phối"},
                                {"q": r"**Câu 11 (NB):** Điều kiện để thực hiện được phép trừ $a - b$ trong tập $\mathbb{N}$ là:", "opts": [r"$a > b$", r"$a < b$", r"$a \ge b$", r"$a \ne b$"], "ans": r"$a \ge b$"},
                                {"q": r"**Câu 12 (NB):** Trong phép chia có dư $a = b \cdot q + r$ ($b \ne 0$), số dư $r$ phải thỏa mãn:", "opts": [r"$r < b$", r"$0 \le r < b$", r"$r = 0$", r"$r > b$"], "ans": r"$0 \le r < b$"},
                                {"q": r"**Câu 13 (NB):** Phép chia có số dư $r = 0$ được gọi là:", "opts": ["Phép chia có dư", "Phép chia hết", "Phép chia vô nghiệm", "Phép nhân"], "ans": "Phép chia hết"},
                                {"q": r"**Câu 14 (NB):** Có bao nhiêu cách để mô tả một tập hợp?", "opts": ["1 cách", "2 cách", "3 cách", "4 cách"], "ans": "2 cách"},
                                {"q": r"**Câu 15 (NB):** Điểm $a$ nằm bên trái điểm $b$ trên tia số thì:", "opts": [r"$a > b$", r"$a = b$", r"$a < b$", r"$a \ge b$"], "ans": r"$a < b$"},
                                
                                # 20 Câu Thông hiểu
                                {"q": r"**Câu 16 (TH):** Viết tập hợp $A = \{x \in \mathbb{N} \mid x < 3\}$ bằng cách liệt kê:", "opts": [r"$\{1; 2\}$", r"$\{0; 1; 2; 3\}$", r"$\{0; 1; 2\}$", r"$\{1; 2; 3\}$"], "ans": r"$\{0; 1; 2\}$"},
                                {"q": r"**Câu 17 (TH):** Số phần tử của tập hợp $M = \{2; 4; 6; 8\}$ là:", "opts": ["2", "4", "6", "8"], "ans": "4"},
                                {"q": r"**Câu 18 (TH):** Số La Mã $XIV$ biểu diễn số tự nhiên nào?", "opts": ["16", "14", "15", "9"], "ans": "14"},
                                {"q": r"**Câu 19 (TH):** Viết số 24 bằng chữ số La Mã:", "opts": ["XXIV", "XIV", "XXVI", "XXIIII"], "ans": "XXIV"},
                                {"q": r"**Câu 20 (TH):** So sánh hai số 2025 và 2052:", "opts": ["2025 > 2052", "2025 < 2052", "2025 = 2052", "Không so sánh được"], "ans": "2025 < 2052"},
                                {"q": r"**Câu 21 (TH):** Kết quả của phép tính $45 + 55$ là:", "opts": ["90", "100", "110", "105"], "ans": "100"},
                                {"q": r"**Câu 22 (TH):** Kết quả của phép tính $125 - 34$ là:", "opts": ["91", "101", "81", "90"], "ans": "91"},
                                {"q": r"**Câu 23 (TH):** Kết quả của phép tính $15 \cdot 4$ là:", "opts": ["50", "60", "70", "45"], "ans": "60"},
                                {"q": r"**Câu 24 (TH):** Kết quả của phép tính $144 : 12$ là:", "opts": ["11", "12", "13", "14"], "ans": "12"},
                                {"q": r"**Câu 25 (TH):** Số dư của phép chia $26 : 5$ là:", "opts": ["0", "1", "2", "3"], "ans": "1"},
                                {"q": r"**Câu 26 (TH):** Tìm $x$ biết: $x + 10 = 25$:", "opts": ["15", "35", "10", "5"], "ans": "15"},
                                {"q": r"**Câu 27 (TH):** Tìm $x$ biết: $20 - x = 5$:", "opts": ["25", "10", "15", "5"], "ans": "15"},
                                {"q": r"**Câu 28 (TH):** Tìm $x$ biết: $3 \cdot x = 18$:", "opts": ["5", "6", "15", "21"], "ans": "6"},
                                {"q": r"**Câu 29 (TH):** Tìm $x$ biết: $x : 4 = 5$:", "opts": ["9", "1", "20", "24"], "ans": "20"},
                                {"q": r"**Câu 30 (TH):** Tính nhẩm $4 \cdot 25 \cdot 7$ ta được:", "opts": ["700", "70", "7000", "100"], "ans": "700"},
                                {"q": r"**Câu 31 (TH):** Tính hợp lí $34 + 56 + 66 + 44$ ta được:", "opts": ["190", "200", "210", "100"], "ans": "200"},
                                {"q": r"**Câu 32 (TH):** Áp dụng tính chất phân phối để tính $5 \cdot 13 + 5 \cdot 7$:", "opts": ["50", "100", "150", "80"], "ans": "100"},
                                {"q": r"**Câu 33 (TH):** Sắp xếp các số $12; 5; 20; 0$ theo thứ tự tăng dần:", "opts": ["0; 5; 12; 20", "20; 12; 5; 0", "0; 12; 5; 20", "5; 0; 12; 20"], "ans": "0; 5; 12; 20"},
                                {"q": r"**Câu 34 (TH):** Tập hợp $M = \{x \in \mathbb{N}^* \mid x \le 3\}$ là:", "opts": [r"$\{0; 1; 2; 3\}$", r"$\{1; 2; 3\}$", r"$\{1; 2\}$", r"$\{0; 1; 2\}$"], "ans": r"$\{1; 2; 3\}$"},
                                {"q": r"**Câu 35 (TH):** Tính: $0 \cdot 2026 + 2026$:", "opts": ["0", "1", "2026", "4052"], "ans": "2026"}
                            ]
                            
                            cau_hoi_tf = [
                                {"q": r"**Câu 36 (VD):** Tập hợp $\mathbb{N}$ và $\mathbb{N}^*$ là hai tập hợp hoàn toàn giống nhau.", "ans": "Sai"},
                                {"q": r"**Câu 37 (VD):** Số 0 là số tự nhiên nhỏ nhất và không có số tự nhiên liền trước.", "ans": "Đúng"},
                                {"q": r"**Câu 38 (VD):** Số 29 được viết bằng chữ số La Mã là $XXIX$.", "ans": "Đúng"},
                                {"q": r"**Câu 39 (VD):** Trong tập hợp số tự nhiên, ta luôn có thể thực hiện được phép chia một số bất kỳ cho 0.", "ans": "Sai"},
                                {"q": r"**Câu 40 (VD):** Biểu thức $15 \cdot (10 - 2) = 15 \cdot 10 - 15 \cdot 2$ là một khẳng định đúng.", "ans": "Đúng"},
                                {"q": r"**Câu 41 (VD):** Trong một phép chia có dư, số dư luôn luôn phải nhỏ hơn số chia.", "ans": "Đúng"},
                                {"q": r"**Câu 42 (VD):** Phép trừ $a - b$ luôn luôn thực hiện được với mọi số tự nhiên $a$ và $b$.", "ans": "Sai"},
                                {"q": r"**Câu 43 (VD):** Số 99 là số tự nhiên lớn nhất có hai chữ số khác nhau.", "ans": "Sai"} # Là 98
                            ]
                            
                            cau_hoi_sa = [
                                {"q": r"**Câu 44 (VD):** Tìm $x$, biết: $(x - 10) \cdot 5 = 25$. (Chỉ nhập số)", "ans": "15"},
                                {"q": r"**Câu 45 (VD):** Tính tổng: $1 + 2 + 3 + \dots + 10 = ?$ (Chỉ nhập số)", "ans": "55"},
                                {"q": r"**Câu 46 (VDC):** Một lớp học có 45 học sinh, mỗi bàn xếp được 4 chỗ ngồi. Cần ít nhất bao nhiêu bàn để tất cả học sinh đều có chỗ ngồi?", "ans": "12"},
                                {"q": r"**Câu 47 (VD):** Mẹ mua 2kg cam (giá 20000đ/kg) và 1kg táo (giá 30000đ/kg). Mẹ phải trả tổng cộng bao nhiêu tiền? (Không nhập chữ đ)", "ans": "70000"},
                                {"q": r"**Câu 48 (VD):** Tìm số tự nhiên nhỏ nhất có ba chữ số khác nhau.", "ans": "102"},
                                {"q": r"**Câu 49 (VD):** Tìm $x$, biết: $100 : (x - 2) = 20$.", "ans": "7"},
                                {"q": r"**Câu 50 (VDC):** Tính nhanh: $25 \cdot 8 \cdot 4 \cdot 125 = ?$ (Chỉ nhập số)", "ans": "100000"}
                            ]

                            # --- VÒNG LẶP IN CÂU HỎI RA MÀN HÌNH ---
                            with st.form("form_luyen_tap_chung"):
                                st.markdown("### Phần 1: Trắc nghiệm Nhiều lựa chọn (35 câu)")
                                for i, cau in enumerate(cau_hoi_mcq):
                                    st.radio(cau["q"], options=["-- Chọn --"] + cau["opts"], key=f"ltc_mcq_{i}")
                                
                                st.markdown("---")
                                st.markdown("### Phần 2: Trắc nghiệm Đúng / Sai (8 câu)")
                                for i, cau in enumerate(cau_hoi_tf):
                                    st.radio(cau["q"], options=["-- Chọn --", "Đúng", "Sai"], key=f"ltc_tf_{i}")
                                    
                                st.markdown("---")
                                st.markdown("### Phần 3: Trắc nghiệm Trả lời ngắn (7 câu)")
                                for i, cau in enumerate(cau_hoi_sa):
                                    st.text_input(cau["q"], placeholder="Nhập đáp án của em vào đây...", key=f"ltc_sa_{i}")
                                
                                st.markdown("---")
                                submit_ltc = st.form_submit_button("Nộp bài thi")
                                
                            # --- LOGIC CHẤM ĐIỂM TỰ ĐỘNG ---
                            if submit_ltc:
                                so_cau_dung = 0
                                
                                # Chấm Phần 1
                                for i, cau in enumerate(cau_hoi_mcq):
                                    if st.session_state.get(f"ltc_mcq_{i}") == cau["ans"]:
                                        so_cau_dung += 1
                                        
                                # Chấm Phần 2
                                for i, cau in enumerate(cau_hoi_tf):
                                    if st.session_state.get(f"ltc_tf_{i}") == cau["ans"]:
                                        so_cau_dung += 1
                                        
                                # Chấm Phần 3
                                for i, cau in enumerate(cau_hoi_sa):
                                    user_ans = str(st.session_state.get(f"ltc_sa_{i}", "")).strip()
                                    if user_ans == cau["ans"]:
                                        so_cau_dung += 1
                                        
                                # Tính điểm thang 10
                                diem_ltc = (so_cau_dung / 50) * 10
                                if diem_ltc >= 7.0:
                                    st.success(f"🎉 RẤT XUẤT SẮC! Em làm đúng **{so_cau_dung}/50** câu. Đạt **{diem_ltc:.1f}/10** điểm. BÀI SỐ 6 ĐÃ ĐƯỢC MỞ KHÓA!")
                                    st.balloons()
                                    
                                    # GHI LÊN SHEET NẾU CHƯA PASS
                                    if not st.session_state.get("hoan_thanh_luyen_tap_chung", False):
                                        st.session_state.hoan_thanh_luyen_tap_chung = True
                                        current_user = st.session_state.current_user
                                        user_idx = user_df[user_df.iloc[:, 2].astype(str).str.strip() == current_user].index
                                        
                                        if not user_idx.empty:
                                            tien_do_cu = str(user_df.loc[user_idx[0], user_df.columns[4]])
                                            if "Pass_LuyenTapChung" not in tien_do_cu:
                                                tien_do_moi = tien_do_cu + ", Pass_LuyenTapChung" if tien_do_cu.strip() and tien_do_cu != "nan" else "Pass_LuyenTapChung"
                                                
                                                user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                                
                                                try:
                                                    import gspread
                                                    kh = st.secrets["connections"]["gsheets"]
                                                    creds = {
                                                        "type": kh["type"],
                                                        "project_id": kh["project_id"],
                                                        "private_key_id": kh["private_key_id"],
                                                        "private_key": kh["private_key"],
                                                        "client_email": kh["client_email"],
                                                        "client_id": kh["client_id"],
                                                        "auth_uri": kh["auth_uri"],
                                                        "token_uri": kh["token_uri"],
                                                        "auth_provider_x509_cert_url": kh["auth_provider_x509_cert_url"],
                                                        "client_x509_cert_url": kh["client_x509_cert_url"]
                                                    }
                                                    gc = gspread.service_account_from_dict(creds)
                                                    sheet_goc = gc.open_by_url(kh["spreadsheet"]).worksheet("Câu trả lời biểu mẫu 1")
                                                    
                                                    dong_sheet = int(user_idx[0]) + 2 
                                                    o_can_ghi = f"E{dong_sheet}" 
                                                    sheet_goc.update_acell(o_can_ghi, tien_do_moi)
                                                    
                                                    st.cache_data.clear()
                                                except Exception as e:
                                                    st.error(f"❌ Lỗi ghi dữ liệu: {e}")
                                else:
                                    st.error(f"⚠️ Em làm đúng **{so_cau_dung}/50** câu (Đạt **{diem_ltc:.1f}/10** điểm). Hãy cố gắng ôn tập và làm lại để đạt 7.0 điểm nhé!")
                                    st.session_state.hoan_thanh_luyen_tap_chung = False

                else:
                    st.warning("🔒 **BÀI LUYỆN TẬP BỊ KHÓA**")
                    st.info("Em cần hoàn thành Bài Đánh giá năng lực của **Bài 5** (đạt từ 7.0 điểm) để mở khóa phần Luyện tập chung này nhé!")
            # ----Bài 6 ---
            elif bai_hoc_selection == "Bài 6. Lũy thừa với số mũ tự nhiên":
                # ĐIỀU KIỆN MỞ KHÓA LÀ PHẢI HOÀN THÀNH BÀI LUYỆN TẬP CHUNG
                if st.session_state.get("hoan_thanh_luyen_tap_chung", False) == True:
                    st.header("BÀI 6: LŨY THỪA VỚI SỐ MŨ TỰ NHIÊN")
                    
                    tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                    
                    with tab_ly_thuyet:
                        st.markdown("**🎥 Video bài giảng trực tuyến**")
                        st.info("*(Thầy cô sẽ cập nhật video bài giảng tại đây)*")
                        st.markdown("---")
                        
                        st.subheader("1. Phép nâng lên lũy thừa")
                        st.write(r"- **Lũy thừa bậc $n$ của số tự nhiên $a$** là tích của $n$ thừa số bằng nhau, mỗi thừa số bằng $a$:")
                        st.latex(r"a^n = \underbrace{a \cdot a \cdot \dots \cdot a}_{n \text{ thừa số}} \quad (n \in \mathbb{N}^*)")
                        st.write(r"- Trong đó: $a$ là **cơ số**, $n$ là **số mũ**.")
                        st.write(r"- $a^n$ đọc là \"$a$ mũ $n$\" hoặc \"$a$ lũy thừa $n$\".")
                        
                        st.markdown(r"> *Ví dụ:* $3 \cdot 3 \cdot 3 \cdot 3 \cdot 3 = 3^5$ (Cơ số là 3, số mũ là 5).")
                        
                        st.warning(r"""🚨 **Quy ước và Tên gọi đặc biệt:**
- $a^1 = a$
- $a^2$ còn gọi là **$a$ bình phương** (hay bình phương của $a$).
- $a^3$ còn gọi là **$a$ lập phương** (hay lập phương của $a$).
- Các số $0, 1, 4, 9, 16...$ (tức là $0^2, 1^2, 2^2, 3^2, 4^2...$) gọi là các **số chính phương**.""")

                        st.markdown("---")
                        st.subheader("2. Nhân và chia hai lũy thừa cùng cơ số")
                        st.write("**a) Nhân hai lũy thừa cùng cơ số**")
                        st.write("- Ta giữ nguyên cơ số và cộng các số mũ:")
                        st.latex(r"a^m \cdot a^n = a^{m+n}")
                        st.markdown(r"> *Ví dụ:* $5^3 \cdot 5^4 = 5^{3+4} = 5^7$")
                        
                        st.write("**b) Chia hai lũy thừa cùng cơ số**")
                        st.write("- Ta giữ nguyên cơ số và lấy số mũ của số bị chia trừ số mũ của số chia:")
                        st.latex(r"a^m : a^n = a^{m-n} \quad (a \ne 0, m \ge n)")
                        st.markdown(r"> *Ví dụ:* $2^6 : 2^3 = 2^{6-3} = 2^3$")
                        
                        st.error(r"💡 **Quy ước bắt buộc phải nhớ:** $a^0 = 1$ (với $a \ne 0$).")

                        # ==========================================
                        # PHẦN THỬ THÁCH TƯƠNG TÁC
                        # ==========================================
                        st.markdown("---")
                        st.subheader("🎯 Thử thách Luyện tập")
                        
                        st.success(r"📝 **Thử thách 1:** Em hãy viết gọn tích sau dưới dạng lũy thừa: $10 \cdot 10 \cdot 10 \cdot 10$")
                        tt1 = st.radio("Đáp án của em là:", [
                            "Chưa chọn",
                            r"$10^3$",
                            r"$10^4$",
                            r"$4^{10}$"
                        ], key="b6_tt1")
                        
                        if tt1 == r"$10^4$":
                            st.success(r"🎉 Chính xác! Tích có 4 thừa số 10 nhân với nhau nên kết quả là $10^4$.")
                        elif tt1 != "Chưa chọn":
                            st.error("❌ Em hãy đếm kĩ xem có bao nhiêu số 10 đang nhân với nhau nhé!")

                        st.info(r"📝 **Thử thách 2:** Cùng tính nhẩm nhanh nào! Giá trị của $11^2$ là bao nhiêu?")
                        tt2 = st.radio("Kết quả là:", [
                            "Chưa chọn", 
                            "22", 
                            "111",
                            "121"
                        ], key="b6_tt2")
                        
                        if tt2 == "121":
                            st.success(r"🎉 Tuyệt vời! $11^2$ (đọc là 11 bình phương) nghĩa là $11 \cdot 11 = 121$.")
                        elif tt2 != "Chưa chọn":
                            st.error(r"❌ Em nhầm rồi! $11^2$ là $11 \cdot 11$, chứ không phải $11 \cdot 2$ đâu nhé.")

                    with tab_bai_tap:
                        st.subheader("✍️ Đánh giá năng lực - Bài 6")
                        st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA BÀI 7:** Em cần đạt tối thiểu **7.0/10 điểm** trong bài kiểm tra này.")

                    with tab_bai_tap:
                        st.subheader("✍️ Đánh giá năng lực - Bài 6")
                        st.info("🔒 **ĐIỀU KIỆN MỞ KHÓA BÀI 7:** Em cần đạt tối thiểu **7.0/10 điểm** trong bài kiểm tra này.")
                        
                        with st.form("quiz_bai_6"):
                            st.markdown("### I. Mức độ Nhận biết (3 điểm)")
                            
                            st.markdown(r"**Câu 1:** Phép nhân nhiều thừa số bằng nhau được gọi là phép toán gì?")
                            q1 = st.radio("Đáp án Câu 1:", ["-- Chọn --", "Phép cộng", "Phép nhân", "Phép nâng lên lũy thừa", "Phép chia"], key="b6_q1")
                            
                            st.markdown(r"**Câu 2:** Trong lũy thừa $a^n$, số $a$ được gọi là gì?")
                            q2 = st.radio("Đáp án Câu 2:", ["-- Chọn --", "Số mũ", "Cơ số", "Số hạng", "Thừa số"], key="b6_q2")
                            
                            st.markdown(r"**Câu 3:** Công thức nhân hai lũy thừa cùng cơ số là:")
                            q3 = st.radio("Đáp án Câu 3:", ["-- Chọn --", r"$a^m \cdot a^n = a^{m \cdot n}$", r"$a^m \cdot a^n = a^{m - n}$", r"$a^m \cdot a^n = a^{m + n}$", r"$a^m \cdot a^n = a^{m : n}$"], key="b6_q3")
                            
                            st.markdown("---")
                            st.markdown("### II. Mức độ Thông hiểu (4 điểm)")
                            
                            st.markdown(r"**Câu 4:** Viết gọn biểu thức $5 \cdot 5 \cdot 5 \cdot 5 \cdot 5$ dưới dạng một lũy thừa là:")
                            q4 = st.radio("Đáp án Câu 4:", ["-- Chọn --", r"$5^5$", r"$5^4$", r"$25^5$", r"$5 \cdot 5$"], key="b6_q4")
                            
                            st.markdown(r"**Câu 5:** Kết quả của phép tính $2^4$ là:")
                            q5 = st.radio("Đáp án Câu 5:", ["-- Chọn --", "8", "16", "6", "32"], key="b6_q5")
                            
                            st.markdown(r"**Câu 6:** Kết quả của phép chia $7^6 : 7^4$ viết dưới dạng lũy thừa là:")
                            q6 = st.radio("Đáp án Câu 6:", ["-- Chọn --", r"$7^{10}$", r"$1^2$", r"$7^2$", r"$7^{24}$"], key="b6_q6")
                            
                            st.markdown(r"**Câu 7:** Quy ước nào sau đây là **ĐÚNG**?")
                            q7 = st.radio("Đáp án Câu 7:", ["-- Chọn --", r"$a^0 = 0$", r"$a^1 = 1$", r"$a^1 = 0$", r"$a^0 = 1 \text{ (với } a \ne 0)$"], key="b6_q7")
                            
                            st.markdown("---")
                            st.markdown("### III. Mức độ Vận dụng (3 điểm)")
                            
                            st.markdown(r"**Câu 8:** Biết $2^{10} = 1024$. Giá trị của $2^9$ là:")
                            q8 = st.radio("Đáp án Câu 8:", ["-- Chọn --", "2048", "512", "1022", "510"], key="b6_q8")
                            
                            st.markdown(r"**Câu 9:** Viết số 2020 thành tổng giá trị các chữ số của nó bằng cách dùng các lũy thừa của 10:")
                            q9 = st.radio("Đáp án Câu 9:", ["-- Chọn --", r"$2 \cdot 10^3 + 2 \cdot 10^2$", r"$2 \cdot 10^3 + 2 \cdot 10$", r"$2 \cdot 10^4 + 2 \cdot 10$", r"$2 \cdot 10^3 + 2$"], key="b6_q9")
                            
                            st.markdown(r"**Câu 10:** Mỗi giây cơ thể người trung bình tạo ra khoảng $25 \cdot 10^5$ tế bào hồng cầu. Hỏi mỗi phút có bao nhiêu tế bào hồng cầu được tạo ra?")
                            q10 = st.radio("Đáp án Câu 10:", ["-- Chọn --", r"$1500 \cdot 10^5 \text{ tế bào}$", r"$150 \cdot 10^5 \text{ tế bào}$", r"$25 \cdot 10^6 \text{ tế bào}$", r"$85 \cdot 10^5 \text{ tế bào}$"], key="b6_q10")
                            
                            submit_b6 = st.form_submit_button("Lưu & Nộp bài")
                            
                        if submit_b6:
                            diem = 0
                            if q1 == "Phép nâng lên lũy thừa": diem += 1
                            if q2 == "Cơ số": diem += 1
                            if q3 == r"$a^m \cdot a^n = a^{m + n}$": diem += 1
                            if q4 == r"$5^5$": diem += 1
                            if q5 == "16": diem += 1
                            if q6 == r"$7^2$": diem += 1
                            if q7 == r"$a^0 = 1 \text{ (với } a \ne 0)$": diem += 1
                            if q8 == "512": diem += 1
                            if q9 == r"$2 \cdot 10^3 + 2 \cdot 10$": diem += 1
                            if q10 == r"$1500 \cdot 10^5 \text{ tế bào}$": diem += 1
                            
                            if diem >= 7:
                                st.success(f"🎉 RẤT XUẤT SẮC! Em đạt **{diem}/10** điểm. Em đã chinh phục thành công Bài 6!")
                                st.balloons()
                                
                                # GHI LÊN SHEET NẾU HỌC SINH CHƯA PASS BÀI 6
                                if not st.session_state.get("hoan_thanh_bai_6", False):
                                    st.session_state.hoan_thanh_bai_6 = True
                                    current_user = st.session_state.current_user
                                    user_idx = user_df[user_df.iloc[:, 2].astype(str).str.strip() == current_user].index
                                    
                                    if not user_idx.empty:
                                        tien_do_cu = str(user_df.loc[user_idx[0], user_df.columns[4]])
                                        if "Pass_Bai_6" not in tien_do_cu:
                                            tien_do_moi = tien_do_cu + ", Pass_Bai_6" if tien_do_cu.strip() and tien_do_cu != "nan" else "Pass_Bai_6"
                                            
                                            user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                            
                                            try:
                                                import gspread
                                                kh = st.secrets["connections"]["gsheets"]
                                                creds = {
                                                    "type": kh["type"],
                                                    "project_id": kh["project_id"],
                                                    "private_key_id": kh["private_key_id"],
                                                    "private_key": kh["private_key"],
                                                    "client_email": kh["client_email"],
                                                    "client_id": kh["client_id"],
                                                    "auth_uri": kh["auth_uri"],
                                                    "token_uri": kh["token_uri"],
                                                    "auth_provider_x509_cert_url": kh["auth_provider_x509_cert_url"],
                                                    "client_x509_cert_url": kh["client_x509_cert_url"]
                                                }
                                                gc = gspread.service_account_from_dict(creds)
                                                sheet_goc = gc.open_by_url(kh["spreadsheet"]).worksheet("Câu trả lời biểu mẫu 1")
                                                
                                                dong_sheet = int(user_idx[0]) + 2 
                                                o_can_ghi = f"E{dong_sheet}" 
                                                sheet_goc.update_acell(o_can_ghi, tien_do_moi)
                                                
                                                st.cache_data.clear()
                                            except Exception as e:
                                                st.error(f"❌ Lỗi ghi dữ liệu: {e}")
                            else:
                                st.error(f"⚠️ Em mới đạt **{diem}/10** điểm. Chưa đủ 7.0 điểm để qua cửa rồi. Hãy ôn lại bài và làm lại nhé!")
                                st.session_state.hoan_thanh_bai_6 = False

                    with tab_mo_rong:
                        st.subheader("💡 Em có biết: Câu chuyện Bàn cờ vua và Hạt thóc?")
                        st.write("Truyền thuyết Ấn Độ kể rằng, người phát minh ra bàn cờ vua đã xin nhà vua phần thưởng như sau: Ô thứ nhất để 1 hạt thóc ($2^0$), ô thứ hai 2 hạt ($2^1$), ô thứ ba 4 hạt ($2^2$)... Cứ như thế, số thóc ở ô sau gấp đôi ô trước cho đến hết 64 ô.")
                        st.write("Nhà vua tưởng phần thưởng này rất nhỏ bé nên đã đồng ý ngay. Nhưng khi các quan tính toán lại, tổng số thóc trên 64 ô cờ là $2^{64} - 1$ hạt thóc. Toàn bộ khối lượng thóc này nặng tới **369 tỉ tấn**! Cả vương quốc gom hết lại cũng không đủ để trả cho ông ta.")
                        st.info("Qua câu chuyện này, em thấy sức mạnh của \"Lũy thừa\" khủng khiếp như thế nào chưa!")
                        
                        st.markdown("---")
                        st.subheader("🎵 Lũy thừa trong... Âm nhạc!")
                        st.write("Trong âm nhạc, độ dài của các nốt nhạc cũng tuân theo quy luật lũy thừa của 2 đấy:")
                        st.write("- 1 nốt tròn = $2^1$ nốt trắng = $2^2$ nốt đen = $2^3$ nốt móc đơn = $2^4$ nốt móc kép.")
          
                else:
                    st.warning("🔒 **BÀI HỌC BỊ KHÓA**")
                    st.info("Hãy hoàn thành Luyện tập chung để mở khóa Bài 6.")
                
    # ---------------- NỘI DUNG TOÁN 7, 8, 9 ----------------
    else:
        st.info("Nội dung bài học đang được thầy cô tiếp tục biên soạn và cập nhật. Các em hãy đón chờ nhé!")
