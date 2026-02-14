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
# 한글 폰트 등록
# -----------------------------
FONT_PATH = "NotoSansKR-Regular.ttf"
if not os.path.exists(FONT_PATH):
    st.error("❌ NotoSansKR-Regular.ttf 파일이 없습니다. GitHub에 업로드하세요.")
    st.stop()

pdfmetrics.registerFont(TTFont("Korean", FONT_PATH))

# -----------------------------
# PDF 생성 함수
# -----------------------------
def create_inspection_pdf(
    output_path,
    site_name,
    check_date,
    inspector,
    table_data,
    photo_entries
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontName="Korean",
        fontSize=16,
        alignment=1,
        spaceAfter=10
    )
    info_style = ParagraphStyle(
        "info",
        parent=styles["Normal"],
        fontName="Korean",
        fontSize=10,
        spaceAfter=4
    )
    photo_info_style = ParagraphStyle(
        "photo_info",
        parent=styles["Normal"],
        fontName="Korean",
        fontSize=10,
        spaceAfter=2
    )

    story = []
    # 제목
    story.append(Paragraph("현장 안전점검 보고서", title_style))
    story.append(Spacer(1, 10))

    # 현장 정보
    story.append(Paragraph(f"현장명: {site_name}", info_style))
    story.append(Paragraph(f"점검일자: {check_date}", info_style))
    story.append(Paragraph(f"점검자: {inspector}", info_style))
    story.append(Spacer(1, 10))

    # 점검 표
    table = Table(table_data, colWidths=[30, 140, 60, 200])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONT", (0,0), (-1,-1), "Korean"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))

    # 사진 + 설명
    if photo_entries:
        story.append(Paragraph(
            "현장 사진",
            ParagraphStyle(
                "photo_title",
                fontName="Korean",
                fontSize=12,
                spaceAfter=6
            )
        ))

        for idx, entry in enumerate(photo_entries):
            photo_file = entry["file"]
            location = entry.get("location", "")
            risk = entry.get("risk", "")
            action = entry.get("action", "")

            img_bytes = BytesIO(photo_file.read())
            img = Image(img_bytes)

            # 사진 크기 조절
            max_width = 150*mm
            max_height = 100*mm
            aspect = img.imageWidth / img.imageHeight
            if img.imageWidth > max_width:
                img.drawWidth = max_width
                img.drawHeight = max_width / aspect
            if img.drawHeight > max_height:
                img.drawHeight = max_height
                img.drawWidth = max_height * aspect

            story.append(img)
            story.append(Spacer(1, 4))

            # 사진별 설명
            story.append(Paragraph(f"위치: {location}", photo_info_style))
            story.append(Paragraph(f"위험요인: {risk}", photo_info_style))
            story.append(Paragraph(f"조치사항: {action}", photo_info_style))
            story.append(Spacer(1, 10))

            # 2장마다 페이지 구분
            if (idx + 1) % 2 == 0:
                story.append(PageBreak())

    doc.build(story)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="현장 안전점검", layout="centered")
st.title("📋 현장 안전점검 앱")

# 현장 정보 입력
site_name = st.text_input("현장명")
inspector = st.text_input("점검자")
check_date = st.date_input("점검일자")

# 점검 결과 입력
st.subheader("점검 결과")
item = st.text_input("점검 항목")
status = st.selectbox("상태", ["양호", "미흡"])
note = st.text_input("비고")

if "rows" not in st.session_state:
    st.session_state.rows = [["번호", "점검항목", "상태", "비고"]]

if st.button("점검 항목 추가"):
    st.session_state.rows.append(
        [str(len(st.session_state.rows)), item, status, note]
    )

st.table(st.session_state.rows)

# 사진 업로드 + 설명
st.subheader("현장 사진 업로드")
uploaded_files = st.file_uploader(
    "사진 선택 (여러 장 가능)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

photo_entries = []
if uploaded_files:
    for f in uploaded_files:
        with st.expander(f"사진: {f.name}"):
            location = st.text_input("위치", key=f"{f.name}_loc")
            risk = st.text_input("위험요인", key=f"{f.name}_risk")
            action = st.text_input("조치사항", key=f"{f.name}_action")
        photo_entries.append({
            "file": f,
            "location": location,
            "risk": risk,
            "action": action
        })

st.divider()

# PDF 생성
if st.button("PDF 생성"):
    if not site_name or not inspector:
        st.error("현장명과 점검자를 입력하세요.")
    else:
        filename = f"{site_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        output_path = os.path.join(tempfile.gettempdir(), filename)

        create_inspection_pdf(
            output_path,
            site_name,
            check_date.strftime("%Y-%m-%d"),
            inspector,
            st.session_state.rows,
            photo_entries
        )

        with open(output_path, "rb") as f:
            st.download_button(
                "📥 PDF 다운로드",
                f,
                file_name=filename,
                mime="application/pdf"
            )

