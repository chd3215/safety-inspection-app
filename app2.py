import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image, ImageOps
from io import BytesIO
import os

# 라이브러리 임포트
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 1. 폰트 및 로그 설정 (NanumGothic.ttf 파일 필요)
# ==========================================
FONT_NAME = "NanumGothic"
FONT_PATH = "NanumGothic.ttf"  # 파일이 앱과 같은 폴더에 있어야 함

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    HAS_FONT = True
else:
    HAS_FONT = False

def save_log(data):
    LOG_FILE = "inspection_log.csv"
    df = pd.DataFrame([data])
    df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False, encoding="utf-8-sig")

# ==========================================
# 2. 스트림릿 UI 구성
# ==========================================
st.set_page_config(page_title="안전점검 리포트 시스템", layout="centered")

if not HAS_FONT:
    st.error(f"⚠️ '{FONT_PATH}' 파일을 찾을 수 없습니다. PDF 한글이 깨질 수 있습니다.")

st.title("🏗️ 안전점검 결과 보고서")

with st.form("inspection_form"):
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
    
    uploaded_files = st.file_uploader("점검 사진 업로드 (여러 장 가능)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    submitted = st.form_submit_button("정보 확인 완료")

# 서명란은 Form 밖에 위치 (Canvas 특성상)
st.write("---")
st.subheader("✍️ 점검자 서명")
canvas_result = st_canvas(
    stroke_width=2, 
    stroke_color="#000", 
    background_color="#f0f0f0", 
    height=120, 
    width=250, 
    drawing_mode="freedraw", 
    key="canvas"
)

# ==========================================
# 3. PDF 생성 로직 (표 내부 한글 깨짐 방지 적용)
# ==========================================
def create_professional_pdf(sig_img):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    
    # 사용할 폰트 결정
    curr_font = FONT_NAME if HAS_FONT else "Helvetica"
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', fontName=curr_font, fontSize=20, alignment=1, spaceAfter=20)
    body_style = ParagraphStyle('B', fontName=curr_font, fontSize=10, leading=14)

    # (1) 문서 제목
    elements.append(Paragraph("안 전 점 검 결 과 보 고 서", title_style))

    # (2) 결재란 (표 내부 폰트 설정 적용)
    approval_data = [
        ["담당", "팀장", "소장"],
        ["", "", ""]
    ]
    app_table = Table(approval_data, colWidths=[20*mm]*3, rowHeights=[7*mm, 15*mm])
    app_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), curr_font), # <-- 표 내부 한글 적용
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    
    top_table = Table([[None, app_table]], colWidths=[120*mm, 60*mm])
    top_table.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT')]))
    elements.append(top_table)
    elements.append(Spacer(1, 5*mm))

    # (3) 메인 정보 표 (표 내부 폰트 설정 적용)
    # 서명 이미지 준비
    sig_tmp = BytesIO()
    sig_img.save(sig_tmp, format="PNG")
    sig_tmp.seek(0)
    rl_sig = RLImage(sig_tmp, width=20*mm, height=10*mm)

    main_data = [
        ["공 사 명", site_name, "점검일자", str(inspection_date)],
        ["점검장소", location, "점 검 자", inspector],
        ["점검항목", item_name, "조치상태", action],
        ["위험요인", ", ".join(risk), "확 인", rl_sig], 
    ]

    t1 = Table(main_data, colWidths=[25*mm, 65*mm, 25*mm, 65*mm], rowHeights=10*mm)
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), curr_font), # <-- 표 내부 한글 적용
        ('BACKGROUND', (0,0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2,0), (2, -1), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t1)

    # (4) 상세 내용 표
    content_data = [
        ["점검 결과 및 조치요구 사항"],
        [Paragraph(remarks.replace("\n", "<br/>"), body_style)],
        ["점검 사진 실사"]
    ]
    
    t2 = Table(content_data, colWidths=[180*mm])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), curr_font), # <-- 표 내부 한글 적용
        ('BACKGROUND', (0,0), (0,0), colors.lightgrey),
        ('BACKGROUND', (0,2), (0,2), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('MINSIZE', (0,1), (0,1), 40*mm),
    ]))
    elements.append(t2)

    # (5) 사진 격자 배치 (표 내부 폰트 설정 적용)
    if uploaded_files:
        photo_cells = []
        temp_row = []
        for f in uploaded_files:
            img = Image.open(f)
            img = ImageOps.exif_transpose(img)
            img_io = BytesIO()
            img.save(img_io, format="JPEG", quality=75)
            img_io.seek(0)
            temp_row.append(RLImage(img_io, width=85*mm, height=65*mm, kind='proportional'))
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

# ==========================================
# 4. 발행 버튼 및 실행
# ==========================================
if st.button("🚀 리포트 최종 발행 및 PDF 다운로드", use_container_width=True):
    if not site_name or not inspector:
        st.error("공사명과 점검자 이름은 필수입니다.")
    elif canvas_result.image_data is None:
        st.warning("점검자 서명을 완료해주세요.")
    else:
        with st.spinner("PDF 리포트를 생성 중입니다..."):
            # 서명 이미지 처리
            sig_img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            
            # PDF 생성
            pdf_file = create_professional_pdf(sig_img)
            
            # 로그 기록
            save_log({
                "날짜": inspection_date, 
                "공사명": site_name, 
                "점검자": inspector, 
                "항목": item_name,
                "상태": action
            })
            
            st.success("✅ 리포트가 성공적으로 생성되었습니다!")
            st.download_button(
                label="📥 PDF 저장하기", 
                data=pdf_file, 
                file_name=f"안전점검_{inspection_date}_{site_name}.pdf", 
                mime="application/pdf",
                use_container_width=True
            )