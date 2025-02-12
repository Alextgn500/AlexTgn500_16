BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"username"	VARCHAR,
	"firstname"	VARCHAR,
	"lastname"	VARCHAR,
	"age"	INTEGER,
	"slug"	VARCHAR,
	PRIMARY KEY("id")
);
INSERT INTO "users" ("id","username","firstname","lastname","age","slug") VALUES (3,'user3','Bear','Gryll',25,'user3');
CREATE INDEX IF NOT EXISTS "ix_users_id" ON "users" (
	"id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "ix_users_slug" ON "users" (
	"slug"
);
COMMIT;
