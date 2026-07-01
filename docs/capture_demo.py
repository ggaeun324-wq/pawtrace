"""전체 탭 동작 흐름 GIF 캡처 스크립트.

오늘의 친구 → 보호소 지도 → 해피ing → 입양 스토리(분기 타임라인)
→ 쇼핑몰(장바구니 담기·서랍·결제) → 반려생활 기록 까지의 실제 동작을
프레임으로 캡처해 docs/home-demo.gif 로 저장합니다.

실행 전제:
- 백엔드 http://localhost:8000, 정적 프론트 http://localhost:8777 가 떠 있어야 함.
- adopter 계정으로 로그인해 장바구니/결제/기록이 실제 동작하도록 함.
"""
import io
import time

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8777"
API = "http://localhost:8000/api/v1"
VW, VH = 1180, 820          # 뷰포트
OUT = "docs/home-demo.gif"

frames: list[Image.Image] = []
durations: list[int] = []


def snap(page, hold=1):
    """현재 화면을 프레임으로 추가하고, hold(초)를 그 프레임의 표시 시간으로 기록."""
    png = page.screenshot(type="png")
    img = Image.open(io.BytesIO(png)).convert("RGB")
    # 폭이 크면 절반으로 줄여 파일 크기 최적화
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    frames.append(img)
    durations.append(int(hold * 1000))


def goto(page, path):
    page.goto(f"{BASE}/{path}", wait_until="networkidle")
    time.sleep(0.8)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": VW, "height": VH}, device_scale_factor=1)
        page = ctx.new_page()

        # 1) adopter 로그인 → 토큰/유저를 localStorage 에 주입(프론트가 읽는 키와 동일)
        page.goto(f"{BASE}/index.html", wait_until="networkidle")
        page.evaluate(
            """async ({api}) => {
                const t = await fetch(api + '/auth/login', {
                    method:'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({email:'adopter@pawtrace.dev', password:'adopter1234'})
                }).then(r=>r.json());
                localStorage.setItem('pawtrace_token', t.access_token);
                const me = await fetch(api + '/auth/me', {headers:{Authorization:'Bearer '+t.access_token}}).then(r=>r.json());
                localStorage.setItem('pawtrace_user', JSON.stringify(me));
            }""",
            {"api": API},
        )

        # 2) 오늘의 친구(홈) — 스크롤로 공고/지도 보여주기
        goto(page, "index.html")
        snap(page, 1.4)
        page.mouse.wheel(0, 520); time.sleep(0.7); snap(page, 1.0)
        page.mouse.wheel(0, 620); time.sleep(0.7); snap(page, 1.2)
        page.mouse.wheel(0, -1140); time.sleep(0.4)

        # 3) 보호소 지도
        goto(page, "map.html")
        snap(page, 1.4)
        page.mouse.wheel(0, 420); time.sleep(0.7); snap(page, 1.2)
        page.mouse.wheel(0, -420); time.sleep(0.3)

        # 4) 해피ing — 단일 컬럼 큰 카드
        goto(page, "happyending.html")
        snap(page, 1.4)
        page.mouse.wheel(0, 520); time.sleep(0.7); snap(page, 1.2)

        # 5) 입양 스토리 — '지금은 어떻게 지내요' 분기 타임라인
        goto(page, "happystory.html?id=2")
        snap(page, 1.3)
        page.mouse.wheel(0, 600); time.sleep(0.7); snap(page, 1.4)

        # 6) 쇼핑몰 — 담기 → 장바구니 서랍 → 결제
        goto(page, "shop.html")
        snap(page, 1.2)
        # 첫 상품 담기
        page.click("#grid .pcard .btn")
        time.sleep(1.0); snap(page, 1.4)          # 서랍이 열림
        # 수량 +
        try:
            page.click("#ditems .qbtn:has-text('+')")
            time.sleep(0.6); snap(page, 1.0)
        except Exception:
            pass
        # 결제
        page.click("#checkoutBtn")
        time.sleep(1.6); snap(page, 1.8)          # 결제 완료 토스트

        # 7) 반려생활 기록 — 분기 작성 + 타임라인
        goto(page, "journey.html")
        snap(page, 1.3)
        page.mouse.wheel(0, 520); time.sleep(0.7); snap(page, 1.4)

        browser.close()

    # GIF 저장 — 프레임마다 개별 표시 시간(durations) 적용
    frames[0].save(
        OUT, save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=True,
    )
    print(f"[gif] saved {OUT} · frames={len(frames)}")


if __name__ == "__main__":
    main()
