# OneWord - 실시간 정보 검색 앱 🚀

바쁜 현대인을 위한 한 단어 검색으로 실시간 정보를 제공하는 스마트 앱입니다.

## ✨ 주요 기능

### 🌤️ **실시간 날씨** (WeatherAPI)
- 현재 날씨 + 시간대별 예보
- 온도, 습도, 바람 정보
- 한국어 날씨 상태 제공

### 🚗 **교통 정보** (카카오맵 API)
- 출발지 → 도착지 최적 경로
- 예상 소요시간 계산
- 대중교통 경로 안내

### 📈 **실시간 주가** (한국투자증권 API)
- 국내 주요 종목 실시간 주가
- 등락률 및 변동 정보
- 주요 종목 코드 자동 매핑

### 🍳 **레시피** (OpenAI GPT)
- 요리별 재료 및 조리법
- 단계별 조리 과정
- 한국 요리 전문

### 💬 **명언** (OpenAI GPT)
- 주제별 의미있는 명언
- 작가/출처 정보 포함
- 한국어 번역 제공

## 🛠️ 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API (레시피, 명언용)
OPENAI_API_KEY=your-openai-api-key-here

# WeatherAPI (날씨용)
WEATHER_API_KEY=your-weather-api-key-here

# 카카오 API (교통용)
KAKAO_API_KEY=your-kakao-api-key-here

# 한국투자증권 API (주가용)
KIS_APP_KEY=your-kis-app-key-here
KIS_APP_SECRET=your-kis-app-secret-here
```

### 3. 앱 실행
```bash
python app.py
```

### 4. 브라우저 접속
```
http://localhost:5000
```

## 🔑 API 키 발급 방법

### 🌤️ WeatherAPI
1. https://www.weatherapi.com 회원가입
2. 무료 플랜: 1,000,000회/월
3. API Keys 메뉴에서 키 복사

### 🗺️ 카카오 API
1. https://developers.kakao.com 회원가입
2. 애플리케이션 추가 → 앱 키 발급
3. REST API 키 사용

### 📈 한국투자증권 API
1. https://apiportal.koreainvestment.com 회원가입
2. 모의투자 또는 실전투자 신청
3. App Key, App Secret 발급

### 🤖 OpenAI API
1. https://platform.openai.com 회원가입
2. API Keys 메뉴에서 새 키 생성
3. 사용량에 따라 요금 부과

## 🎨 UI 특징

- **글래스모피즘 디자인**: 모던한 반투명 효과
- **반응형 레이아웃**: 모바일/데스크톱 최적화
- **다크모드 지원**: 시스템 설정 자동 감지
- **부드러운 애니메이션**: 사용자 경험 최적화
- **실시간 UI 업데이트**: 카테고리 변경 시 즉시 반영

## 📁 프로젝트 구조

```
oneWord/
├── app.py              # Flask 메인 애플리케이션
├── api_services.py     # 외부 API 서비스 모듈
├── requirements.txt    # Python 의존성
├── .gitignore         # Git 무시 파일
├── README.md          # 프로젝트 문서
├── static/
│   └── style.css      # CSS 스타일
└── templates/
    └── index.html     # HTML 템플릿
```

## 🚀 주요 기술 스택

- **Backend**: Python Flask
- **API 통합**: requests, python-dotenv
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **디자인**: CSS Grid, Flexbox, 애니메이션
- **API**: OpenAI GPT, WeatherAPI, 카카오맵, 한국투자증권

## 📝 사용 예시

### 날씨 검색
```
입력: "서울"
결과: 📍 서울 날씨 정보
     ☀️ 오전(9시): 맑음, 22°C
     🌤️ 오후(15시): 구름 조금, 25°C
     🌙 저녁(21시): 맑음, 18°C
```

### 교통 검색
```
출발지: "강남역"
도착지: "홍대입구역"
결과: 🚉 강남역 → 홍대입구역
     📍 예상 소요시간: 37분
     🚇 지하철 2호선 → 6호선 환승
```

### 주가 검색
```
입력: "삼성전자"
결과: 📈 삼성전자 (005930)
     💰 현재가: 71,000원
     📊 등락률: +0.42%
```

## ⚠️ 주의사항

1. **API 키 보안**: `.env` 파일을 절대 공유하지 마세요
2. **사용량 제한**: 각 API별 사용량 제한을 확인하세요
3. **네트워크**: 안정적인 인터넷 연결이 필요합니다
4. **실시간 데이터**: 주가/날씨는 실시간 데이터이므로 지연이 있을 수 있습니다

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**만든이**: OneWord Team  
**문의**: 이슈 탭에서 문의해주세요!
