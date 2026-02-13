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
import tempfile
import os
from datetime import datetime

# -----------------------------
# 한글 폰트 등록
# -----------------------------
FONT_PATH = "MalgunGothic.ttf"

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError("MalgunGothic.ttf 파일이 프로젝트 루트에 없습니다.")

pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))

# -----------------------------
# PDF 생성 함수
# -----------------------------
def create_inspection_pdf(
    output_path,
    site_name,
    check_date,
    inspector,
    table_data,
    photo_files
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontName="Malgun",
        fontSize=18,
        alignment=1,
        spaceAfter=12
    )

    info_style = ParagraphStyle(
        "info",
        parent=styles["Normal"],
        fontName="Malgun",
        fontSize=10,
        spaceAfter=6
    )

    table_style_font = [
        ("FONT", (0, 0), (-1, -1), "Malgun")
    ]

    story = []

    # 제목
    story.append(Paragraph("현장 안전점검 보고서", title_style))
    story.append(Spacer(1, 12))

    # 기본 정보
    story.append(Paragraph(f"현장명: {site_name}", info_style))
    story.append(Paragraph(f"점검일자: {check_date}", info_style))
    story.append(Paragraph(f"점검자: {inspector}", info_style))
    story.append(Spacer(1, 16))

    # 점검 표
    table = Table(
        table_data,
        colWidths=[50, 120, 60, 200]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("FONT", (0, 0), (-1, -1), "Malgun"),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # 사진
    if photo_files:
        story.append(Paragraph("현장 사진", ParagraphStyle(
            "photo_title",
            fontName="Malgun",
            fontSize=14,
            spaceAfter=12
        )))

        for idx, photo in enumerate(photo_files):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(photo.read())
                img_path = tmp.name

            img = Image(img_path)
            img.drawWidth = 120 * mm
            img.drawHeight = img.drawWidth * 0.75

            story.append(img)
            story.append(Spacer(1, 12))

            if (idx + 1) % 2 == 0:
                story.append(PageBreak())

    doc.build(story)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="현장 안전점검", layout="centered")
st.title("📋 현장 안전점검 앱")

site_name = st.text_input("현장명")
inspector = st.text_input("점검자")
check_date = st.date_input("점검일자")

st.subheader("점검 결과")
item = st.text_input("점검 항목")
status = st.selectbox("상태", ["양호", "미흡"])
note = st.text_input("비고")

if "rows" not in st.session_state:
    st.session_state.rows = [["번호", "점검항목", "상태", "비고"]]

if st.button("점검 항목 추가"):
    num = len(st.session_state.rows)
    st.session_state.rows.append([str(num), item, status, note])

st.table(st.session_state.rows)

st.subheader("현장 사진 업로드")
photos = st.file_uploader(
    "사진 선택 (여러 장 가능)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

st.divider()

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
            photos
        )

        with open(output_path, "rb") as f:
            st.download_button(
                "📥 PDF 다운로드",
                f,
                file_name=filename,
                mime="application/pdf"
            )
