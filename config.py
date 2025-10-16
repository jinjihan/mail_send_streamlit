"""설정 관리"""
import streamlit as st


class Config:
    def __init__(self):
        try:
            self.smtp_host = st.secrets["smtp"]["host"]
            self.smtp_port = st.secrets["smtp"]["port"]
            self.smtp_user = st.secrets["smtp"]["user"]
            self.smtp_password = st.secrets["smtp"]["password"]
            self.sender_name = st.secrets["sender"]["name"]
            self.sender_email = st.secrets["sender"]["email"]
            self.admin_email = st.secrets["admin"]["email"]
        except Exception as e:
            st.error(f"⚠️ 설정 파일(.streamlit/secrets.toml)을 확인하세요.\n오류: {e}")
            st.stop()
