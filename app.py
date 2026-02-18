import streamlit as st
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import tempfile
import os
from datetime import datetime

# -----------------------------
# 한글 폰트 (배포용)
# -----------------------------
FONT_PATH = "NotoSansKR-Regular.ttf"
pdfmetrics.registerFont(TTFont("Korean", FONT_PATH))

# -----------------------------
# PDF 생성 함수
# -----------------------------
def create_pdf(output_path, site, date, inspector, table_data, photos):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "title", fontName="Korean", fontSize=16, alignment=1, spaceAfter=10
    )
    normal = ParagraphStyle(
        "normal", fontName="Korean", fontSize=10, spaceAfter=4
    )

    story = []

    # 제목
    story.append(Paragraph("현장 안전점검 보고서", title))
    story.append(Paragraph(f"현장명: {site}", normal))
    story.append(Paragraph(f"점검일자: {date}", normal))
    story.append(Paragraph(f"점검자: {inspector}", normal))
    story.append(Spacer(1, 10))

    # 점검표
    table = Table(table_data, colWidths=[30, 150, 60, 180])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONT", (0,0), (-1,-1), "Korean"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(table)
    story.append(PageBreak())

    # 사진 (1장 = 1페이지)
    for p in photos:
        img = Image(BytesIO(p["file"].read()))
        img.drawWidth = 160 * mm
        img.drawHeight = 100 * mm

        story.append(img)
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"위치: {p['location']}", normal))
        story.append(Paragraph(f"위험요인: {p['risk']}", normal))
        story.append(Paragraph(f"조치사항: {p['action']}", normal))
        story.append(PageBreak())

    doc.build(story)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="현장 안전점검", layout="centered")
st.title("##📋 현장 안전점검 앱")

site = st.text_input("현장명")
inspector = st.text_input("점검자")
date = st.date_input("점검일자")

# -----------------------------
# 점검표
# -----------------------------
st.subheader("점검 항목")

if "rows" not in st.session_state:
    st.session_state.rows = [["번호", "점검항목", "상태", "비고"]]

item = st.text_input("점검항목")
status = st.selectbox("상태", ["양호", "미흡"])
note = st.text_input("비고")

if st.button("항목 추가"):
    st.session_state.rows.append(
        [str(len(st.session_state.rows)), item, status, note]
    )

st.table(st.session_state.rows)

# -----------------------------
# 사진 + 항상 보이는 선택형 UI
# -----------------------------
st.subheader("📷 현장 사진")

LOCATION_OPTIONS = ["1층", "2층", "옥상", "계단", "출입구", "기계실", "기타"]
RISK_OPTIONS = ["추락", "감전", "전도", "협착", "낙하물", "화재"]
ACTION_OPTIONS = [
    "즉시 시정조치 요청",
    "작업 중지 조치",
    "안전조치 완료",
    "추후 조치 예정"
]

uploaded = st.file_uploader(
    "사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

photo_entries = []

if uploaded:
    st.info("사진마다 아래 항목을 바로 선택하세요")

    for i, f in enumerate(uploaded):
        st.markdown(f"### 📸 사진 {i+1}")

        location = st.selectbox(
            "위치",
            LOCATION_OPTIONS,
            key=f"loc_{i}"
        )

        risk = st.multiselect(
            "위험요인",
            RISK_OPTIONS,
            key=f"risk_{i}"
        )

        action = st.selectbox(
            "조치사항",
            ACTION_OPTIONS,
            key=f"action_{i}"
        )

        photo_entries.append({
            "file": f,
            "location": location,
            "risk": ", ".join(risk),
            "action": action
        })

        st.divider()

# -----------------------------
# PDF 생성
# -----------------------------
if st.button("📄 PDF 생성"):
    filename = f"{site}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    path = os.path.join(tempfile.gettempdir(), filename)

    create_pdf(
        path,
        site,
        date.strftime("%Y-%m-%d"),
        inspector,
        st.session_state.rows,
        photo_entries
    )

    with open(path, "rb") as f:
        st.download_button(
            "📥 PDF 다운로드",
            f,
            file_name=filename,
            mime="application/pdf"
        )


