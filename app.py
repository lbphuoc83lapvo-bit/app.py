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
                tab_ly_thuyet, tab_bai_tap, tab_mo_rong = st.tabs(["📚 Lý thuyết bài học", "✍️ Luyện tập & Bài tập", "💡 Em có biết?"])
                
                with tab_ly_thuyet:
                    # KHU VỰC VIDEO BÀI GIẢNG
                    st.markdown("**🎥 Video bài giảng trực tuyến**")
                    st.video("https://youtu.be/beV0JRiJLvQ")
                    st.markdown("---")
                    
                    st.subheader("1. Tập hợp và phần tử của tập hợp")
                    st.write("Một **tập hợp** (gọi tắt là **tập**) bao gồm những đối tượng nhất định. Các đối tượng ấy được gọi là những **phần tử** của tập hợp.")
                    
                    st.info("💡 *Ví dụ trực quan:* Tập hợp các bông hồng trong lọ hoa, tập hợp các con cá vàng trong bình, hoặc tập hợp các số trên mặt đồng hồ.")
                    
                    st.write(r"Xét tập hợp $M$ gồm các số: 4; 1; 9; 8. Ta ký hiệu các mối quan hệ như sau:")
                    st.write(r"- $4 \in M$ (đọc là: 4 thuộc M, hoặc 4 là một phần tử của M).")
                    st.write(r"- $7 \notin M$ (đọc là: 7 không thuộc M, hoặc 7 không là phần tử của M).")
                    st.write(r"⚠️ *Chú ý:* Khi $x \in A$, ta còn nói '*x nằm trong A*' hoặc '*A chứa x*'.")
                    
                    st.markdown("---")
                    st.subheader("2. Cách mô tả một tập hợp")
                    st.write(r"Người ta thường đặt tên tập hợp bằng các **chữ cái in hoa** ($A, B, C...$). Có 2 cách chính để mô tả:")
                    
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.markdown("**Cách 1: Liệt kê các phần tử**")
                        st.write("Viết các phần tử trong dấu ngoặc nhọn `{ }` theo thứ tự tùy ý, cách nhau bởi dấu chấm phẩy `;`. Mỗi phần tử **chỉ được viết một lần**.")
                        st.latex(r"P = \{0; 1; 2; 3; 4; 5\}")
                    with col_c2:
                        st.markdown("**Cách 2: Nêu dấu hiệu đặc trưng**")
                        st.write("Chỉ ra tính chất chung của các phần tử để xác định chúng một cách chính xác.")
                        st.latex(r"P = \{n \mid n \text{ là số tự nhiên nhỏ hơn } 6\}")
                        
                    st.markdown("---")
                    st.subheader(r"3. Tập hợp các số tự nhiên $\mathbb{N}$ và $\mathbb{N}^*$")
                    st.write(r"- Kí hiệu $\mathbb{N}$ là tập hợp gồm tất cả các số tự nhiên: $0; 1; 2; 3;...$")
                    st.latex(r"\mathbb{N} = \{0; 1; 2; 3; ...\}")
                    st.write(r"- Kí hiệu $\mathbb{N}^*$ là tập hợp các số tự nhiên **khác 0**:")
                    st.latex(r"\mathbb{N}^* = \{1; 2; 3; ...\}")
                    
                    st.markdown("---")
                    st.subheader("🎯 Thử thách Luyện tập")
                    
                    # 1. Thử thách nhỏ (Vận dụng) - ĐÃ ĐƯA LÊN TRƯỚC
                    st.success(r"📝 **Thử thách Vận dụng:** Khi viết tập hợp $L$ các chữ cái trong từ 'NHA TRANG' bằng cách liệt kê, bạn Nam viết: $L = \{N; H; A; T; R; A; N; G\}$. Theo em bạn Nam viết đúng hay sai?")
                    chose_nam = st.radio("Câu trả lời của bạn:", ["Chưa chọn", "Nam viết ĐÚNG", "Nam viết SAI"], key="quiz_nam")
                    if chose_nam == "Nam viết SAI":
                        st.success(r"🎉 Chính xác! Mỗi phần tử chỉ được viết 1 lần. Chữ N và chữ A xuất hiện 2 lần nên chỉ viết lại 1 lần. Cách viết đúng là: $L = \{N; H; A; T; R; G\}$.")
                    elif chose_nam == "Nam viết ĐÚNG":
                        st.error("❌ Chưa chính xác rồi! Em hãy nhớ quy tắc: Mỗi phần tử chỉ được liệt kê duy nhất một lần nhé.")

                    # 2. Luyện tập 2 (Chuyển thể từ SGK)
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

                    # 3. Luyện tập 3 (Chuyển thể từ SGK)
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
                        
                        if diem >= 7:
                            st.success(f"🎉 TUYỆT VỜI! Em đạt **{diem}/10** điểm. Bài học số 2 đã được mở khóa!")
                            st.balloons()
                            # Lưu trạng thái hoàn thành vào bộ nhớ tạm
                            st.session_state.hoan_thanh_bai_1 = True
                        else:
                            st.error(f"⚠️ Em mới đạt **{diem}/10** điểm. Chưa đủ 7.0 điểm để qua cửa rồi. Hãy đọc lại lý thuyết và làm lại nhé!")
                            st.session_state.hoan_thanh_bai_1 = False

                with tab_mo_rong:
                    st.subheader("👨‍🔬 Nhà toán học Georg Cantor (1845 - 1918)")
                    st.write("Mãi đến cuối thế kỉ XIX, lí thuyết tập hợp mới được phát triển nhờ các nghiên cứu của nhà toán học Cantor, người Đức. Từ đó, lí thuyết tập hợp đã nhanh chóng trở thành nền tảng của Toán học hiện đại.")
                    
                    st.markdown("**💡 Kiến thức mở rộng thêm:**")
                    st.write(r"- **Tập hữu hạn:** Là tập hợp có một số lượng phần tử đếm được. Ví dụ tập $Y = \{1; 2; 3; ...; 50\}$ có đúng 50 phần tử.")
                    st.write(r"- **Tập vô hạn:** Là tập hợp có vô số phần tử. Ví dụ tập hợp số tự nhiên $\mathbb{N}$ là tập vô hạn.")
                    
                    st.markdown("**🤝 Giao của hai tập hợp:**")
                    st.write(r"Gọi $C$ là tập hợp gồm các phần tử vừa thuộc tập $A$, vừa thuộc tập $B$. Ta gọi tập $C$ là **giao của hai tập hợp $A$ và $B$**, kí hiệu là:")
                    st.latex(r"C = A \cap B")
