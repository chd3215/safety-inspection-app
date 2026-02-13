from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
import os


def create_inspection_pdf(
    output_path,
    site_name,
    check_date,
    inspector,
    table_data,
    photo_paths
):
    # -----------------------------
    # PDF 기본 설정
    # -----------------------------
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
        fontSize=18,
        alignment=1,  # 가운데
        spaceAfter=12
    )

    info_style = ParagraphStyle(
        "info",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=6
    )

    story = []

    # -----------------------------
    # 제목
    # -----------------------------
    story.append(Paragraph("현장 안전점검 보고서", title_style))
    story.append(Spacer(1, 12))

    # -----------------------------
    # 기본 정보
    # -----------------------------
    story.append(Paragraph(f"현장명: {site_name}", info_style))
    story.append(Paragraph(f"점검일자: {check_date}", info_style))
    story.append(Paragraph(f"점검자: {inspector}", info_style))
    story.append(Spacer(1, 16))

    # -----------------------------
    # 점검 결과 표
    # -----------------------------
    table = Table(
        table_data,
        colWidths=[60, 80, 60, 200]  # 모바일 기준 안정 폭
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # -----------------------------
    # 사진 섹션
    # -----------------------------
    if photo_paths:
        story.append(Paragraph("현장 사진", styles["Heading2"]))
        story.append(Spacer(1, 12))

        for idx, photo in enumerate(photo_paths):
            if not os.path.exists(photo):
                continue

            img = Image(photo)

            # 📱 모바일 기준 안전 사이즈
            img.drawWidth = 120 * mm
            img.drawHeight = img.drawWidth * 0.75

            story.append(img)
            story.append(Spacer(1, 12))

            # 사진 2장마다 페이지 분리 (가독성)
            if (idx + 1) % 2 == 0:
                story.append(PageBreak())

    # -----------------------------
    # PDF 생성
    # -----------------------------
    doc.build(story)

