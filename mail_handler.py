"""메일 발송 처리"""
import streamlit as st
import pandas as pd
from email_sender import EmailSender
from config import Config


def validate_input(subject: str, content: str, mode: str, email: str | None, df: pd.DataFrame | None) -> bool:
    """입력값 검증"""
    if not subject:
        st.error("❌ 제목을 입력하세요.")
        return False
    if not content:
        st.error("❌ 본문을 입력하세요.")
        return False
    if mode == "단건 발송" and not email:
        st.error("❌ 수신자 이메일을 입력하세요.")
        return False
    if mode == "대량 발송" and (df is None or len(df) == 0):
        st.error("❌ 수신자 목록을 입력하세요.")
        return False
    return True


def handle_test_send(subject: str, content: str, attachment, email_sender: EmailSender, config: Config):
    """테스트 메일 발송"""
    if not subject or not content:
        st.error("❌ 제목과 본문을 입력하세요.")
        return
    
    st.info(f"📤 테스트 메일을 {config.admin_email}로 발송 시작...")
    
    with st.spinner(f"테스트 발송 중..."):
        success, error = email_sender.send_mail(
            subject=f"[테스트] {subject}",
            html_content=content,
            receiver_email=config.admin_email,
            attachment_file=attachment
        )
    
    if success:
        st.success(f"✅ {config.admin_email}로 테스트 발송 완료!")
    else:
        st.error(f"❌ 테스트 발송 실패: {error}")
        st.error("💡 SMTP 설정을 확인해주세요.")


def send_single(subject: str, content: str, email: str, attachment, email_sender: EmailSender):
    """단건 메일 발송"""
    st.info(f"📤 {email}로 메일 발송 시작...")
    
    with st.spinner("발송 중..."):
        success, error = email_sender.send_mail(
            subject=subject,
            html_content=content,
            receiver_email=email,
            attachment_file=attachment
        )
    
    if success:
        st.success(f"✅ {email}로 발송 완료!")
    else:
        st.error(f"❌ 발송 실패: {error}")
        st.error("💡 SMTP 설정을 확인해주세요.")


def send_bulk(subject: str, content: str, df: pd.DataFrame, attachment, email_sender: EmailSender):
    """대량 메일 발송"""
    st.info(f"📤 {len(df)}명에게 메일 발송 시작...")
    
    with st.spinner(f"{len(df)}명에게 발송 중..."):
        success, results = email_sender.send_bulk_mail(
            subject=subject,
            html_content=content,
            df=df,
            attachment_file=attachment
        )
    
    if success:
        st.success("✅ 발송 완료!")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)
        
        csv = results_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 결과 다운로드", csv, "results.csv", "text/csv")
    else:
        st.error(f"❌ 발송 실패: {results}")
        st.error("💡 SMTP 설정을 확인해주세요.")


def handle_send(mode: str, subject: str, content: str, email: str | None, df: pd.DataFrame | None, attachment, email_sender: EmailSender):
    """메일 발송 처리"""
    if not validate_input(subject, content, mode, email, df):
        return
    
    if mode == "단건 발송":
        send_single(subject, content, email, attachment, email_sender)
    else:
        send_bulk(subject, content, df, attachment, email_sender)

