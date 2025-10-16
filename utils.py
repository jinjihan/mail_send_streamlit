"""유틸리티 함수"""
import re
import pandas as pd
from pathlib import Path


def load_template() -> str:
    """HTML 템플릿 로드"""
    template_path = Path("template/primary_mail.html")
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return "<html><body><p>메일 내용을 입력하세요.</p></body></html>"


def build_html_from_text(body_text: str) -> str:
    """텍스트를 HTML 템플릿에 삽입"""
    template_path = Path("template/primary_mail.html")
    if not template_path.exists():
        return f"<html><body><p>{body_text}</p></body></html>"
    
    html_template = template_path.read_text(encoding='utf-8')
    body_html = body_text.replace('\n', '<br>\n                ')
    pattern = r'(<p style="color: #000; font-size: 16px; line-height: 34px; margin: 0px;">)(.*?)(</p>)'
    return re.sub(pattern, rf'\1\n                {body_html}\n            \3', html_template, flags=re.DOTALL)


def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    return '@' in email and '.' in email


def replace_variables(text: str, row_data: dict) -> str:
    """텍스트 내 변수를 실제 데이터로 치환"""
    result = text
    for key, value in row_data.items():
        result = result.replace(f"${{{key}}}", str(value))
    return result


def get_available_columns(df: pd.DataFrame | None) -> list[str]:
    """사용 가능한 컬럼 목록 반환 (이메일 제외)"""
    if df is None or df.empty:
        return []
    return [col for col in df.columns if col != '이메일']

