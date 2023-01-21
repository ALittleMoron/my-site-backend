from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    CREATE EXTENSION pg_trgm;
    CREATE EXTENSION btree_gin;
    CREATE TABLE IF NOT EXISTS "anime_watch_list" (
        "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
        "id" UUID NOT NULL  PRIMARY KEY,
        "name" VARCHAR(255) NOT NULL,
        "native_name" VARCHAR(255),
        "description" TEXT,
        "my_opinion" TEXT,
        "score" SMALLINT,
        "repeat_view_count" INT NOT NULL  DEFAULT 0,
        "status" VARCHAR(20) NOT NULL  DEFAULT 'Запланирован',
        "kind" VARCHAR(10) NOT NULL  DEFAULT 'Не указано'
    );
    CREATE INDEX IF NOT EXISTS "idx_anime_watch_name_84cbd7" ON "anime_watch_list" USING GIN ("name", "description");
    COMMENT ON COLUMN "anime_watch_list"."created_at" IS 'Дата и время создания модели';
    COMMENT ON COLUMN "anime_watch_list"."updated_at" IS 'Дата и время обновления модели';
    COMMENT ON COLUMN "anime_watch_list"."id" IS 'Уникальный идентификатор модели';
    COMMENT ON COLUMN "anime_watch_list"."name" IS 'Название';
    COMMENT ON COLUMN "anime_watch_list"."native_name" IS 'Название на языке оригинала';
    COMMENT ON COLUMN "anime_watch_list"."description" IS 'Описание';
    COMMENT ON COLUMN "anime_watch_list"."my_opinion" IS 'Моё мнение';
    COMMENT ON COLUMN "anime_watch_list"."score" IS 'Оценка';
    COMMENT ON COLUMN "anime_watch_list"."repeat_view_count" IS 'Количество повторных просмотров/прочтений';
    COMMENT ON COLUMN "anime_watch_list"."status" IS 'Статус';
    COMMENT ON COLUMN "anime_watch_list"."kind" IS 'вид аниме';
    COMMENT ON TABLE "anime_watch_list" IS 'Модель аниме.';;
    CREATE TABLE IF NOT EXISTS "kinopoisk_watch_list" (
        "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
        "id" UUID NOT NULL  PRIMARY KEY,
        "name" VARCHAR(255) NOT NULL,
        "native_name" VARCHAR(255),
        "description" TEXT,
        "my_opinion" TEXT,
        "score" SMALLINT,
        "repeat_view_count" INT NOT NULL  DEFAULT 0,
        "status" VARCHAR(20) NOT NULL  DEFAULT 'Запланирован',
        "kind" VARCHAR(18) NOT NULL  DEFAULT 'Не указано'
    );
    CREATE INDEX IF NOT EXISTS "idx_kinopoisk_w_name_723d09" ON "kinopoisk_watch_list" USING GIN ("name", "description");
    COMMENT ON COLUMN "kinopoisk_watch_list"."created_at" IS 'Дата и время создания модели';
    COMMENT ON COLUMN "kinopoisk_watch_list"."updated_at" IS 'Дата и время обновления модели';
    COMMENT ON COLUMN "kinopoisk_watch_list"."id" IS 'Уникальный идентификатор модели';
    COMMENT ON COLUMN "kinopoisk_watch_list"."name" IS 'Название';
    COMMENT ON COLUMN "kinopoisk_watch_list"."native_name" IS 'Название на языке оригинала';
    COMMENT ON COLUMN "kinopoisk_watch_list"."description" IS 'Описание';
    COMMENT ON COLUMN "kinopoisk_watch_list"."my_opinion" IS 'Моё мнение';
    COMMENT ON COLUMN "kinopoisk_watch_list"."score" IS 'Оценка';
    COMMENT ON COLUMN "kinopoisk_watch_list"."repeat_view_count" IS 'Количество повторных просмотров/прочтений';
    COMMENT ON COLUMN "kinopoisk_watch_list"."status" IS 'Статус';
    COMMENT ON COLUMN "kinopoisk_watch_list"."kind" IS 'вид контента с Кинопоиска';
    COMMENT ON TABLE "kinopoisk_watch_list" IS 'Модель контента с Кинопоиска (фильмы, сериалы и мультики, кроме аниме).';;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "anime_watch_list";
        DROP TABLE IF EXISTS "kinopoisk_watch_list";
        DROP EXTENSION IF EXISTS pg_trgm;
        DROP EXTENSION IF EXISTS btree_gin;"""
