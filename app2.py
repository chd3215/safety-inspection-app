# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF  # PDF 생성용 → pip install fpdf
import io

# 페이지 설정 (wide 모드 + 제목)
st.set_page_config(
    page_title="현장안전점검 앱",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🔨"
)

# 커스텀 CSS (UI 크게 만들기)
st.markdown("""
<style>
    .stApp { font-size: 18px !important; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 20px !important;
        padding: 12px !important;
        height: 50px !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label {
        font-size: 22px !important;
        font-weight: bold;
    }
    .stSelectbox > div > div > select {
        font-size: 20px !important;
        padding: 10px !important;
    }
    button[kind="primary"], button[kind="secondary"] {
        font-size: 20px !important;
        padding: 14px 28px !important;
        min-height: 60px !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] {
        font-size: 18px !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        min-height: 300px !important;
        font-size: 24px !important;
        border: 3px dashed #4CAF50 !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 95% !important;
    }
</style>
""", unsafe_allow_html=True)

# 제목
st.title("🔨 현장안전점검 통합")

# 입력 영역 (컬럼으로 나누어 레이아웃)
col_left, col_right = st.columns([1, 3])

with col_left:
    site_name = st.text_input("현장명", placeholder="현장명을 입력하세요")
    inspector = st.text_input("점검자", placeholder="이름 입력")
    check_date = st.date_input("점검일자", value=datetime.today())

with col_right:
    st.subheader("점검 항목")

    # session_state 초기화
    if 'items' not in st.session_state:
        st.session_state.items = []

    # 새 항목 입력
    new_item = st.text_input("점검항목", key="new_item_input")
    status = st.selectbox("상태", ["양호", "보통", "불량", "미확인"], key="status_select")
    note = st.text_area("비고", height=80, key="note_area")

    if st.button("항목 추가", type="primary"):
        if new_item.strip():
            st.session_state.items.append({
                "번호": len(st.session_state.items) + 1,
                "점검항목": new_item.strip(),
                "상태": status,
                "비고": note.strip()
            })
            # 입력창 초기화 위해 rerun
            st.rerun()
        else:
            st.warning("점검항목을 입력해주세요.")

    # 테이블 표시
    if st.session_state.items:
        try:
            df = pd.DataFrame(st.session_state.items)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        except Exception as e:
            st.error(f"테이블 표시 오류: {e}")
            st.write("현재 항목 데이터:", st.session_state.items)
    else:
        st.info("아직 추가된 점검 항목이 없습니다.")

# 사진 업로드
st.subheader("현장 사진")
photos = st.file_uploader(
    "사진 업로드 (여러 장 가능, JPG/PNG)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if photos:
    st.write(f"업로드된 사진: {len(photos)}장")
    cols = st.columns(3)
    for idx, photo in enumerate(photos):
        with cols[idx % 3]:
            st.image(photo, use_column_width=True, caption=f"사진 {idx+1}")

# PDF 생성
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)  # 한글 폰트 (필요 시 다운로드)
    pdf.set_font("DejaVu", size=12)

    pdf.cell(200, 10, txt=f"현장안전점검 보고서 - {check_date}", ln=1, align='C')
    pdf.cell(200, 10, txt=f"현장명: {site_name}   점검자: {inspector}", ln=1)

    pdf.ln(10)
    pdf.cell(200, 10, txt="점검 항목 목록", ln=1)

    if st.session_state.items:
        pdf.set_font("DejaVu", size=10)
        col_widths = [20, 70, 40, 60]
        headers = ["번호", "점검항목", "상태", "비고"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1)
        pdf.ln()

        for item in st.session_state.items:
            pdf.cell(col_widths[0], 10, str(item["번호"]), border=1)
            pdf.cell(col_widths[1], 10, item["점검항목"], border=1)
            pdf.cell(col_widths[2], 10, item["상태"], border=1)
            pdf.cell(col_widths[3], 10, item["비고"], border=1)
            pdf.ln()

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

if st.button("PDF 생성 및 다운로드", type="primary", use_container_width=True):
    if not site_name or not inspector:
        st.warning("현장명과 점검자를 입력해주세요.")
    else:
        pdf_data = create_pdf()
        st.download_button(
            label="PDF 다운로드",
            data=pdf_data,
            file_name=f"안전점검_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )
        st.success("PDF 생성 완료! 다운로드 버튼을 눌러 저장하세요.")

# 끝
st.markdown("---")
st.caption("포항 현장 맞춤 안전점검 앱 ")