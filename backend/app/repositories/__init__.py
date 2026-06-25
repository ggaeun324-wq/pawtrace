"""저장소(Repository) 계층.

DB 접근을 추상화합니다. MVP 첫 실행 편의를 위해 현재는 메모리 시드 데이터를
반환하며, 실제 구현 시 SQLAlchemy 쿼리로 교체합니다. (services는 이 계약만 의존)
"""
