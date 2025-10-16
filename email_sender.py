"""메일 발송"""
import smtplib
import ssl
import time
import pandas as pd
from email import encoders
from email.header import Header
from email.utils import formataddr
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self, config):
        self.config = config
    
    def build_message(self, subject: str, html_content: str, receiver_email: str, attachment_file=None) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = str(Header(subject, "utf-8"))
        msg["From"] = formataddr((str(Header(self.config.sender_name, "utf-8")), self.config.sender_email))
        msg["To"] = receiver_email
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        if attachment_file:
            self._attach_file(msg, attachment_file)

        return msg
    
    def _attach_file(self, msg: MIMEMultipart, file):
        file_bytes = file.read()
        file_name = file.name
        
        mime_type = self._get_mime_type(file_name)
        part = MIMEBase(*mime_type.split("/"))
        part.set_payload(file_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", file_name))
        msg.attach(part)
        file.seek(0)
    
    def _get_mime_type(self, file_name: str) -> str:
        mime_types = {
            '.zip': "application/zip",
            '.pdf': "application/pdf",
            '.xlsx': "application/vnd.ms-excel",
            '.xls': "application/vnd.ms-excel",
            '.jpg': "image/jpeg",
            '.jpeg': "image/jpeg",
            '.png': "image/png",
            '.docx': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        
        for ext, mime in mime_types.items():
            if file_name.endswith(ext):
                return mime
        return "application/octet-stream"
    
    def send_mail(self, subject: str, html_content: str, receiver_email: str, attachment_file=None) -> tuple[bool, str | None]:
        try:
            with self._create_smtp() as server:
                msg = self.build_message(subject, html_content, receiver_email, attachment_file)
                server.send_message(msg)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def _create_smtp(self):
        context = ssl.create_default_context()
        server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
        server.ehlo()
        server.starttls(context=context)
        server.login(self.config.smtp_user, self.config.smtp_password)
        return server
    
    def send_bulk_mail(self, subject: str, html_content: str, df: pd.DataFrame, attachment_file=None, sleep_seconds: float = 0.5) -> tuple[bool, list | str]:
        results = []
        
        try:
            with self._create_smtp() as server:
                for idx, row in df.iterrows():
                    receiver = str(row["이메일"]).strip()
                    row_data = row.to_dict()
                    
                    personalized_subject = self._replace_vars(subject, row_data)
                    personalized_html = self._replace_vars(html_content, row_data)
                    
                    result = self._send_one(server, personalized_subject, personalized_html, receiver, attachment_file)
                    results.append(result)
                    time.sleep(sleep_seconds)
            
            return True, results
        except Exception as e:
            return False, str(e)
    
    def _replace_vars(self, text: str, data: dict) -> str:
        result = text
        for key, value in data.items():
            result = result.replace(f"${{{key}}}", str(value))
        return result
    
    def _send_one(self, server, subject: str, html: str, receiver: str, attachment) -> dict:
        try:
            msg = self.build_message(subject, html, receiver, attachment)
            server.send_message(msg)
            return {"이메일": receiver, "상태": "✅ 성공"}
        except Exception as e:
            return {"이메일": receiver, "상태": f"❌ 실패: {str(e)}"}
