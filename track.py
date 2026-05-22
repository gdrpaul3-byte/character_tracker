#!/usr/bin/env python3
"""
Crack.wrtn.ai Character Tracker
- 한서윤 (제작자: 헌혈) 캐릭터의 조회수/좋아요 수를 추적
- 매일 밤 11시(KST) cron으로 실행
"""

import json
import csv
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 한국 시간(KST)
KST = timezone(timedelta(hours=9))

# 설정
CHARACTER_ID = "6a0cdd99c0cf573be43391fc"
CHARACTER_URL = f"https://crack.wrtn.ai/characters/{CHARACTER_ID}/detail"
CHARACTER_NAME = "한서윤"
CREATOR_NAME = "헌혈"

# 랭킹 페이지 설정
RANKING_PAGES = [
    {"name": "신작 랭킹", "url": "https://crack.wrtn.ai/characters?sort=new-ranking"},
    {"name": "남성 인기", "url": "https://crack.wrtn.ai/characters?sort=male-popular"},
    {"name": "로맨스", "url": "https://crack.wrtn.ai/characters?sort=romance"},
    {"name": "일상/현대", "url": "https://crack.wrtn.ai/characters?sort=daily"},
]

# 경로
PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
CSV_PATH = DATA_DIR / "hanseo_yun_stats.csv"
LATEST_PATH = DATA_DIR / "hanseo_yun_latest.json"

# 데이터 디렉토리 생성
DATA_DIR.mkdir(exist_ok=True)


def find_rank_in_page(page, ranking_name: str, character_name: str, max_scroll: int = 5) -> dict | None:
    """현재 페이지에서 캐릭터 이름을 찾아 순위를 반환합니다."""
    for scroll_count in range(max_scroll):
        # 페이지에서 캐릭터 이름이 포함된 요소 찾기
        result = page.evaluate(f"""
            () => {{
                const characterName = '{character_name}';
                // 모든 텍스트 노드에서 캐릭터 이름 찾기
                const allElements = document.querySelectorAll('*');
                for (const el of allElements) {{
                    if (el.textContent.trim() === characterName && el.children.length === 0) {{
                        // 부모 카드 찾기 (여러 레벨 위로)
                        let card = el;
                        for (let i = 0; i < 5; i++) {{
                            card = card?.parentElement;
                            if (!card) break;
                        }}
                        if (card) {{
                            // 같은 레벨의 형제 요소들 찾기
                            const parent = card.parentElement;
                            if (!parent) continue;
                            const siblings = Array.from(parent.children);
                            const idx = siblings.indexOf(card);
                            return {{
                                found: true,
                                index: idx + 1,
                                total: siblings.length
                            }};
                        }}
                    }}
                }}
                return {{ found: false }};
            }}
        """)
        
        if result and result.get("found"):
            return {
                "ranking_name": ranking_name,
                "rank": result.get("index", 0),
                "total": result.get("total", 0),
            }
        
        # 스크롤 다운
        if scroll_count < max_scroll - 1:
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(1)
    
    return None


def fetch_all_data():
    """Playwright를 사용해 캐릭터 통계와 랭킹을 모두 가져옵니다."""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="ko-KR",
        )
        page = context.new_page()
        
        try:
            # 1. 캐릭터 상세 페이지에서 통계 수집
            print(f"[{datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}] 캐릭터 페이지 로딩 중...")
            page.goto(CHARACTER_URL, wait_until="networkidle", timeout=60000)
            
            data_json = page.evaluate("""
                () => {
                    const el = document.getElementById('__NEXT_DATA__');
                    if (!el) return null;
                    const data = JSON.parse(el.textContent);
                    const detail = data?.props?.pageProps?.characterDetail;
                    if (!detail) return null;
                    return {
                        name: detail.name,
                        totalMessageCount: detail.totalMessageCount,
                        likeCount: detail.likeCount,
                        commentCount: detail.commentCount,
                        imageCount: detail.imageCount,
                        simpleDescription: detail.simpleDescription,
                        creatorNickname: detail.creator?.nickname,
                        tags: detail.tags,
                        isAdult: detail.isAdult,
                        target: detail.target,
                        status: detail.status,
                        createdAt: detail.createdAt,
                        updatedAt: detail.updatedAt,
                        updateInfo: detail.updateInfo,
                    };
                }
            """)
            
            if not data_json:
                print("ERROR: __NEXT_DATA__에서 캐릭터 데이터를 찾을 수 없습니다.")
                sys.exit(1)
            
            # 2. 랭킹 페이지에서 순위 확인
            print(f"\n랭킹 확인 중...")
            rankings = []
            
            for rp in RANKING_PAGES:
                print(f"  [{rp['name']}] 랭킹 확인 중...")
                try:
                    page.goto(rp["url"], wait_until="networkidle", timeout=30000)
                    time.sleep(1)
                    
                    rank_info = find_rank_in_page(page, rp["name"], CHARACTER_NAME)
                    if rank_info:
                        print(f"    → {rank_info['rank']}위 발견!")
                        rankings.append(rank_info)
                    else:
                        print(f"    → 랭킹권 외")
                except Exception as e:
                    print(f"    → 에러: {e}")
            
            return data_json, rankings
            
        finally:
            browser.close()


def save_to_csv(stats: dict):
    """통계를 CSV 파일에 추가합니다."""
    now = datetime.now(KST)
    
    # 업데이트 정보 추출
    update_info = stats.get("updateInfo") or {}
    
    row = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "totalMessageCount": stats["totalMessageCount"],
        "likeCount": stats["likeCount"],
        "commentCount": stats["commentCount"],
        "imageCount": stats["imageCount"],
        "version": update_info.get("version", 1),
        "releasedAt": update_info.get("releasedAt", ""),
    }
    
    file_exists = CSV_PATH.exists()
    
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    
    print(f"CSV 저장 완료: {CSV_PATH}")


def save_latest(stats: dict):
    """최신 상태를 JSON 파일로 저장합니다."""
    now = datetime.now(KST)
    
    # 업데이트 정보 추출
    update_info = stats.get("updateInfo") or {}
    
    latest = {
        "timestamp": now.isoformat(),
        "characterId": CHARACTER_ID,
        "characterName": stats["name"],
        "creatorNickname": stats["creatorNickname"],
        "simpleDescription": stats["simpleDescription"],
        "totalMessageCount": stats["totalMessageCount"],
        "likeCount": stats["likeCount"],
        "commentCount": stats["commentCount"],
        "imageCount": stats["imageCount"],
        "tags": stats["tags"],
        "isAdult": stats["isAdult"],
        "target": stats["target"],
        "status": stats["status"],
        "createdAt": stats.get("createdAt"),
        "updatedAt": stats.get("updatedAt"),
        "version": update_info.get("version", 1),
        "releasedAt": update_info.get("releasedAt"),
        "url": CHARACTER_URL,
    }
    
    with open(LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)
    
    print(f"최신 상태 저장 완료: {LATEST_PATH}")


def get_previous_stats() -> dict | None:
    """이전 수집 데이터를 불러옵니다."""
    if not CSV_PATH.exists():
        return None
    
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        if not reader:
            return None
        return reader[-1]


def format_report(stats: dict, rankings: list = None, prev: dict = None) -> str:
    """Telegram 전송용 리포트를 생성합니다."""
    now = datetime.now(KST)
    
    # 업데이트 정보 추출
    update_info = stats.get("updateInfo") or {}
    version = update_info.get("version", 1)
    released_at = update_info.get("releasedAt")
    
    # 업데이트 날짜 포맷팅
    if released_at:
        try:
            released_dt = datetime.fromisoformat(released_at.replace("Z", "+00:00"))
            released_str = released_dt.astimezone(KST).strftime("%Y.%m.%d")
        except:
            released_str = released_at[:10]
    else:
        released_str = "-"
    
    lines = [
        f"📊 **한서윤 캐릭터 일일 리포트**",
        f"📅 {now.strftime('%Y-%m-%d %H:%M')} (KST)",
        f"",
        f"👤 캐릭터: {stats['name']} (by {stats['creatorNickname']})",
        f"💬 한줄소개: {stats['simpleDescription']}",
        f"",
        f"🔄 **버전: V{version}** (업데이트: {released_str})",
        f"",
        f"💬 조회수(대화수): **{stats['totalMessageCount']:,}**",
        f"❤️ 좋아요: **{stats['likeCount']:,}**",
        f"💬 댓글수: **{stats['commentCount']:,}**",
        f"🖼️ 이미지: **{stats['imageCount']}**장",
    ]
    
    # 랭킹 정보 추가
    if rankings:
        lines.append("")
        lines.append("🏆 **랭킹 현황**")
        for r in rankings:
            lines.append(f"  • {r['ranking_name']}: **{r['rank']}위**")
    
    if prev:
        msg_diff = stats["totalMessageCount"] - int(prev.get("totalMessageCount", 0))
        like_diff = stats["likeCount"] - int(prev.get("likeCount", 0))
        comment_diff = stats["commentCount"] - int(prev.get("commentCount", 0))
        
        # 버전 변화 확인
        prev_version = int(prev.get("version", 1))
        version_diff = version - prev_version
        
        lines.append("")
        lines.append("📈 **전일 대비 변화**")
        lines.append(f"  조회수: {'+' if msg_diff >= 0 else ''}{msg_diff:,}")
        lines.append(f"  좋아요: {'+' if like_diff >= 0 else ''}{like_diff:,}")
        lines.append(f"  댓글수: {'+' if comment_diff >= 0 else ''}{comment_diff:,}")
        
        if version_diff > 0:
            lines.append(f"  🆕 버전 업데이트: V{prev_version} → V{version}")
    
    lines.append("")
    lines.append(f"🔗 {CHARACTER_URL}")
    
    return "\n".join(lines)


def main():
    print("=" * 50)
    print(f"Crack Character Tracker - {CHARACTER_NAME}")
    print("=" * 50)
    
    # 이전 데이터 로드
    prev = get_previous_stats()
    
    # 현재 데이터 수집 (통계 + 랭킹)
    stats, rankings = fetch_all_data()
    
    print(f"\n수집 결과:")
    print(f"  이름: {stats['name']}")
    print(f"  조회수: {stats['totalMessageCount']:,}")
    print(f"  좋아요: {stats['likeCount']:,}")
    print(f"  댓글수: {stats['commentCount']:,}")
    
    # 저장
    save_to_csv(stats)
    save_latest(stats)
    
    # 리포트 생성
    report = format_report(stats, rankings, prev)
    print(f"\n{'=' * 50}")
    print(report)
    print(f"{'=' * 50}")
    
    # 리포트 파일로도 저장 (cron에서 읽어서 전송용)
    report_path = DATA_DIR / "latest_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()
