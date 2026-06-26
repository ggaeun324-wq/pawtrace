"""Alembic 실행 환경.

핵심:
- 접속 URL 은 app.core.config(환경변수)에서 가져옵니다. → 시크릿 분리.
- app.models 를 import 해 모든 테이블 메타데이터를 등록합니다. → autogenerate 가
  모델과 실제 DB 의 차이를 감지할 수 있습니다.
- geoalchemy2 alembic_helpers 로 PostGIS Geometry 컬럼을 올바르게 렌더링하고,
  geoalchemy2 가 자동 관리하는 공간 인덱스의 불필요한 diff 를 무시합니다.
"""
from logging.config import fileConfig

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.session import Base

# 모델을 import 해야 Base.metadata 에 테이블이 등록됩니다.
import app.models  # noqa: F401,E402

config = context.config
# alembic.ini 대신 환경변수의 DATABASE_URL 을 사용.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# PawTrace 가 관리하는 테이블만 마이그레이션 대상에 포함합니다.
# postgis 이미지에는 spatial_ref_sys, tiger/topology 등 시스템 테이블이 많은데,
# 이를 'autogenerate' 가 '삭제된 테이블'로 오인해 drop 하지 않도록 필터링합니다.
_OWNED_TABLES = set(target_metadata.tables.keys())


def _include_object(obj, name, type_, reflected, compare_to):
    # DB 에만 있고 우리 모델엔 없는 테이블(=postgis 시스템 테이블)은 무시.
    if type_ == "table" and reflected and name not in _OWNED_TABLES:
        return False
    return alembic_helpers.include_object(obj, name, type_, reflected, compare_to)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=alembic_helpers.render_item,
        include_object=_include_object,
        process_revision_directives=alembic_helpers.writer,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=alembic_helpers.render_item,
            include_object=_include_object,
            process_revision_directives=alembic_helpers.writer,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
