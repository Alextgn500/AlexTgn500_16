BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "tasks" (
	"id"	INTEGER NOT NULL,
	"title"	VARCHAR,
	"content"	VARCHAR,
	"priority"	INTEGER,
	"completed"	BOOLEAN,
	"user_id"	INTEGER NOT NULL,
	"slug"	VARCHAR,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
INSERT INTO "tasks" ("id","title","content","priority","completed","user_id","slug") VALUES (4,'FourthTask','Content4',6,0,3,'fourthtask');
CREATE INDEX IF NOT EXISTS "ix_tasks_id" ON "tasks" (
	"id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "ix_tasks_slug" ON "tasks" (
	"slug"
);
CREATE INDEX IF NOT EXISTS "ix_tasks_user_id" ON "tasks" (
	"user_id"
);
COMMIT;
