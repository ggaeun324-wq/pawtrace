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

  // ── 인증(JWT) 헬퍼 ────────────────────────────────────────────────
  //   토큰/사용자 정보는 localStorage 에 보관합니다(데모 수준).
  const TOKEN_KEY = "pawtrace_token";
  const USER_KEY = "pawtrace_user";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }
  function getUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY));
    } catch {
      return null;
    }
  }
  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  // 인증이 필요한 호출용 fetch (Authorization 헤더 자동 첨부)
  async function pawSend(path, method, body, withAuth) {
    const headers = { "Content-Type": "application/json" };
    if (withAuth && getToken()) headers["Authorization"] = "Bearer " + getToken();
    const res = await fetch(API_BASE + path, {
      method: method || "GET",
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = (data && data.detail) || "요청 실패 (HTTP " + res.status + ")";
      throw new Error(typeof msg === "string" ? msg : "입력값을 확인해 주세요.");
    }
    return data;
  }

  async function register(payload) {
    return pawSend("/auth/register", "POST", payload, false);
  }
  async function login(email, password) {
    const tok = await pawSend("/auth/login", "POST", { email, password }, false);
    localStorage.setItem(TOKEN_KEY, tok.access_token);
    const me = await pawSend("/auth/me", "GET", null, true);
    localStorage.setItem(USER_KEY, JSON.stringify(me));
    return me;
  }

  const ROLE_LABEL = {
    user: "일반 사용자",
    shelter_staff: "보호소 직원",
    admin: "플랫폼 관리자",
  };

  // 모든 페이지 우상단에 로그인 상태 칩을 표시
  function authChip() {
    let el = document.getElementById("auth-chip");
    if (!el) {
      el = document.createElement("div");
      el.id = "auth-chip";
      el.style.cssText =
        "position:fixed;top:14px;right:130px;z-index:999;font:700 12px/1 " +
        "Pretendard,system-ui,sans-serif;padding:8px 13px;border-radius:999px;" +
        "box-shadow:0 6px 15px rgba(150,120,100,.18);background:#fff;color:#7a6a5d;" +
        "text-decoration:none;cursor:pointer";
      document.body.appendChild(el);
    }
    const u = getUser();
    if (u) {
      el.textContent = "🐾 " + u.display_name + " (" + (ROLE_LABEL[u.role] || u.role) + ") · 로그아웃";
      el.onclick = () => {
        logout();
        location.reload();
      };
    } else {
      el.textContent = "🐾 로그인 / 회원가입";
      el.onclick = () => (location.href = "login.html");
    }
  }

  // 전역으로 노출 (각 페이지 스크립트에서 사용)
  window.PawAPI = {
    API_BASE,
    pawFetch,
    pawSend,
    badge,
    LABELS,
    dogMeta,
    fmtDate,
    register,
    login,
    logout,
    getToken,
    getUser,
    authChip,
    ROLE_LABEL,
  };

  // 모든 페이지에서 로그인 상태 칩을 자동 표시
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", authChip);
  } else {
    authChip();
  }
})();
