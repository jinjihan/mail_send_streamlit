"""메일 발송 시스템"""
import streamlit as st
from config import Config
from email_sender import EmailSender
from auth import is_authenticated, show_login_form
from ui_components import (
    render_header,
    render_send_mode,
    render_subject,
    render_receiver,
    render_body,
    render_attachment,
    render_send_buttons,
    render_sidebar
)
from mail_handler import handle_test_send, handle_send


st.set_page_config(page_title="메일 발송 시스템", page_icon="📧", layout="wide")


def main():
    """메인 함수"""
    # 인증 체크
    if not is_authenticated():
        show_login_form()
        return
    
    # 인증 완료 후 Config 및 EmailSender 초기화
    config = Config()
    email_sender = EmailSender(config)
    
    # UI 렌더링
    render_header()
    
    mode = render_send_mode()
    subject = render_subject()
    email, df = render_receiver(mode)
    content = render_body(df if mode == "대량 발송" else None)
    attachment = render_attachment()
    
    # 발송 전 경고 메시지
    if mode == "단건 발송" and email:
        st.warning(f"⚠️ **{email}**로 메일이 발송됩니다.")
    elif mode == "대량 발송" and df is not None and len(df) > 0:
        st.warning(f"⚠️ **{len(df)}명**에게 메일이 발송됩니다.")
    
    test, send = render_send_buttons()
    
    render_sidebar(config)
    
    # 발송 처리
    if test:
        handle_test_send(subject, content, attachment, email_sender, config)
    
    if send:
        handle_send(mode, subject, content, email, df, attachment, email_sender)


if __name__ == "__main__":
    main()
