BEGIN;
DROP TABLE "hr_book_tags";
ALTER TABLE "hr_readingoccasion" DROP CONSTRAINT "reader_id_refs_id_52d2ec";
DROP TABLE "hr_reader";
ALTER TABLE "hr_readingoccasion" DROP CONSTRAINT "book_id_refs_id_3a724fa4";
DROP TABLE "hr_book";
DROP TABLE "hr_tag";
DROP TABLE "hr_readingoccasion";
CREATE TABLE "hr_readingoccasion" (
    "id" serial NOT NULL PRIMARY KEY,
    "reader_id" integer NOT NULL,
    "book_id" integer NOT NULL,
    "finished" date NOT NULL,
    "reading_time" numeric(5, 2) NOT NULL,
    "notes" text NOT NULL
);
CREATE TABLE "hr_tag" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(200) NOT NULL UNIQUE
);
CREATE TABLE "hr_book" (
    "id" serial NOT NULL PRIMARY KEY,
    "title" varchar(200) NOT NULL,
    "author" varchar(200) NOT NULL,
    "isbn" varchar(15) NOT NULL,
    "summary" text NOT NULL
);
ALTER TABLE "hr_readingoccasion" ADD CONSTRAINT book_id_refs_id_3a724fa4 FOREIGN KEY ("book_id") REFERENCES "hr_book" ("id");
CREATE TABLE "hr_reader" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "bio" text NOT NULL,
    "picture" varchar(100) NOT NULL
);
ALTER TABLE "hr_readingoccasion" ADD CONSTRAINT reader_id_refs_id_52d2ec FOREIGN KEY ("reader_id") REFERENCES "hr_reader" ("id");
CREATE TABLE "hr_book_tags" (
    "id" serial NOT NULL PRIMARY KEY,
    "book_id" integer NOT NULL REFERENCES "hr_book" ("id"),
    "tag_id" integer NOT NULL REFERENCES "hr_tag" ("id"),
    UNIQUE ("book_id", "tag_id")
);
CREATE INDEX hr_readingoccasion_reader_id ON "hr_readingoccasion" ("reader_id");
CREATE INDEX hr_readingoccasion_book_id ON "hr_readingoccasion" ("book_id");
CREATE INDEX hr_reader_user_id ON "hr_reader" ("user_id");
DROP TABLE "django_admin_log";
CREATE TABLE "django_admin_log" (
    "id" serial NOT NULL PRIMARY KEY,
    "action_time" timestamp with time zone NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "content_type_id" integer NULL REFERENCES "django_content_type" ("id"),
    "object_id" text NULL,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint CHECK ("action_flag" >= 0) NOT NULL,
    "change_message" text NOT NULL
);
CREATE INDEX django_admin_log_user_id ON "django_admin_log" ("user_id");
CREATE INDEX django_admin_log_content_type_id ON "django_admin_log" ("content_type_id");
DROP TABLE "auth_user_user_permissions";
DROP TABLE "auth_user_groups";
DROP TABLE "auth_group_permissions";
DROP TABLE "auth_permission";
ALTER TABLE "auth_message" DROP CONSTRAINT "user_id_refs_id_650f49a6";
DROP TABLE "auth_user";
DROP TABLE "auth_group";
DROP TABLE "auth_message";
CREATE TABLE "auth_message" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "message" text NOT NULL
);
CREATE TABLE "auth_group" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL UNIQUE
);
CREATE TABLE "auth_user" (
    "id" serial NOT NULL PRIMARY KEY,
    "username" varchar(30) NOT NULL UNIQUE,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL,
    "email" varchar(75) NOT NULL,
    "password" varchar(128) NOT NULL,
    "is_staff" boolean NOT NULL,
    "is_active" boolean NOT NULL,
    "is_superuser" boolean NOT NULL,
    "last_login" timestamp with time zone NOT NULL,
    "date_joined" timestamp with time zone NOT NULL
);
ALTER TABLE "auth_message" ADD CONSTRAINT user_id_refs_id_650f49a6 FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id");
CREATE TABLE "auth_permission" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "codename" varchar(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);
CREATE TABLE "auth_group_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("group_id", "permission_id")
);
CREATE TABLE "auth_user_groups" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
    UNIQUE ("user_id", "group_id")
);
CREATE TABLE "auth_user_user_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("user_id", "permission_id")
);
CREATE INDEX auth_message_user_id ON "auth_message" ("user_id");
CREATE INDEX auth_permission_content_type_id ON "auth_permission" ("content_type_id");
COMMIT;
