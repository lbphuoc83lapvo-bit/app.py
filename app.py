import streamlit as st

# Cấu hình trang web
st.set_page_config(page_title="Web App Học Tập Toán Học", layout="centered")

# 1. KHỞI TẠO TRẠNG THÁI (Ghi nhớ tiến độ của học sinh)
if 'lesson_1_passed' not in st.session_state:
    st.session_state.lesson_1_passed = False
if 'score_lesson_1' not in st.session_state:
    st.session_state.score_lesson_1 = 0

st.title("📐 CỔNG HỌC TẬP TOÁN HỌC TRỰC TUYẾN")
st.write("Hãy hoàn thành từng bài học và đạt từ 5 điểm trở lên để mở khóa bài tiếp theo.")

# ==========================================
# BÀI HỌC 1: ĐẠI SỐ
# ==========================================
st.header("📖 Bài 1: Khái niệm về Phương trình bậc nhất")

# Phần 1: Video bài giảng
st.subheader("1. Video bài giảng")
# Thay đường dẫn video bằng link YouTube bài giảng của bạn
st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") 

# Phần 2: Tài liệu đọc (Hỗ trợ công thức LaTeX)
st.subheader("2. Tài liệu tóm tắt lý thuyết")
st.markdown("""
Phương trình bậc nhất một ẩn là phương trình có dạng:
$$ax + b = 0$$
Trong đó:
- $a$ và $b$ là hai số đã biết ($a \neq 0$).
- $x$ là ẩn số.

**Ví dụ:** Giải phương trình $2x - 4 = 0$
$$\Leftrightarrow 2x = 4 \Leftrightarrow x = 2$$
""")

# Phần 3: Bài tập trắc nghiệm sau bài học
st.subheader("3. Bài tập đánh giá năng lực")

with st.form(key='quiz_lesson_1'):
    st.write("Chọn đáp án đúng cho các câu hỏi sau (Mỗi câu đúng được 5 điểm):")
    
    # Câu hỏi 1
    q1 = st.radio(
        "**Câu 1:** Phương trình nào sau đây là phương trình bậc nhất một ẩn?",
        ["a) $0x + 3 = 0$", "b) $2x^2 - 1 = 0$", "c) $3x - 5 = 0$", "d) $\frac{1}{x} + 2 = 0$"]
    )
    
    # Câu hỏi 2
    q2 = st.radio(
        "**Câu 2:** Nghiệm của phương trình $5x + 10 = 0$ là:",
        ["a) $x = 2$", "b) $x = -2$", "c) $x = 5$", "d) $x = -5$"]
    )
    
    submit_button = st.form_submit_button(label='Nộp bài kiểm tra')

# Xử lý kết quả khi học sinh bấm nộp bài
if submit_button:
    score = 0
    # Chấm câu 1 (Đáp án đúng là c)
    if "c)" in q1:
        score += 5
    # Chấm câu 2 (Đáp án đúng là b)
    if "b)" in q2:
        score += 5
        
    st.session_state.score_lesson_1 = score
    
    if score >= 5:
        st.session_state.lesson_1_passed = True
        st.success(f"🎉 Chúc mừng! Bạn đạt {score}/10 điểm. Bài học tiếp theo đã được mở khóa!")
    else:
        st.session_state.lesson_1_passed = False
        st.error(f"❌ Bạn đạt {score}/10 điểm. Bạn cần đạt từ 5 điểm trở lên để tiếp tục. Hãy xem lại video và làm lại bài!")

# ==========================================
# BÀI HỌC 2: TỰ ĐỘNG KHÓA/MỞ
# ==========================================
st.markdown("---")
st.header("🔒 Bài 2: Hệ hai phương trình bậc nhất hai ẩn")

if st.session_state.lesson_1_passed:
    st.info("🔓 Bài học này đã được mở khóa thành công!")
    st.subheader("1. Video bài giảng Bài 2")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    st.subheader("2. Lý thuyết trọng tâm")
    st.markdown("""
    Hệ hai phương trình bậc nhất hai ẩn có dạng tổng quát:
    $$\\begin{cases} ax + by = c \\\\ a'x + b'y = c' \\end{cases}$$
    Bạn có thể dùng phương pháp thế hoặc phương pháp cộng đại số để giải hệ phương trình này.
    """)
    # Bạn có thể tiếp tục thêm form bài tập cho Bài 2 tại đây...
else:
    st.warning("Bài học này đang bị khóa. Bạn cần hoàn thành Bài tập 1 với số điểm $\ge 5$ để mở khóa.")
