import streamlit as st
from PIL import Image
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =====================
# 기본 설정
# =====================
st.set_page_config(
    page_title="현장 안전 점검",
    layout="centered"
)

# =====================
# 모바일 가독성용 CSS
# =====================
st.markdown("""
<style>
    .big-title {
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 20px;
    }
    .stButton>button {
        font-size: 20px;
        height: 3em;
    }
    label {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# 제목
# =====================
st.markdown("<div class='big-title'>📸 현장 안전 점검 앱</div>", unsafe_allow_html=True)

# =====================
# 기본 정보
# =====================
st.markdown("<div class='section-title'>기본 정보</div>", unsafe_allow_html=True)

site_name = st.text_input("현장명")
inspector = st.text_input("점검자")

# =====================
# 사진 업로드
# =====================
st.markdown("<div class='section-title'>사진 업로드</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "현장 사진을 업로드하세요",
    type=["jpg", "jpeg", "png"]
)

image = None
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 사진", use_container_width=True)

    # =====================
    # 사진 선택 후 UI
    # =====================
    st.markdown("<div class='section-title'>점검 항목 선택</div>", unsafe_allow_html=True)

    location = st.selectbox(
        "위치",
        ["작업장", "통로", "고소작업 구간", "전기설비 주변", "기타"]
    )

    risk = st.selectbox(
        "위험요인",
        ["추락 위험", "전도 위험", "낙하물 위험", "감전 위험", "협착 위험"]
    )

    action = st.selectbox(
        "조치사항",
        ["즉시 조치", "작업 중지", "안전시설 설치", "관리자 통보", "교육 실시"]
    )

    remark = st.selectbox(
        "비고",
        ["해당 없음", "추가 조치 필요", "지속 관리 필요"]
    )

# =====================
# PDF 생성 함수
# =====================
def create_pdf(data, image):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "현장 안전 점검 보고서")
    y -= 30

    c.setFont("Helvetica", 11)
    for key, value in data.items():
        c.drawString(50, y, f"{key} : {value}")
        y -= 18

    if image:
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        c.drawImage(img_buffer, 50, y - 200, width=200, height=200)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# =====================
# 저장 버튼
# =====================
st.markdown("<br>", unsafe_allow_html=True)

if st.button("📄 PDF로 저장"):
    if not uploaded_file:
        st.warning("사진을 업로드하세요.")
    else:
        data = {
            "현장명": site_name,
            "점검자": inspector,
            "점검일": datetime.now().strftime("%Y-%m-%d"),
            "위치": location,
            "위험요인": risk,
            "조치사항": action,
            "비고": remark
        }

        pdf = create_pdf(data, image)

        st.success("PDF 생성 완료!")
        st.download_button(
            label="📥 PDF 다운로드",
            data=pdf,
            file_name="안전점검보고서.pdf",
            mime="application/pdf"
        )