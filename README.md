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
- 매일 밤 11시(KST) cron으로 실행

## 데이터 추출 방법
1. Playwright로 캐릭터 상세 페이지 접속
2. `document.getElementById('__NEXT_DATA__')` 에서 JSON 파싱
3. `characterDetail.totalMessageCount`, `characterDetail.likeCount`, `characterDetail.commentCount` 추출

## 프로젝트 구조
```
/root/projects/crack-tracker/
├── README.md
├── requirements.txt
├── track.py          # 메인 스크립트
└── data/
    ├── hanseo_yun_stats.csv     # 일별 이력
    └── hanseo_yun_latest.json   # 최신 상태
```
