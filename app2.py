import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image, ImageOps
from io import BytesIO
import os

from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# 폰트 설정 (현장명에 맞게 NanumGothic.ttf 파일이 있어야 함)
FONT_NAME = "NanumGothic"
FONT_PATH = "NanumGothic.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    HAS_FONT = True
else:
    HAS_FONT = False

def save_log(data):
    LOG_FILE = "inspection_log.csv"
    df = pd.DataFrame([data])
    df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False, encoding="utf-8-sig")

st.set_page_config(page_title="안전점검 리포트", layout="centered")

# --- UI 입력부 ---
st.title("🏗️ 안전점검 결과 보고서")

with st.container():
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        site_name = st.text_input("공사명", value="OO지구 신축공사")
        location = st.text_input("점검장소", placeholder="예: 101동 주변")
    with col_info2:
        inspection_date = st.date_input("점검일시", value=date.today())
        inspector = st.text_input("점검자", value="홍길동")

    item_name = st.text_input("점검항목", placeholder="내용을 입력하세요")
    
    col_info3, col_info4 = st.columns(2)
    with col_info3:
        risk = st.multiselect("위험요인", ["추락", "낙하", "붕괴", "감전", "화재", "전도"])
    with col_info4:
        action = st.selectbox("조치상태", ["즉시조치", "조치예정", "해당없음"])

    remarks = st.text_area("점검 결과 및 조치요구 사항", height=100)

st.write("---")
st.subheader("✍️ 서명 및 사진")
c1, c2 = st.columns([1, 1])
with c1:
    st.write("점검자 서명")
    canvas_result = st_canvas(stroke_width=2, stroke_color="#000", background_color="#f0f0f0", height=120, width=250, drawing_mode="freedraw", key="canvas")
with c2:
    uploaded_files = st.file_uploader("사진 업로드", type=["jpg", "png"], accept_multiple_files=True)

# --- PDF 생성 로직 ---
def create_professional_pdf(sig_img):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    
    f_name = FONT_NAME if HAS_FONT else "Helvetica"
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', fontName=f_name, fontSize=18, alignment=1, spaceAfter=15)
    body_style = ParagraphStyle('B', fontName=f_name, fontSize=10, leading=14)

    # 1. 문서 제목
    elements.append(Paragraph("안 전 점 검 결 과 보 고 서", title_style))

    # 2. 결재란 (상단 우측 배치용 표)
    approval_data = [
        ["담당", "팀장", "소장"],
        ["", "", ""]
    ]
    app_table = Table(approval_data, colWidths=[20*mm]*3, rowHeights=[7*mm, 15*mm])
    app_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), f_name),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    
    # 결재란을 우측으로 밀기 위해 전체 너비 표 안에 배치
    top_table = Table([[None, app_table]], colWidths=[120*mm, 60*mm])
    top_table.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT')]))
    elements.append(top_table)
    elements.append(Spacer(1, 5*mm))

    # 3. 메인 정보 표
    main_data = [
        ["공 사 명", site_name, "점검일자", str(inspection_date)],
        ["점검장소", location, "점 검 자", inspector],
        ["점검항목", item_name, "조치상태", action],
        ["위험요인", ", ".join(risk), "확 인", ""], # 서명 들어갈 자리
    ]
    
    # 서명 이미지 넣기
    sig_tmp = BytesIO()
    sig_img.save(sig_tmp, format="PNG")
    sig_tmp.seek(0)
    rl_sig = RLImage(sig_tmp, width=20*mm, height=10*mm)
    main_data[3][3] = rl_sig # 확인 칸에 서명 이미지 삽입

    t1 = Table(main_data, colWidths=[25*mm, 65*mm, 25*mm, 65*mm], rowHeights=10*mm)
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), f_name),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('BACKGROUND', (2,0), (2,-1), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t1)

    # 4. 상세 내용 및 사진 (격자 형태)
    content_data = [
        ["점검 결과 및 조치요구 사항"],
        [Paragraph(remarks.replace("\n", "<br/>"), body_style)],
        ["점검 사진"]
    ]
    
    t2 = Table(content_data, colWidths=[180*mm])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (0,0), 0.5, colors.black),
        ('GRID', (0,1), (0,1), 0.5, colors.black),
        ('GRID', (0,2), (0,2), 0.5, colors.black),
        ('BACKGROUND', (0,0), (0,0), colors.lightgrey),
        ('BACKGROUND', (0,2), (0,2), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('MINSIZE', (0,1), (0,1), 40*mm), # 내용 칸 최소 높이
    ]))
    elements.append(t2)

    # 사진 배치 (2장씩)
    if uploaded_files:
        photo_cells = []
        temp_row = []
        for f in uploaded_files:
            img = Image.open(f)
            img = ImageOps.exif_transpose(img)
            img_io = BytesIO()
            img.save(img_io, format="JPEG", quality=70)
            img_io.seek(0)
            temp_row.append(RLImage(img_io, width=85*mm, height=60*mm, kind='proportional'))
            if len(temp_row) == 2:
                photo_cells.append(temp_row)
                temp_row = []
        if temp_row: photo_cells.append(temp_row + [""])
        
        if photo_cells:
            photo_table = Table(photo_cells, colWidths=[90*mm, 90*mm])
            photo_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            elements.append(photo_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("📝 리포트 최종 발행", use_container_width=True):
    if canvas_result.image_data is not None:
        sig_img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        pdf_file = create_professional_pdf(sig_img)
        
        save_log({"날짜": inspection_date, "현장": site_name, "점검자": inspector, "항목": item_name})
        
        st.success("리포트가 생성되었습니다.")
        st.download_button("📥 PDF 다운로드", pdf_file, f"안전점검_{inspection_date}.pdf", "application/pdf")