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
                    st.subheader("1. Tập hợp và phần tử của tập hợp")
                    st.write("Một **tập hợp** (gọi tắt là **tập**) bao gồm những đối tượng nhất định. Các đối tượng ấy được gọi là những **phần tử** của tập hợp.")
                    
                    st.info("💡 *Ví dụ trực quan:* Tập hợp các bông hồng trong lọ hoa, tập hợp các con cá vàng trong bình, hoặc tập hợp các số trên mặt đồng hồ.")
                    
                    st.write("Xét tập hợp $M$ gồm các số: 4; 1; 9; 8. Ta ký hiệu các mối quan hệ như sau:")
                    st.write("- $4 \in M$ (đọc là: *4 thuộc M*, hoặc *4 là một phần tử của M*).")
                    st.write("- $7 \notin M$ (đọc là: *7 không thuộc M*, hoặc *7 không là phần tử của M*).")
                    st.write("⚠️ *Chú ý:* Khi $x \in A$, ta còn nói '*x nằm trong A*' hoặc '*A chứa x*'.")
                    
                    st.markdown("---")
                    st.subheader("2. Cách mô tả một tập hợp")
                    st.write("Người ta thường đặt tên tập hợp bằng các **chữ cái in hoa** ($A, B, C...$). Có 2 cách chính để mô tả:")
                    
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
                    st.subheader("3. Tập hợp các số tự nhiên $\mathbb{N}$ và $\mathbb{N}^*$")
                    st.write("- Kí hiệu $\mathbb{N}$ là tập hợp gồm tất cả các số tự nhiên: $0; 1; 2; 3;...$")
                    st.latex(r"\mathbb{N} = \{0; 1; 2; 3; ...\}")
                    st.write("- Kí hiệu $\mathbb{N}^*$ là tập hợp các số tự nhiên **khác 0**:")
                    st.latex(r"\mathbb{N}^* = \{1; 2; 3; ...\}")
                    
                    st.success("📝 **Thử thách nhỏ:** Khi viết tập hợp $L$ các chữ cái trong từ 'NHA TRANG' bằng cách liệt kê, bạn Nam viết: $L = \{N; H; A; T; R; A; N; G\}$. Theo em bạn Nam viết đúng hay sai?")
                    chose_nam = st.radio("Câu trả lời của bạn:", ["Chưa chọn", "Nam viết ĐÚNG", "Nam viết SAI"], key="quiz_nam")
                    if chose_nam == "Nam viết SAI":
                        st.success("🎉 Chính xác! Mỗi phần tử chỉ được viết 1 lần. Chữ N và chữ A xuất hiện 2 lần nên chỉ viết lại 1 lần. Cách viết đúng là: $L = \{N; H; A; T; R; G\}$.")
                    elif chose_nam == "Nam viết ĐÚNG":
                        st.error("❌ Chưa chính xác rồi! Em hãy nhớ quy tắc: Mỗi phần tử chỉ được liệt kê duy nhất một lần nhé.")

                with tab_bai_tap:
                    st.subheader("✍️ Hệ thống bài tập tự động chấm điểm")
                    st.write("Các em hãy hoàn thành các bài tập dưới đây để củng cố kiến thức nhé!")
                    
                    # Bài tập 1 (Dựa theo Bài 1.2 SGK)
                    st.markdown("**Câu 1:** Cho tập hợp $U = \{x \in \mathbb{N} \mid x \text{ chia hết cho } 3\}$. Số nào sau đây thuộc tập hợp $U$?")
                    q1 = st.selectbox("Chọn đáp án của em:", ["-- Chọn số --", "5", "7", "6", "1"], key="q1")
                    if q1 == "6":
                        st.success("🎯 Đúng rồi! 6 chia hết cho 3 nên $6 \in U$.")
                    elif q1 != "-- Chọn số --":
                        st.error("📌 Sai rồi, số này không chia hết cho 3 nên không thuộc tập U.")
                        
                    # Bài tập 2 (Dựa theo Bài 1.3 SGK)
                    st.markdown("**Câu 2:** Tập hợp $K$ các số tự nhiên nhỏ hơn 7 được viết theo cách liệt kê là:")
                    q2 = st.radio("Chọn một đáp án:", [
                        "Chưa chọn",
                        r"K = {1; 2; 3; 4; 5; 6}",
                        r"K = {0; 1; 2; 3; 4; 5; 6}",
                        r"K = {0; 1; 2; 3; 4; 5; 6; 7}"
                    ], key="q2")
                    if q2 == r"K = {0; 1; 2; 3; 4; 5; 6}":
                        st.success("🎯 Xuất sắc! Số tự nhiên nhỏ hơn 7 bắt đầu từ số 0 và kết thúc ở số 6.")
                    elif q2 != "Chưa chọn":
                        st.error("📌 Hãy lưu ý: Tập hợp số tự nhiên phải chứa cả số 0, và từ 'nhỏ hơn 7' tức là không lấy số 7.")

                    # Bài tập 3 (Dựa theo Bài 1.5 SGK)
                    st.markdown("**Câu 3 (Thực tế):** Hệ Mặt Trời gồm Mặt Trời ở trung tâm và 8 hành tinh quay quanh. Nếu gọi $S$ là tập hợp các hành tinh này, hành tinh nào dưới đây **không** nằm trong tập $S$?")
                    q3 = st.selectbox("Chọn hành tinh:", ["-- Chọn --", "Trái Đất", "Sao Hỏa", "Mặt Trăng", "Mộc tinh"], key="q3")
                    if q3 == "Mặt Trăng":
                        st.success("🎯 Chính xác! Mặt Trăng là vệ tinh của Trái Đất, không phải là một hành tinh trong 8 hành tinh quay quanh Mặt Trời.")
                    elif q3 != "-- Chọn --":
                        st.error("📌 Sai rồi, đây là một trong số các hành tinh thuộc Hệ Mặt Trời.")

                with tab_mo_rong:
                    st.subheader("👨‍🔬 Nhà toán học Georg Cantor (1845 - 1918)")
                    st.write("Mãi đến cuối thế kỉ XIX, lí thuyết tập hợp mới được phát triển nhờ các nghiên cứu của nhà toán học Cantor, người Đức. Từ đó, lí thuyết tập hợp đã nhanh chóng trở thành nền tảng của Toán học hiện đại.")
                    
                    st.markdown("**💡 Kiến thức mở rộng thêm:**")
                    st.write("- **Tập hữu hạn:** Là tập hợp có một số lượng phần tử đếm được. Ví dụ tập $Y = \{1; 2; 3; ...; 50\}$ có đúng 50 phần tử.")
                    st.write("- **Tập vô hạn:** Là tập hợp có vô số phần tử. Ví dụ tập hợp số tự nhiên $\mathbb{N}$ là tập vô hạn.")
                    
                    st.markdown("**🤝 Giao của hai tập hợp:**")
                    st.write("Gọi $C$ là tập hợp gồm các phần tử vừa thuộc tập $A$, vừa thuộc tập $B$. Ta gọi tập $C$ là **giao của hai tập hợp $A$ và $B$**, kí hiệu là:")
                    st.latex(r"C = A \cap B")
