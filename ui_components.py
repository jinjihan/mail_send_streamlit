"""UI 컴포넌트"""
import streamlit as st
import pandas as pd
from constants import EXAMPLE_COLUMNS, EXAMPLE_DATA, VARIABLE_HELP_TEXT, EXAMPLE_MESSAGE
from utils import load_template, build_html_from_text, validate_email, replace_variables, get_available_columns
from auth import show_logout_button


def show_variable_info(columns: list[str]):
    """사용 가능한 변수 정보 표시"""
    if columns:
        vars_text = ', '.join([f'`${{{col}}}`' for col in columns])
        st.info(f"💡 사용 가능한 변수: {vars_text}")


def show_example_guide():
    """사용 예시 가이드 표시"""
    with st.expander("📖 사용 예시"):
        st.markdown("**1단계: 컬럼 개수 및 이름 설정**")
        st.info("💡 첫 번째 컬럼은 '이메일'로 고정, 나머지는 자유롭게 변경 가능")
        
        st.markdown("**2단계: 엑셀에서 데이터 복사**")
        
        example_df = pd.DataFrame(EXAMPLE_DATA, columns=EXAMPLE_COLUMNS)
        st.dataframe(example_df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **3단계: 표에 붙여넣기 (Ctrl+V)**
        - 표의 첫 번째 셀 클릭 후 Ctrl+V
        - 또는 직접 입력/수정 가능
        
        **4단계: 메일에서 변수 사용**
        """)
        
        st.code(EXAMPLE_MESSAGE, language=None)
        
        st.markdown("**💡 변수 사용법**")
        st.info("컬럼명을 `${컬럼명}` 형태로 메일 본문이나 제목에 입력하면 해당 데이터로 치환됩니다.")


def render_header():
    """헤더 렌더링"""
    st.title("📧 메일 발송 시스템")
    st.markdown("---")


def render_send_mode() -> str:
    """발송 모드 선택"""
    st.subheader("1️⃣ 발송 모드")
    mode = st.radio("발송 방식을 선택하세요", ["단건 발송", "대량 발송"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    return mode


def render_subject() -> str:
    """메일 제목 입력"""
    st.subheader("2️⃣ 메일 제목")
    subject = st.text_input(
        "메일 제목을 입력하세요",
        value="[포텐데이] 메일 제목을 입력하세요.",
        placeholder=f"예: [포텐데이] ${{이름}}님, 안녕하세요!",
        help=VARIABLE_HELP_TEXT,
        label_visibility="collapsed"
    )
    st.markdown("---")
    return subject


def render_single_receiver() -> str:
    """단건 발송 수신자 입력"""
    return st.text_input("수신자 이메일 주소를 입력하세요", placeholder="example@example.com", label_visibility="collapsed")


def render_paste_input() -> pd.DataFrame | None:
    """대량 발송 수신자 입력 (표 형태)"""
    st.markdown("**표 형태로 입력**")
    st.info("💡 엑셀에서 복사(Ctrl+C) → 표에 붙여넣기(Ctrl+V) 또는 직접 입력")
    
    show_example_guide()
    
    # 컬럼명 설정
    col1, col2 = st.columns([1, 2])
    
    with col1:
        num_cols = st.number_input("컬럼 개수", min_value=2, max_value=10, value=2, step=1)
    
    with col2:
        if 'column_names' not in st.session_state:
            st.session_state.column_names = EXAMPLE_COLUMNS.copy()
    
        cols = st.columns(min(num_cols, 4))
        new_columns = []
        
        for i in range(num_cols):
            with cols[i % 4]:
                if i == 0:
                    # 첫 번째 컬럼은 이메일로 고정
                    col_name = "이메일"
                    st.text_input("컬럼1", value=col_name, disabled=True, key=f"col_{i}")
                else:
                    if i == 1:
                        default_name = "이름"
                    else:
                        default_name = f"컬럼{i+1}"
                    col_name = st.text_input(
                        f"컬럼{i+1}", 
                        value=st.session_state.column_names[i] if i < len(st.session_state.column_names) else default_name,
                        key=f"col_{i}",
                        placeholder=f"컬럼{i+1}"
                    )
                new_columns.append(col_name)
        
        st.session_state.column_names = new_columns
    
    # 표 초기화
    if 'paste_df' not in st.session_state or len(st.session_state.paste_df.columns) != num_cols:
        st.session_state.paste_df = pd.DataFrame(
            [[''] * num_cols for _ in range(5)],
            columns=st.session_state.column_names
        )
    
    # 컬럼 설정
    column_config = {}
    for i, col_name in enumerate(st.session_state.column_names):
        column_config[col_name] = st.column_config.TextColumn(
            col_name, 
            width="medium", 
            required=(i == 0)
        )
    
    edited_df = st.data_editor(
        st.session_state.paste_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
        key="paste_editor"
    )
    
    # 빈 행 제거
    email_col = st.session_state.column_names[0]
    df = edited_df[edited_df[email_col].notna() & (edited_df[email_col] != '')].copy()
    
    if len(df) == 0:
        return None
    
    df = df.reset_index(drop=True)
    
    # 이메일 유효성 검사
    invalid = [email for email in df[email_col] if not validate_email(email)]
    if invalid:
        st.warning(f"⚠️ 유효하지 않은 이메일: {', '.join(invalid[:5])}")
    
    st.success(f"✅ 총 {len(df)}명")
    show_variable_info(get_available_columns(df))
    
    return df


def render_bulk_receiver() -> pd.DataFrame | None:
    """대량 발송 수신자 렌더링"""
    return render_paste_input()


def render_receiver(send_mode: str) -> tuple[str | None, pd.DataFrame | None]:
    """수신자 입력"""
    st.subheader("3️⃣ 수신자")
    
    if send_mode == "단건 발송":
        email = render_single_receiver()
        df = None
    else:
        email = None
        df = render_bulk_receiver()
    
    st.markdown("---")
    return email, df


def render_text_editor() -> str:
    """텍스트 편집기"""
    st.markdown("**본문 텍스트**")
    st.caption(f"💡 {VARIABLE_HELP_TEXT}")
    
    if 'default_body' not in st.session_state:
        st.session_state.default_body = "메일 내용을 입력하세요."
    
    text = st.text_area(
        "메일 본문을 입력하세요",
        value=st.session_state.default_body,
        height=400,
        placeholder=EXAMPLE_MESSAGE,
        help=VARIABLE_HELP_TEXT,
        label_visibility="collapsed"
    )
    
    return build_html_from_text(text)


def render_html_editor() -> str:
    """HTML 편집기"""
    st.markdown("**HTML 편집**")
    st.caption(f"💡 {VARIABLE_HELP_TEXT}")
    
    if 'template' not in st.session_state:
        st.session_state.template = load_template()
    
    html = st.text_area(
        "HTML 코드를 입력하세요",
        value=st.session_state.template,
        height=400,
        help=VARIABLE_HELP_TEXT,
        label_visibility="collapsed"
    )
    
    return html


def render_body(df: pd.DataFrame | None = None) -> str:
    """메일 본문 편집"""
    st.subheader("4️⃣ 메일 본문")
    
    if df is not None:
        show_variable_info(get_available_columns(df))
    
    mode = st.radio("편집 모드를 선택하세요", ["📝 텍스트", "💻 HTML"], horizontal=True, label_visibility="collapsed")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        content = render_text_editor() if mode == "📝 텍스트" else render_html_editor()
    
    with col2:
        st.markdown("**미리보기**")
        preview = content
        if df is not None and len(df) > 0:
            preview = replace_variables(preview, df.iloc[0].to_dict())
        with st.container(height=400):
            st.html(preview)
    
    st.markdown("---")
    return content


def render_attachment():
    """파일 첨부"""
    st.subheader("5️⃣ 파일 첨부 (선택)")
    file = st.file_uploader(
        "파일",
        type=['zip', 'pdf', 'xlsx', 'xls', 'jpg', 'png', 'docx'],
        label_visibility="collapsed"
    )
    st.markdown("---")
    return file


def render_send_buttons() -> tuple[bool, bool]:
    """발송 버튼"""
    st.subheader("6️⃣ 발송")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        test = st.button("🧪 테스트", type="secondary", use_container_width=True)
    with col2:
        send = st.button("📤 실제 발송", type="primary", use_container_width=True)
    
    return test, send


def render_sidebar(config):
    """사이드바"""
    with st.sidebar:
        st.header("ℹ️ 정보")
        st.markdown(f"""
        **발신자**: {config.sender_name}  
        **발신 이메일**: {config.sender_email}  
        **테스트 수신 이메일**: {config.admin_email}
        
        ---
        
        ### 📝 사용 순서
        1. 발송 모드 선택
        2. 제목 입력
        3. 수신자 입력
        4. 본문 작성
        5. 파일 첨부 (선택)
        6. 발송
        
        ---
        
        ### 💡 변수 사용
        **메일 제목**, **메일 본문**에서 사용 가능

        `${{이름}}` → 홍길동  
        `${{포지션}}` → 서비스 기획자
        
        **예시:**
        ```
        안녕하세요 ${{이름}}님!
        ${{포지션}} 포지션 관련 안내드립니다.
        ```
        ->
        ```
        안녕하세요 홍길동님!
        서비스 기획자 포지션 관련 안내드립니다.
        ```
        
        ---
        
        ### 📋 대량 발송
        
        엑셀에서 복사 → 표에 붙여넣기 (Ctrl+V)
        
        | {' | '.join(EXAMPLE_COLUMNS)} |
        |{'|'.join(['---'] * len(EXAMPLE_COLUMNS))}|
        | {' | '.join(EXAMPLE_DATA[0])} |
        | {' | '.join(EXAMPLE_DATA[1])} |
        """)
    
    show_logout_button()

