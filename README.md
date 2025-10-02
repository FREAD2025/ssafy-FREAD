# SSAFY Fread - 개인 작가 Agent 서비스

> AI 기반 텍스트 분석 및 맞춤법 검사 서비스

## 📋 프로젝트 개요

SSAFY Fread는 개인 작가들을 위한 AI 기반 텍스트 분석 서비스입니다. 사용자가 작성한 텍스트를 분석하여 완성도, 설득력, 전달력, 몰입도, 문장 간결성, 대중성 등의 다양한 지표로 평가하고, 맞춤법 검사 기능을 제공합니다.

## 🚀 주요 기능

### 1. 텍스트 분석 (Fread Analysis)
- **완성도 분석**: 전체적인 글의 완성도를 종합적으로 평가
- **설득력 점수**: 논리적 구성과 설득력 측정
- **전달력 점수**: 메시지 전달의 명확성 평가
- **몰입도 점수**: 독자의 몰입도를 높이는 요소 분석
- **문장 간결성**: 문장의 간결성과 명확성 평가
- **대중성 점수**: 일반 독자들의 이해도와 접근성 측정
- **AI 댓글 예측**: 예상되는 독자 댓글 데이터 제공
- **솔루션 제안**: 글의 개선을 위한 구체적인 제안 제공

### 2. 맞춤법 검사
- **한국어 맞춤법 검사**: 한글 맞춤법 및 문법 오류 검출
- **실시간 검사**: 5000자 내외의 텍스트에 대한 즉시 검사
- **오류 수정 제안**: 맞춤법 오류에 대한 정확한 수정 제안

### 3. 공모전 정보 서비스
- **공모전 목록 조회**: 다양한 문학 공모전 정보 제공
- **공모전 상세 정보**: 주최사, 참여 대상, 상금, 마감일 등 상세 정보
- **공모전 찜하기**: 관심 있는 공모전을 저장하고 관리

### 4. 사용자 관리
- **회원가입/로그인**: 일반 회원가입 및 카카오 소셜 로그인 지원
- **프로필 관리**: 작가 정보, 선호 장르, 작가 경력 등 프로필 설정
- **분석 이력 관리**: 과거 분석 결과 조회 및 관리
- **찜한 공모전 관리**: 관심 공모전 목록 관리

## 🛠 기술 스택

### Backend
- **Django 4.2.16**: 웹 프레임워크
- **Django REST Framework**: API 개발
- **SQLite**: 데이터베이스
- **OpenAI API**: AI 텍스트 분석
- **한글 맞춤법 검사 라이브러리**: 맞춤법 검사 기능

### Frontend (예정)
- **Vue.js**: 프론트엔드 프레임워크
- **JavaScript**: 클라이언트 사이드 로직

### 인증 및 보안
- **Django Allauth**: 소셜 로그인 (카카오)
- **Django CORS Headers**: CORS 처리
- **Token Authentication**: API 인증

### API 문서화
- **DRF Spectacular**: Swagger UI 자동 생성
- **OpenAPI 3.0**: API 스키마 정의

## 📁 프로젝트 구조

```
ssafy-fread/
├── analyses/                 # 텍스트 분석 앱
│   ├── models.py            # 분석 모델 정의
│   ├── views/               # 분석 관련 뷰
│   │   ├── analysis_view.py
│   │   └── spell_check_view.py
│   ├── utils/               # 분석 유틸리티
│   │   ├── generate_analysis.py
│   │   ├── generate_fread_analysis.py
│   │   └── spellcheck_utils.py
│   └── hanspell/            # 한글 맞춤법 검사 모듈
├── contests/                # 공모전 정보 앱
│   ├── models.py           # 공모전 모델 정의
│   └── views.py            # 공모전 관련 뷰
├── users/                   # 사용자 관리 앱
│   ├── models.py           # 사용자 모델 정의
│   ├── views.py            # 사용자 관련 뷰
│   └── adapter.py          # 소셜 로그인 어댑터
├── project_fread/          # 프로젝트 설정
│   ├── settings.py         # Django 설정
│   └── urls.py            # 메인 URL 설정
├── media/                  # 미디어 파일
│   ├── contest_images/     # 공모전 이미지
│   └── profile_pics/       # 프로필 이미지
└── requirements.txt        # 의존성 패키지
```

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd ssafy-fread
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
OPENAI_API_KEY=your_openai_api_key
KAKAO_REST_API_KEY=your_kakao_rest_api_key
FRONTEND_URL=http://localhost:5173
EMAIL_HOST_USER=your_email@gmail.com
```

### 5. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 관리자 계정 생성
```bash
python manage.py createsuperuser
```

### 7. 서버 실행
```bash
python manage.py runserver
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

## 🔗 주요 API 엔드포인트

### 사용자 관리
- `POST /api/v1/users/signup/` - 회원가입
- `POST /api/v1/users/login/` - 로그인
- `POST /api/v1/users/logout/` - 로그아웃
- `GET /api/v1/users/mypage/` - 마이페이지
- `PUT /api/v1/users/profile/` - 프로필 수정

### 텍스트 분석
- `POST /api/v1/analyses/fread/` - Fread 분석 요청
- `GET /api/v1/analyses/fread/{id}/` - 분석 결과 조회
- `GET /api/v1/analyses/` - 분석 이력 조회
- `DELETE /api/v1/analyses/{id}/` - 분석 결과 삭제

### 맞춤법 검사
- `POST /api/v1/analyses/spellcheck/` - 맞춤법 검사

### 공모전 정보
- `GET /api/v1/contests/` - 공모전 목록 조회
- `GET /api/v1/contests/{id}/` - 공모전 상세 조회
- `POST /api/v1/contests/{id}/like/` - 공모전 찜하기
- `DELETE /api/v1/contests/{id}/like/` - 찜 해제

## 🎯 사용 예시

### 텍스트 분석 요청
```python
import requests

# Fread 분석 요청
response = requests.post(
    'http://localhost:8000/api/v1/analyses/fread/',
    headers={'Authorization': 'Token your_token'},
    json={
        'title': '나의 첫 소설',
        'original_text': '분석하고자 하는 텍스트 내용...',
        'analysis_type': 'FREAD'
    }
)
```

### 맞춤법 검사
```python
# 맞춤법 검사 요청
response = requests.post(
    'http://localhost:8000/api/v1/analyses/spellcheck/',
    json={'text': '맞춤법을 검사할 텍스트...'}
)

---

**SSAFY Fread** - AI로 더 나은 글쓰기를 시작하세요! ✍️
