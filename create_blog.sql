BEGIN;
--
-- Create model Post
--
CREATE TABLE "blog_post" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(250) NOT NULL, "slug" varchar(250) NOT NULL, "body" text NOT NULL, "publish" datetime NOT NULL, "created" datetime NOT NULL, "updated" datetime NOT NULL, "status" varchar(2) NOT NULL, "author_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "blog_post_slug_b95473f2" ON "blog_post" ("slug");
CREATE INDEX "blog_post_author_id_dd7a8485" ON "blog_post" ("author_id");
CREATE INDEX "blog_post_publish_bb7600_idx" ON "blog_post" ("publish" DESC);
COMMIT;
BEGIN;
--
-- Alter field status on post
--
CREATE TABLE "new__blog_post" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(2) NOT NULL, "title" varchar(250) NOT NULL, "slug" varchar(250) NOT NULL, "body" text NOT NULL, "publish" datetime NOT NULL, "created" datetime NOT NULL, "updated" datetime NOT NULL, "author_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__blog_post" ("id", "title", "slug", "body", "publish", "created", "updated", "author_id", "status") SELECT "id", "title", "slug", "body", "publish", "created", "updated", "author_id", "status" FROM "blog_post";
DROP TABLE "blog_post";
ALTER TABLE "new__blog_post" RENAME TO "blog_post";
CREATE INDEX "blog_post_slug_b95473f2" ON "blog_post" ("slug");
CREATE INDEX "blog_post_author_id_dd7a8485" ON "blog_post" ("author_id");
CREATE INDEX "blog_post_publish_bb7600_idx" ON "blog_post" ("publish" DESC);
COMMIT;
