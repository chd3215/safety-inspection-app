import streamlit as st
from datetime import date
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ===============================
# 기본 설정
# ===============================
st.set_page_config(
    page_title="현장 안전점검",
    layout="wide"
)

# ===============================
# 한글 폰트 등록 (★ 핵심)
# ===============================
FONT_PATH = "NotoSansKR-Regular.ttf"

if not os.path.exists(FONT_PATH):
    st.error("❌ NotoSansKR-Regular.ttf 파일이 app.py와 같은 폴더에 없습니다.")
    st.stop()

pdfmetrics.registerFont(TTFont("Korean", FONT_PATH))

# ===============================
# 제목
# ===============================
st.markdown(
    "<h1 style='font-size:32px; text-align:center'>📋 현장 안전점검</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size:18px; text-align:center'>사진 찍고 체크 → PDF 바로 생성</p>",
    unsafe_allow_html=True
)
st.divider()

# ===============================
# 현장 정보
# ===============================
st.markdown("<h2 style='font-size:24px'>현장 정보</h2>", unsafe_allow_html=True)

site_name = st.text_input("현장명", placeholder="예: ○○현장")
inspector = st.text_input("점검자", placeholder="이름")
inspection_date = st.date_input("점검일자", value=date.today())

st.divider()

# ===============================
# 점검 내용
# ===============================
st.markdown("<h2 style='font-size:24px'>점검 내용</h2>", unsafe_allow_html=True)

item_name = st.text_input("점검 항목", placeholder="예: 계단 안전 상태")

LOCATION_OPTIONS = ["현장 입구", "작업장 내부", "외부", "기타"]
RISK_OPTIONS = ["낙상", "감전", "낙하물", "전도", "기타"]
ACTION_OPTIONS = ["주의", "즉시 조치", "보수 필요", "교육 실시", "기타"]

location = st.selectbox("위치", LOCATION_OPTIONS)
risk = st.multiselect("위험요인", RISK_OPTIONS)
action = st.selectbox("조치사항", ACTION_OPTIONS)
remark = st.text_input("비고", placeholder="추가 설명 (선택)")

st.divider()

# ===============================
# 사진 업로드
# ===============================
st.markdown("<h2 style='font-size:24px'>📷 현장 사진</h2>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    for i, f in enumerate(uploaded_files):
        st.image(f, caption=f"사진 {i+1}", use_column_width=True)

st.divider()

# ===============================
# PDF 생성
# ===============================
if st.button("📄 PDF 생성"):
    if not uploaded_files:
        st.warning("사진을 1장 이상 업로드하세요.")
        st.stop()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 25 * mm

    # 제목
    c.setFont("Korean", 16)
    c.drawString(20 * mm, y, "현장 안전점검 보고서")
    y -= 15 * mm

    # 기본 정보
    c.setFont("Korean", 11)
    c.drawString(20 * mm, y, f"현장명: {site_name}")
    y -= 7 * mm
    c.drawString(20 * mm, y, f"점검자: {inspector}")
    y -= 7 * mm
    c.drawString(20 * mm, y, f"점검일자: {inspection_date.strftime('%Y-%m-%d')}")
    y -= 10 * mm

    # 점검 내용
    c.drawString(20 * mm, y, f"점검항목: {item_name}")
    y -= 7 * mm
    c.drawString(20 * mm, y, f"위치: {location}")
    y -= 7 * mm
    c.drawString(20 * mm, y, f"위험요인: {', '.join(risk)}")
    y -= 7 * mm
    c.drawString(20 * mm, y, f"조치사항: {action}")
    y -= 7 * mm
    c.drawString(20 * mm, y, f"비고: {remark}")
    y -= 10 * mm

    # ===============================
    # 사진 (1장 = 자동 페이지 분리)
    # ===============================
    for f in uploaded_files:
        img = Image.open(f)
        img_width, img_height = img.size
        ratio = img_height / img_width

        draw_width = width - 40 * mm
        draw_height = draw_width * ratio

        if y - draw_height < 20 * mm:
            c.showPage()
            y = height - 25 * mm
            c.setFont("Korean", 11)

        c.drawInlineImage(
            img,
            20 * mm,
            y - draw_height,
            draw_width,
            draw_height
        )
        y -= draw_height + 10 * mm

    c.save()
    buffer.seek(0)

    st.download_button(
        label="📥 PDF 다운로드",
        data=buffer,
        file_name=f"{site_name}_안전점검보고서.pdf",
        mime="application/pdf"
    )

    st.success("✅ PDF 생성 완료")

