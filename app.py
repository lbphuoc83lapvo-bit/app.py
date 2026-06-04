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
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    user_df = conn.read(worksheet="Câu trả lời biểu mẫu 1", ttl=0) 
    
    # Lọc bỏ dòng trống
    user_df = user_df.dropna(subset=[user_df.columns[1], user_df.columns[2], user_df.columns[3]], how='all')
    
    # Đảm bảo có đủ 5 cột (thêm cột Tiến độ nếu chưa có)
    while len(user_df.columns) < 5:
        user_df[f"Cột mới {len(user_df.columns)}"] = ""

    if len(user_df.columns) >= 4:
        email_hs = user_df.iloc[:, 1].astype(str).str.strip()
        ten_dang_nhap = user_df.iloc[:, 2].astype(str).str.strip()
        mat_khau = user_df.iloc[:, 3].astype(str).str.strip()
        tien_do = user_df.iloc[:, 4].astype(str).str.strip() # Đọc Cột E (Tiến độ)
        
        user_db = dict(zip(ten_dang_nhap, mat_khau))
        email_db = dict(zip(email_hs, mat_khau))
        progress_db = dict(zip(ten_dang_nhap, tien_do)) # Lưu trữ tiến độ
    else:
        user_db, email_db, progress_db = {}, {}, {}
except Exception as e:
    st.error(f"⚠️ Lỗi kết nối dữ liệu: {e}")
    user_db, email_db, progress_db = {}, {}, {}
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
                "Luyện tập chung (trang 20)",
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
                                        
                                        # CHỈ CẦN THÊM [0] VÀO DÒNG DƯỚI ĐÂY:
                                        user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                        
                                        try:
                                            conn.update(worksheet="Câu trả lời biểu mẫu 1", data=user_df)
                                        except Exception as e:
                                            st.warning("Hệ thống chưa đồng bộ lên Cloud.")
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
                                            
                                            # CHỈ CẦN THÊM [0] VÀO DÒNG DƯỚI ĐÂY:
                                            user_df.loc[user_idx[0], user_df.columns[4]] = tien_do_moi
                                            
                                            try:
                                                conn.update(worksheet="Câu trả lời biểu mẫu 1", data=user_df)
                                            except Exception as e:
                                                st.warning("Hệ thống chưa đồng bộ lên Cloud.")
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

    # ---------------- NỘI DUNG TOÁN 7, 8, 9 ----------------
    else:
        st.info("Nội dung bài học đang được thầy cô tiếp tục biên soạn và cập nhật. Các em hãy đón chờ nhé!")
