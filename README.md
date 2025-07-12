# 🏠 주택정책 RAG 챗봇

공공데이터 포탈의 주택정책 보도자료 PDF를 분석하고 임베딩하여 RAG(Retrieval-Augmented Generation) 기반의 지능형 챗봇을 구현한 프로젝트입니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [설치 및 실행](#설치-및-실행)
- [사용법](#사용법)
- [API 키 설정](#api-키-설정)
- [프로젝트 구조](#프로젝트-구조)
- [기술 스택](#기술-스택)
- [주요 특징](#주요-특징)
- [문제 해결](#문제-해결)

## 🎯 프로젝트 개요

이 프로젝트는 논문 분석 사이트 문라이트와 유사한 방식으로, PDF 문서의 정보를 임베딩하여 더 정확하고 유용한 답변을 제공하는 AI 챗봇을 구현합니다.

### 핵심 기능
- **PDF 텍스트 추출**: PyPDF2를 사용한 효율적인 PDF 처리
- **벡터 임베딩**: Sentence Transformers를 활용한 텍스트 임베딩
- **벡터 데이터베이스**: ChromaDB를 사용한 고성능 벡터 검색
- **RAG 시스템**: OpenAI GPT 모델과 결합한 검색 기반 생성
- **웹 인터페이스**: Streamlit을 활용한 사용자 친화적 UI

## 🚀 주요 기능

### 1. PDF 처리 및 분석
- 공공데이터 포탈에서 주택정책 보도자료 자동 수집
- PDF 텍스트 추출 및 청킹
- 메타데이터 추출 및 관리

### 2. 임베딩 및 벡터 검색
- 고품질 텍스트 임베딩 생성
- 유사도 기반 문서 검색
- 실시간 벡터 데이터베이스 관리

### 3. RAG 기반 챗봇
- 컨텍스트 기반 정확한 답변 생성
- 대화 히스토리 관리
- 참고 문서 표시

### 4. 웹 인터페이스
- 직관적인 채팅 인터페이스
- 실시간 대화 기능
- 파일 업로드 및 처리
- 시스템 모니터링

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   공공데이터    │    │   PDF 처리      │    │   임베딩 관리   │
│   포탈 수집     │───▶│   및 청킹       │───▶│   및 벡터 DB    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   웹 인터페이스  │◀───│   RAG 챗봇      │◀───│   OpenAI API    │
│   (Streamlit)   │    │   엔진          │    │   (GPT 모델)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd housing-policy-rag-chatbot
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일을 생성하고 API 키를 설정합니다:
```env
OPENAI_API_KEY=your_openai_api_key_here
DECODING_API_KEY=your_decoding_api_key_here
PUBLIC_DATA_URL=https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15109325
```

### 5. 실행

#### 명령행 인터페이스
```bash
# 기본 실행
python main.py

# 데이터베이스 구축
python main.py setup

# 데모 모드
python main.py demo
```

#### 웹 인터페이스
```bash
streamlit run streamlit_app.py
```

## 💻 사용법

### 1. 명령행 인터페이스

```bash
python main.py
```

실행 후 다음과 같은 명령어를 사용할 수 있습니다:
- `quit`, `exit`, `종료`: 프로그램 종료
- `clear`: 대화 히스토리 초기화
- `info`: 시스템 정보 확인

### 2. 웹 인터페이스

```bash
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`로 접속하여 사용할 수 있습니다.

### 3. 주요 기능

#### PDF 파일 업로드
- 사이드바의 "PDF 파일 업로드" 섹션에서 파일 선택
- "파일 처리" 버튼으로 임베딩 데이터베이스에 추가

#### 데이터베이스 구축
- "데이터베이스 구축" 버튼으로 공공데이터 포탈에서 자동 수집
- 수집된 PDF를 처리하여 벡터 데이터베이스 구축

#### 챗봇 대화
- 메인 채팅 인터페이스에서 질문 입력
- 실시간으로 관련 문서를 검색하여 답변 생성
- 참고 문서 정보 확인 가능

## 🔑 API 키 설정

### OpenAI API 키
1. [OpenAI Platform](https://platform.openai.com/)에서 계정 생성
2. API 키 발급
3. `.env` 파일에 설정

### Decoding API 키
1. [Decoding](https://decoding.kr/)에서 계정 생성
2. API 키 발급
3. `.env` 파일에 설정

## 📁 프로젝트 구조

```
housing-policy-rag-chatbot/
├── README.md                 # 프로젝트 문서
├── requirements.txt          # Python 의존성
├── .env                      # 환경변수 설정
├── main.py                   # 메인 실행 파일
├── streamlit_app.py          # 웹 인터페이스
├── pdf_processor.py          # PDF 처리 모듈
├── embedding_manager.py      # 임베딩 관리 모듈
├── rag_chatbot.py           # RAG 챗봇 엔진
├── data_collector.py        # 데이터 수집 모듈
├── pdfs/                    # PDF 파일 저장소
├── chroma_db/               # 벡터 데이터베이스
└── temp/                    # 임시 파일
```

## 🛠️ 기술 스택

### 백엔드
- **Python 3.8+**: 메인 프로그래밍 언어
- **PyPDF2**: PDF 텍스트 추출
- **Sentence Transformers**: 텍스트 임베딩
- **ChromaDB**: 벡터 데이터베이스
- **OpenAI API**: GPT 모델 연동

### 프론트엔드
- **Streamlit**: 웹 인터페이스
- **HTML/CSS**: 커스텀 스타일링

### 데이터 처리
- **BeautifulSoup**: 웹 스크래핑
- **Requests**: HTTP 요청 처리
- **Pandas**: 데이터 처리

## ✨ 주요 특징

### 1. 고품질 임베딩
- Sentence Transformers의 최신 모델 사용
- 다국어 지원 (한국어 최적화)
- 효율적인 벡터 검색

### 2. 정확한 답변
- RAG 시스템으로 문서 기반 답변
- 컨텍스트 기반 생성
- 참고 문서 표시

### 3. 사용자 친화적
- 직관적인 웹 인터페이스
- 실시간 대화 기능
- 파일 업로드 지원

### 4. 확장 가능
- 모듈화된 구조
- 새로운 데이터 소스 추가 용이
- 다양한 AI 모델 지원

## 🔧 문제 해결

### 일반적인 문제들

#### 1. API 키 오류
```
❌ OPENAI_API_KEY가 설정되지 않았습니다.
```
**해결방법**: `.env` 파일에 올바른 API 키를 설정하세요.

#### 2. PDF 처리 오류
```
PDF에서 텍스트를 추출할 수 없습니다
```
**해결방법**: 
- PDF 파일이 텍스트 기반인지 확인
- 스캔된 PDF의 경우 OCR 처리 필요

#### 3. 메모리 부족
```
메모리 부족 오류
```
**해결방법**:
- 더 작은 청크 크기로 설정
- 배치 처리 크기 조정

#### 4. 네트워크 오류
```
PDF 다운로드 실패
```
**해결방법**:
- 인터넷 연결 확인
- URL 유효성 검사
- 재시도 로직 구현

### 성능 최적화

#### 1. 임베딩 모델 선택
```python
# 더 빠른 모델 (정확도 약간 낮음)
model_name = "sentence-transformers/all-MiniLM-L6-v2"

# 더 정확한 모델 (속도 약간 느림)
model_name = "sentence-transformers/all-mpnet-base-v2"
```

#### 2. 청크 크기 조정
```python
# 작은 청크 (더 정확한 검색)
chunk_size = 500

# 큰 청크 (더 빠른 처리)
chunk_size = 2000
```

#### 3. 검색 결과 수 조정
```python
# 더 많은 결과 (더 포괄적)
n_results = 10

# 더 적은 결과 (더 빠름)
n_results = 3
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**🏠 주택정책 RAG 챗봇** - 더 나은 주택정책 이해를 위한 AI 솔루션