/*
 * api.js — 프로토타입 ↔ 백엔드 API 연결 (공용 모듈)
 * ------------------------------------------------------------------
 * 설계: "점진적 향상(progressive enhancement)"
 *   1) HTML 에 박혀 있는 데모 데이터가 먼저 보입니다 (백엔드 없어도 동작).
 *   2) 이 스크립트가 백엔드 API 를 호출해 성공하면 실제 데이터로 교체합니다.
 *   3) 우상단 배지로 연결 상태를 표시합니다 (● 실시간 API / ○ 데모 데이터).
 *
 * API 주소 결정 순서:
 *   ?api=<url>  쿼리스트링  >  localStorage('pawtrace_api')  >  기본값
 *   예) 로컬:  http://localhost:8000/api/v1
 *       클라우드: http://<alb_dns_name>/api/v1
 */
(function () {
  const DEFAULT_API = "http://localhost:8000/api/v1";

  const params = new URLSearchParams(location.search);
  const fromQuery = params.get("api");
  if (fromQuery) localStorage.setItem("pawtrace_api", fromQuery);

  const API_BASE =
    fromQuery || localStorage.getItem("pawtrace_api") || DEFAULT_API;

  // ── 공용 fetch: 2초 타임아웃, 실패 시 throw → 호출부에서 fallback 처리 ──
  async function pawFetch(path) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 2000);
    try {
      const res = await fetch(API_BASE + path, { signal: ctrl.signal });
      if (!res.ok) throw new Error("HTTP " + res.status);
      return await res.json();
    } finally {
      clearTimeout(timer);
    }
  }

  // ── 연결 상태 배지 ────────────────────────────────────────────────
  function badge(state) {
    let el = document.getElementById("api-badge");
    if (!el) {
      el = document.createElement("div");
      el.id = "api-badge";
      el.style.cssText =
        "position:fixed;top:14px;right:14px;z-index:999;font:700 12px/1 " +
        "Pretendard,system-ui,sans-serif;padding:8px 13px;border-radius:999px;" +
        "box-shadow:0 6px 15px rgba(150,120,100,.18);cursor:default;transition:.2s";
      el.title = "API: " + API_BASE;
      document.body.appendChild(el);
    }
    if (state === "live") {
      el.style.background = "#CCE7DF";
      el.style.color = "#2f7d68";
      el.textContent = "● 실시간 API";
    } else if (state === "loading") {
      el.style.background = "#F2DEAE";
      el.style.color = "#8a6d1f";
      el.textContent = "… 연결 중";
    } else {
      el.style.background = "#EDE6DF";
      el.style.color = "#94887F";
      el.textContent = "○ 데모 데이터";
    }
  }

  // ── enum → 한글 라벨 매핑 (백엔드 domain enum 과 1:1) ──────────────
  const LABELS = {
    adoption: {
      protected: "보호중",
      available: "입양 가능",
      reserved: "예약됨",
      adopted: "입양 완료",
    },
    transparency: {
      verified: { text: "검증됨", cls: "verified", mark: "✓ 검증됨" },
      basic: { text: "기본", cls: "basic", mark: "기본" },
      unverified: { text: "미검증", cls: "unverified", mark: "미검증" },
    },
    gender: { female: "여아", male: "남아", unknown: "성별 미상" },
    source: {
      public_api: { text: "공공데이터", cls: "public" },
      manual: { text: "보호소 기록", cls: "" },
    },
    eventIcon: {
      rescue: "🌳",
      intake: "🏠",
      medical: "🩺",
      vaccination: "💉",
      neuter: "✂️",
      available: "💗",
      adopted: "👨‍👩‍👧",
      post_adoption: "💌",
    },
  };

  function dogMeta(d) {
    // "추정 2살 · 믹스(추정) · 여아 · 중성화 완료"
    const parts = [];
    if (d.age_estimate) parts.push(d.age_estimate);
    if (d.breed_label) parts.push(d.breed_label);
    if (d.gender) parts.push(LABELS.gender[d.gender] || d.gender);
    if (d.is_neutered === true) parts.push("중성화 완료");
    else if (d.is_neutered === false) parts.push("중성화 전");
    return parts.join(" · ");
  }

  function fmtDate(iso) {
    if (!iso) return "지금";
    return iso.replaceAll("-", "."); // 2026-01-08 → 2026.01.08
  }

  // 전역으로 노출 (각 페이지 스크립트에서 사용)
  window.PawAPI = {
    API_BASE,
    pawFetch,
    badge,
    LABELS,
    dogMeta,
    fmtDate,
  };
})();
