# app.py (모바일 전용 최적화)
import streamlit as st
from datetime import date
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

st.set_page_config(page_title="현장 안전점검 앱", layout="wide")

# =======================
# 1️⃣ 제목
# =======================
st.markdown("<h1 style='font-size:32px; text-align:center'>📋 현장 안전점검</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:18px; text-align:center'>사진 + 체크 후 PDF 바로 생성</p>", unsafe_allow_html=True)
st.divider()

# =======================
# 2️⃣ 현장 정보 카드
# =======================
with st.container():
    st.markdown("<h2 style='font-size:24px'>현장 정보</h2>", unsafe_allow_html=True)
    site_name = st.text_input("현장명", placeholder="현장명을 입력하세요")
    inspector = st.text_input("점검자", placeholder="점검자 이름")
    inspection_date = st.date_input("점검일자", value=date.today())

st.divider()

# =======================
# 3️⃣ 점검 항목 카드
# =======================
with st.container():
    st.markdown("<h2 style='font-size:24px'>점검 항목</h2>", unsafe_allow_html=True)
    item_name = st.text_input("점검항목", placeholder="예: 계단 안전, 감전 위험 등")

    LOCATION_OPTIONS = ["사무실", "현장 A", "현장 B", "현장 C"]
    RISK_OPTIONS = ["낙상", "감전", "낙하물", "전도", "기타"]
    ACTION_OPTIONS = ["주의", "보수", "개선", "교육", "기타"]

    location = st.selectbox("위치", LOCATION_OPTIONS)
    risk = st.multiselect("위험요인", RISK_OPTIONS)
    action = st.selectbox("조치사항", ACTION_OPTIONS)
    remarks = st.text_input("비고", placeholder="필요 시 입력")

st.divider()

# =======================
# 4️⃣ 사진 업로드 카드
# =======================
with st.container():
    st.markdown("<h2 style='font-size:24px'>📷 현장 사진</h2>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("사진 업로드 (여러장 가능)", type=["png","jpg","jpeg"], accept_multiple_files=True)

    if uploaded_files:
        for i, f in enumerate(uploaded_files):
            st.image(f, caption=f"사진 {i+1}", use_column_width=True)

st.divider()

# =======================
# 5️⃣ PDF 생성 고정 버튼
# =======================
st.markdown(
    """
    <style>
    .fixed-button {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 100;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("📄 PDF 생성", key="pdf_button"):
    if not uploaded_files:
        st.warning("사진을 업로드해야 PDF를 생성할 수 있습니다.")
    else:
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        y = height - 30*mm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20*mm, y, f"📋 현장 안전점검 보고서")
        y -= 15*mm

        c.setFont("Helvetica", 12)
        c.drawString(20*mm, y, f"현장명: {site_name}")
        y -= 7*mm
        c.drawString(20*mm, y, f"점검자: {inspector}")
        y -= 7*mm
        c.drawString(20*mm, y, f"점검일자: {inspection_date.strftime('%Y/%m/%d')}")
        y -= 12*mm

        c.drawString(20*mm, y, f"점검항목: {item_name}")
        y -= 7*mm
        c.drawString(20*mm, y, f"위치: {location}")
        y -= 7*mm
        c.drawString(20*mm, y, f"위험요인: {', '.join(risk)}")
        y -= 7*mm
        c.drawString(20*mm, y, f"조치사항: {action}")
        y -= 7*mm
        c.drawString(20*mm, y, f"비고: {remarks}")
        y -= 10*mm

        # 사진 삽입
        for f in uploaded_files:
            img = Image.open(f)
            img_width, img_height = img.size
            aspect = img_height / img_width
            display_width = width - 40*mm
            display_height = display_width * aspect
            if y - display_height < 20*mm:
                c.showPage()
                y = height - 30*mm
            c.drawInlineImage(img, 20*mm, y - display_height, display_width, display_height)
            y -= (display_height + 5*mm)

        c.save()
        pdf_buffer.seek(0)

        st.download_button(
            label="PDF 다운로드",
            data=pdf_buffer,
            file_name=f"{site_name}_{inspection_date}.pdf",
            mime="application/pdf"
        )
        st.success("PDF 생성 완료!")

