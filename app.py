import streamlit as st
import os
import json
from datetime import datetime
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# =============================
# 한글 폰트
# =============================
pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))

# =============================
# 폴더 설정
# =============================
BASE_PHOTO_DIR = "site_photos"
PDF_DIR = "pdf_output"
CHECKLIST_DIR = "checklists"

for d in [BASE_PHOTO_DIR, PDF_DIR, CHECKLIST_DIR]:
    os.makedirs(d, exist_ok=True)

st.set_page_config(page_title="현장 안전점검 앱", page_icon="🦺", layout="centered")
st.title("🦺 현장 일일안전점검 앱")

# =============================
# 기본 정보
# =============================
site_name = st.text_input("현장명", placeholder="예: 현장A")
check_date = st.date_input("점검일자", value=datetime.today())
inspector = st.text_input("점검자", placeholder="홍길동")

st.divider()

# =============================
# 체크리스트 로드
# =============================
checklist_path = os.path.join(CHECKLIST_DIR, f"{site_name}.json")
default_items = [
    "보호구 착용 상태",
    "추락 위험 방지 조치",
    "전기 설비 안전 상태",
    "작업장 정리정돈",
    "위험물 보관 상태",
]

if os.path.exists(checklist_path):
    with open(checklist_path, "r", encoding="utf-8") as f:
        saved_items = json.load(f)
else:
    saved_items = default_items

st.subheader("✅ 안전 점검 항목 (현장별 저장)")

check_items = {}
for item in saved_items:
    check_items[item] = st.checkbox(item, value=False)

# =============================
# 체크리스트 저장 버튼
# =============================
if st.button("💾 체크리스트 저장"):
    if site_name:
        with open(checklist_path, "w", encoding="utf-8") as f:
            json.dump(list(check_items.keys()), f, ensure_ascii=False, indent=2)
        st.success("✅ 체크리스트 저장 완료")
    else:
        st.warning("현장명을 입력하세요.")

st.divider()

# =============================
# 사진 업로드
# =============================
uploaded_files = st.file_uploader(
    "📸 현장 사진 업로드",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

photo_comments = {}

if uploaded_files:
    st.subheader("✍ 사진별 위험요인 / 조치내용")
    for idx, file in enumerate(uploaded_files, start=1):
        st.image(file, width=250)
        photo_comments[f"{idx}.jpg"] = st.text_area(
            f"{idx}번 사진 코멘트",
            key=f"comment_{idx}"
        )

if st.button("📂 사진 저장"):
    if site_name and uploaded_files:
        site_folder = os.path.join(BASE_PHOTO_DIR, site_name)
        os.makedirs(site_folder, exist_ok=True)

        for idx, file in enumerate(uploaded_files, start=1):
            Image.open(file).save(os.path.join(site_folder, f"{idx}.jpg"))

        st.success("✅ 사진 저장 완료")
    else:
        st.warning("현장명과 사진을 입력하세요.")

# =============================
# PDF 생성 함수
# =============================
def create_pdf(site_name, check_date, inspector, check_items, photo_comments):
    pdf_path = os.path.join(PDF_DIR, f"{site_name}_일일안전점검일지.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)

    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", fontName="HYSMyeongJo-Medium", fontSize=18, alignment=1)

    story = [Paragraph("일일 안전점검 일지", title)]

    info = Table([
        ["현장명", site_name],
        ["점검일자", str(check_date)],
        ["점검자", inspector],
    ], colWidths=[100, 300])

    info.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONT", (0,0), (-1,-1), "HYSMyeongJo-Medium"),
    ]))

    story.append(info)

    checklist = [["점검 항목", "결과"]]
    for k, v in check_items.items():
        checklist.append([k, "양호" if v else "미흡"])

    table = Table(checklist, colWidths=[300, 100])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONT", (0,0), (-1,-1), "HYSMyeongJo-Medium"),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    story.append(table)

    site_folder = os.path.join(BASE_PHOTO_DIR, site_name)
    if os.path.exists(site_folder):
        for img in sorted(os.listdir(site_folder)):
            story.append(RLImage(os.path.join(site_folder, img), width=400, height=300))
            story.append(Paragraph(photo_comments.get(img, ""), styles["Normal"]))

    doc.build(story)
    return pdf_path

# =============================
# PDF 생성
# =============================
if st.button("📄 PDF 생성"):
    if site_name:
        pdf_file = create_pdf(site_name, check_date, inspector, check_items, photo_comments)
        st.success("✅ PDF 생성 완료")
        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ PDF 다운로드", f, os.path.basename(pdf_file))
    else:
        st.warning("현장명을 입력하세요.")

