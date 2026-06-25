"""DB 연결/세션 패키지 (SQLAlchemy).

MVP 첫 실행은 시드 데이터로 동작하므로 DB 없이도 API가 응답합니다.
실제 DB 사용 시 session.py 의 SessionLocal 을 라우터 의존성으로 주입하세요.
"""
