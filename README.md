# 📧 메일 발송 시스템

Streamlit 기반 메일 발송 시스템

## 🚀 빠른 시작

### 1. 설치
```bash
pip install -r requirements.txt
```

### 2. 설정
`.streamlit/secrets.toml` 파일 생성 (`.streamlit/secrets.toml.example` 참고):

```toml
[smtp]
host = "smtp.gmail.com"
port = 587
user = "your-email@gmail.com"
password = "your-app-password"

[sender]
name = "발신자 이름"
email = "sender@example.com"
 
[admin]
email = "admin@example.com"

[users]
username = "sha256_hashed_password"
```

**Gmail 앱 비밀번호 발급:**
1. Google 계정 → 보안 → 2단계 인증 활성화
2. 보안 → 앱 비밀번호 생성
3. 생성된 비밀번호를 `password`에 입력

**사용자 비밀번호 해시 생성:**
```python
import hashlib
password = "your_password"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)
```

### 3. 실행
```bash
streamlit run app.py
```

## 📋 주요 기능

### 발송 모드
- **단건**: 1명에게 발송
- **대량**: 여러 명에게 동시 발송 (변수 치환 지원)
  - 표 형태로 입력: 엑셀에서 복사 → 표에 붙여넣기 또는 직접 입력

### 변수 치환 ✨
대량 발송 시 수신자별 개인화:

**엑셀 데이터:**
| 이메일 | 이름 | 포지션 |
|---|---|---|
| hong@example.com | 홍길동 | 서비스 기획자 |
| kim@example.com | 김철수 | 프로덕트 디자이너 |

**메일 작성:**
```
제목: [포텐데이] ${이름}님, 안녕하세요!

본문:
안녕하세요 ${이름}님!
${포지션} 직무 역량을 키울 수 있는 프로그램 추천드려요.
```

**발송 결과:**
- 홍길동님 → "안녕하세요 홍길동님! 서비스 기획자 직무..."
- 김철수님 → "안녕하세요 김철수님! 프로덕트 디자이너 직무..."

### 기타
- 실시간 미리보기
- 파일 첨부 (ZIP, PDF, Excel, 이미지, Word)
- 테스트 발송
- 결과 다운로드 (CSV)

## 📁 구조

```
mail_send_streamlit/
├── app.py              # 메인 애플리케이션
├── auth.py             # 인증 및 사용자 관리
├── config.py           # 설정 로드
├── constants.py        # 상수 정의
├── email_sender.py     # 메일 발송 로직
├── mail_handler.py     # 메일 발송 처리
├── ui_components.py    # UI 컴포넌트
├── utils.py            # 유틸리티 함수
├── requirements.txt    # 패키지 목록
├── .streamlit/
│   └── secrets.toml.example  # 설정 파일 예시
└── template/
    └── primary_mail.html  # HTML 메일 템플릿
```

## 🔒 보안

- **로그인 인증**: 시스템 접근 전 사용자 인증 필요
- **비밀번호 해싱**: 사용자 비밀번호는 SHA-256으로 해시화하여 저장
- **민감 정보 보호**: SMTP 비밀번호, 이메일 등은 `.streamlit/secrets.toml`에서 관리
- **Git 제외**: `.gitignore`에 포함되어 Git에 커밋되지 않음
- **배포 환경**: Streamlit Cloud의 Secrets 기능 사용

### Streamlit Cloud 배포 시
1. GitHub에 푸시 (`.streamlit/secrets.toml`은 자동 제외됨)
2. Streamlit Cloud에서 앱 연결
3. Settings → Secrets에 `.streamlit/secrets.toml` 내용 복사/붙여넣기
4. 앱 재시작
