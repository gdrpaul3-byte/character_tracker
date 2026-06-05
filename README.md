# Crack.wrtn.ai 캐릭터 트래커

크랙(crack.wrtn.ai) 플랫폼의 특정 캐릭터 조회수/좋아요 수를 매일 추적하는 프로그램

## 대상 캐릭터
- **이름**: 한서윤
- **제작자**: 헌혈
- **캐릭터 ID**: 6a0cdd99c0cf573be43391fc
- **URL**: https://crack.wrtn.ai/characters/6a0cdd99c0cf573be43391fc/detail
- **한줄소개**: 문을 잠갔는데 반장이 또 들어왔다

## 기술 스펙
- Python 3 + Playwright (headless browser)
- `__NEXT_DATA__` JSON에서 데이터 추출 (API 직접 호출 불가)
- 수집 데이터: 날짜, 조회수(totalMessageCount), 좋아요(likeCount), 댓글수(commentCount)
- CSV 파일로 이력 저장 (`data/hanseo_yun_stats.csv`)
- JSON 파일로 최신 상태 저장 (`data/hanseo_yun_latest.json`)
- 정적 공개 대시보드: `index.html`, `charts.html`, `research.html`
- 매일 밤 11시(KST) cron으로 실행

## 데이터 추출 방법
1. Playwright로 캐릭터 상세 페이지 접속
2. `document.getElementById('__NEXT_DATA__')` 에서 JSON 파싱
3. `characterDetail.totalMessageCount`, `characterDetail.likeCount`, `characterDetail.commentCount` 추출

## 프로젝트 구조
```
/root/projects/character_tracker/
├── README.md
├── index.html        # 현재 캐릭터 추적 대시보드
├── charts.html       # 차트 전용 보기
├── research.html     # Tingle + Crack 캐릭터 플랫폼 리서치 페이지
├── requirements.txt
├── track.py          # 메인 스크립트
└── data/
    ├── hanseo_yun_stats.csv     # 일별 이력
    ├── hanseo_yun_latest.json   # 최신 상태
    └── research_seed.json       # 리서치 페이지용 시드 데이터
```

## 공개 리서치 페이지

`research.html`은 Tingle과 Crack의 캐릭터 플랫폼 리서치를 한국어 정적 페이지로 보여준다. 포함 내용은 다음과 같다.

- 인기 캐릭터 설정/내러티브 테마 클러스터
- 클러스터 간 관계·네트워크 맵
- Tingle과 Crack의 플랫폼 차이
- 데이터 수집 및 운영 로드맵
- 공개 데이터 해석 시 주의사항

페이지는 `data/research_seed.json`을 fetch로 읽는다. 브라우저에서 `file://`로 직접 열어 fetch가 차단될 경우에도 내장 fallback 데이터로 화면이 표시된다. 정상 운영 확인은 프로젝트 루트에서 `python3 -m http.server 8000` 실행 후 `http://localhost:8000/research.html`로 접근한다.

## 리서치 운영 계획

1. 상위 노출 슬롯과 표본 기준을 고정하고 캐릭터 소개문, 태그, 공개 지표 필드를 수집한다.
2. Crack은 현재 상세 페이지 지표 추출 흐름을 확장하고, Tingle은 공개 페이지에서 수집 가능한 범위와 정책 리스크를 먼저 확인한다.
3. 소개문 키워드, 관계 설정, 세계관 장르, 안전 주의 문구를 수동 코드북과 자동 태깅으로 병행 분류한다.
4. 월간 단위로 클러스터 점유율, 성장률, 플랫폼별 차이를 업데이트하고 신규 캐릭터 기획 백로그에 연결한다.
5. 공개 데이터는 대표성 한계가 있으므로 조회수 단독 판단을 피하고 재방문율, 첫 대화 품질, 정책·권리 리스크를 함께 검토한다.
