# Launch your local Phoenix instance:


https://github.com/Arize-ai/phoenix/blob/main/tutorials/tracing/openai_sessions_tutorial.ipynb




```
pip install arize-phoenix
phoenix serve


```



# Install packages:

```
pip install arize-phoenix-otel
Set your Phoenix endpoint:

import os

os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006"
```


pip install openinference-instrumentation-langchain


```angular2html

820 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("project_sessions")
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_project_id")
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_project_sessions_1")
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,820 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,822 INFO sqlalchemy.engine.Engine
CREATE TABLE _alembic_tmp_trace_annotations (
	id INTEGER NOT NULL,
	trace_rowid INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	label VARCHAR,
	score FLOAT,
	explanation VARCHAR,
	metadata NUMERIC NOT NULL,
	annotator_kind VARCHAR NOT NULL,
	created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	user_id INTEGER,
	identifier VARCHAR DEFAULT '' NOT NULL,
	source VARCHAR,
	CONSTRAINT pk_trace_annotations PRIMARY KEY (id),
	CONSTRAINT fk_trace_annotations_trace_rowid_traces FOREIGN KEY(trace_rowid) REFERENCES traces (id) ON DELETE CASCADE,
	CONSTRAINT fk_trace_annotations_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL,
	CONSTRAINT "ck_trace_annotations_`valid_annotator_kind`" CHECK (annotator_kind IN ('LLM', 'CODE', 'HUMAN')),
	CONSTRAINT uq_trace_annotations_name_trace_rowid_identifier UNIQUE (name, trace_rowid, identifier)
)


2025-05-14 18:47:03,822 INFO sqlalchemy.engine.Engine [no key 0.00004s] ()
2025-05-14 18:47:03,822 INFO sqlalchemy.engine.Engine INSERT INTO _alembic_tmp_trace_annotations (id, trace_rowid, name, label, score, explanation, metadata, annotator_kind, created_at, updated_at) SELECT trace_annotations.id, trace_annotations.trace_rowid, trace_annotations.name, trace_annotations.label, trace_annotations.score, trace_annotations.explanation, trace_annotations.metadata, trace_annotations.annotator_kind, trace_annotations.created_at, trace_annotations.updated_at
FROM trace_annotations
2025-05-14 18:47:03,822 INFO sqlalchemy.engine.Engine [generated in 0.00005s] ()
2025-05-14 18:47:03,823 INFO sqlalchemy.engine.Engine
DROP TABLE trace_annotations
2025-05-14 18:47:03,823 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,824 INFO sqlalchemy.engine.Engine ALTER TABLE _alembic_tmp_trace_annotations RENAME TO trace_annotations
2025-05-14 18:47:03,824 INFO sqlalchemy.engine.Engine [no key 0.00005s] ()
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine CREATE INDEX ix_trace_annotations_trace_rowid ON trace_annotations (trace_rowid)
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine [no key 0.00004s] ()
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine
                UPDATE trace_annotations
                SET source = CASE
                    WHEN annotator_kind = 'HUMAN' THEN 'APP'
                    ELSE 'API'
                END

2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine [generated in 0.00003s] ()
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("trace_annotations")
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine [raw sql] ('trace_annotations',)
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("trace_annotations")
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine [raw sql] ('trace_annotations',)
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("trace_annotations")
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,825 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_trace_annotations_trace_rowid")
2025-05-14 18:47:03,826 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,826 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("trace_annotations")
2025-05-14 18:47:03,826 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,826 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_trace_annotations_trace_rowid")
2025-05-14 18:47:03,826 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,826 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_trace_annotations_1")
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine [raw sql] ('trace_annotations',)
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("traces")
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,827 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("traces")
2025-05-14 18:47:03,828 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,828 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,828 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("traces")
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_session_rowid")
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_rowid")
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_start_time")
2025-05-14 18:47:03,829 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("traces")
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_session_rowid")
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_rowid")
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_start_time")
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_traces_1")
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("projects")
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("projects")
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,830 INFO sqlalchemy.engine.Engine PRAGMA temp.foreign_key_list("projects")
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("projects")
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_projects_1")
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("project_sessions")
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,831 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("project_sessions")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("project_sessions")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_project_id")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("project_sessions")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_project_id")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_project_sessions_1")
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,832 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("users")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("users")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("users")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_email")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_user_role_id")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_user_id")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_username")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_client_id")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("users")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_email")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_user_role_id")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_user_id")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_username")
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,833 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_client_id")
2025-05-14 18:47:03,834 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,834 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_users_1")
2025-05-14 18:47:03,834 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,834 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,834 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,834 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("user_roles")
2025-05-14 18:47:03,834 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("user_roles")
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine PRAGMA temp.foreign_key_list("user_roles")
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("user_roles")
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_user_roles_name")
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("user_roles")
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_user_roles_name")
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,835 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,837 INFO sqlalchemy.engine.Engine
CREATE TABLE _alembic_tmp_trace_annotations (
	id INTEGER NOT NULL,
	trace_rowid INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	label VARCHAR,
	score FLOAT,
	explanation VARCHAR,
	metadata NUMERIC NOT NULL,
	annotator_kind VARCHAR NOT NULL,
	created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	user_id INTEGER,
	identifier VARCHAR DEFAULT ('') NOT NULL,
	source VARCHAR NOT NULL,
	CONSTRAINT pk_trace_annotations PRIMARY KEY (id),
	CONSTRAINT "ck_trace_annotations_`valid_annotator_kind`" CHECK (annotator_kind IN ('LLM', 'CODE', 'HUMAN')),
	CONSTRAINT uq_trace_annotations_name_trace_rowid_identifier UNIQUE (name, trace_rowid, identifier),
	CONSTRAINT fk_trace_annotations_trace_rowid_traces FOREIGN KEY(trace_rowid) REFERENCES traces (id) ON DELETE CASCADE,
	CONSTRAINT fk_trace_annotations_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL,
	CONSTRAINT "ck_trace_annotations_`valid_source`" CHECK (source IN ('API', 'APP'))
)


2025-05-14 18:47:03,837 INFO sqlalchemy.engine.Engine [no key 0.00008s] ()
2025-05-14 18:47:03,838 INFO sqlalchemy.engine.Engine INSERT INTO _alembic_tmp_trace_annotations (id, trace_rowid, name, label, score, explanation, metadata, annotator_kind, created_at, updated_at, user_id, identifier, source) SELECT trace_annotations.id, trace_annotations.trace_rowid, trace_annotations.name, trace_annotations.label, trace_annotations.score, trace_annotations.explanation, trace_annotations.metadata, trace_annotations.annotator_kind, trace_annotations.created_at, trace_annotations.updated_at, trace_annotations.user_id, trace_annotations.identifier, trace_annotations.source
FROM trace_annotations
2025-05-14 18:47:03,838 INFO sqlalchemy.engine.Engine [generated in 0.00007s] ()
2025-05-14 18:47:03,838 INFO sqlalchemy.engine.Engine
DROP TABLE trace_annotations
2025-05-14 18:47:03,838 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,838 INFO sqlalchemy.engine.Engine ALTER TABLE _alembic_tmp_trace_annotations RENAME TO trace_annotations
2025-05-14 18:47:03,838 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,839 INFO sqlalchemy.engine.Engine CREATE INDEX ix_trace_annotations_trace_rowid ON trace_annotations (trace_rowid)
2025-05-14 18:47:03,839 INFO sqlalchemy.engine.Engine [no key 0.00003s] ()
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("document_annotations")
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine [raw sql] ('document_annotations',)
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("document_annotations")
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine [raw sql] ('document_annotations',)
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("document_annotations")
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_score")
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_span_rowid")
2025-05-14 18:47:03,840 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_label")
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("document_annotations")
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_score")
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_span_rowid")
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_label")
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_document_annotations_1")
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,841 INFO sqlalchemy.engine.Engine [raw sql] ('document_annotations',)
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("spans")
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ('spans',)
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("spans")
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ('spans',)
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("spans")
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_cumulative_llm_token_count_total")
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_latency")
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_trace_rowid")
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_parent_id")
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,842 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_start_time")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("spans")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_cumulative_llm_token_count_total")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_latency")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_trace_rowid")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_parent_id")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_start_time")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_spans_1")
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,843 INFO sqlalchemy.engine.Engine [raw sql] ('spans',)
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("traces")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("traces")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("traces")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_session_rowid")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_rowid")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_start_time")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("traces")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_session_rowid")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_rowid")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_start_time")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_traces_1")
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,844 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("projects")
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("projects")
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine PRAGMA temp.foreign_key_list("projects")
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("projects")
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_projects_1")
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,845 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("project_sessions")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("project_sessions")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("project_sessions")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_project_id")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("project_sessions")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_project_id")
2025-05-14 18:47:03,846 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_project_sessions_1")
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,847 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,848 INFO sqlalchemy.engine.Engine
CREATE TABLE _alembic_tmp_document_annotations (
	id INTEGER NOT NULL,
	span_rowid INTEGER NOT NULL,
	document_position INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	label VARCHAR,
	score FLOAT,
	explanation VARCHAR,
	metadata NUMERIC NOT NULL,
	annotator_kind VARCHAR NOT NULL,
	created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	user_id INTEGER,
	identifier VARCHAR DEFAULT '' NOT NULL,
	source VARCHAR,
	CONSTRAINT pk_document_annotations PRIMARY KEY (id),
	CONSTRAINT fk_document_annotations_span_rowid_spans FOREIGN KEY(span_rowid) REFERENCES spans (id) ON DELETE CASCADE,
	CONSTRAINT fk_document_annotations_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL,
	CONSTRAINT "ck_document_annotations_`valid_annotator_kind`" CHECK (annotator_kind IN ('LLM', 'CODE', 'HUMAN')),
	CONSTRAINT uq_document_annotations_name_span_rowid_document_pos_identifier UNIQUE (name, span_rowid, document_position, identifier)
)


2025-05-14 18:47:03,848 INFO sqlalchemy.engine.Engine [no key 0.00007s] ()
2025-05-14 18:47:03,849 INFO sqlalchemy.engine.Engine INSERT INTO _alembic_tmp_document_annotations (id, span_rowid, document_position, name, label, score, explanation, metadata, annotator_kind, created_at, updated_at) SELECT document_annotations.id, document_annotations.span_rowid, document_annotations.document_position, document_annotations.name, document_annotations.label, document_annotations.score, document_annotations.explanation, document_annotations.metadata, document_annotations.annotator_kind, document_annotations.created_at, document_annotations.updated_at
FROM document_annotations
2025-05-14 18:47:03,849 INFO sqlalchemy.engine.Engine [generated in 0.00006s] ()
2025-05-14 18:47:03,849 INFO sqlalchemy.engine.Engine
DROP TABLE document_annotations
2025-05-14 18:47:03,849 INFO sqlalchemy.engine.Engine [no key 0.00003s] ()
2025-05-14 18:47:03,850 INFO sqlalchemy.engine.Engine ALTER TABLE _alembic_tmp_document_annotations RENAME TO document_annotations
2025-05-14 18:47:03,850 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine CREATE INDEX ix_document_annotations_span_rowid ON document_annotations (span_rowid)
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine [no key 0.00003s] ()
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine
                UPDATE document_annotations
                SET source = CASE
                    WHEN annotator_kind = 'HUMAN' THEN 'APP'
                    ELSE 'API'
                END

2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine [generated in 0.00004s] ()
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("document_annotations")
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine [raw sql] ('document_annotations',)
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("document_annotations")
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,851 INFO sqlalchemy.engine.Engine [raw sql] ('document_annotations',)
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("document_annotations")
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_span_rowid")
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("document_annotations")
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_document_annotations_span_rowid")
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_document_annotations_1")
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,852 INFO sqlalchemy.engine.Engine [raw sql] ('document_annotations',)
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("spans")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ('spans',)
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("spans")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ('spans',)
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("spans")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_cumulative_llm_token_count_total")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_latency")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_trace_rowid")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_parent_id")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_start_time")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("spans")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_cumulative_llm_token_count_total")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_latency")
2025-05-14 18:47:03,853 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_trace_rowid")
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_parent_id")
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_spans_start_time")
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_spans_1")
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,854 INFO sqlalchemy.engine.Engine [raw sql] ('spans',)
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("traces")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("traces")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("traces")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_session_rowid")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_rowid")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_start_time")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("traces")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_session_rowid")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_project_rowid")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_traces_start_time")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_traces_1")
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,855 INFO sqlalchemy.engine.Engine [raw sql] ('traces',)
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("projects")
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("projects")
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine PRAGMA temp.foreign_key_list("projects")
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("projects")
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_projects_1")
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,856 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("project_sessions")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("project_sessions")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("project_sessions")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_project_id")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("project_sessions")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_project_id")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_start_time")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_project_sessions_end_time")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_project_sessions_1")
2025-05-14 18:47:03,857 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine [raw sql] ('project_sessions',)
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("users")
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("users")
2025-05-14 18:47:03,858 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("users")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_email")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_user_role_id")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_user_id")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_username")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_client_id")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("users")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_email")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_user_role_id")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_user_id")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_username")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_client_id")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_users_1")
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,859 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("user_roles")
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("user_roles")
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine PRAGMA temp.foreign_key_list("user_roles")
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("user_roles")
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_user_roles_name")
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("user_roles")
2025-05-14 18:47:03,860 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,861 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_user_roles_name")
2025-05-14 18:47:03,861 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,861 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,861 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,862 INFO sqlalchemy.engine.Engine
CREATE TABLE _alembic_tmp_document_annotations (
	id INTEGER NOT NULL,
	span_rowid INTEGER NOT NULL,
	document_position INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	label VARCHAR,
	score FLOAT,
	explanation VARCHAR,
	metadata NUMERIC NOT NULL,
	annotator_kind VARCHAR NOT NULL,
	created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	user_id INTEGER,
	identifier VARCHAR DEFAULT ('') NOT NULL,
	source VARCHAR NOT NULL,
	CONSTRAINT pk_document_annotations PRIMARY KEY (id),
	CONSTRAINT "ck_document_annotations_`valid_annotator_kind`" CHECK (annotator_kind IN ('LLM', 'CODE', 'HUMAN')),
	CONSTRAINT fk_document_annotations_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL,
	CONSTRAINT fk_document_annotations_span_rowid_spans FOREIGN KEY(span_rowid) REFERENCES spans (id) ON DELETE CASCADE,
	CONSTRAINT uq_document_annotations_name_span_rowid_document_pos_identifier UNIQUE (name, span_rowid, document_position, identifier),
	CONSTRAINT "ck_document_annotations_`valid_source`" CHECK (source IN ('API', 'APP'))
)


2025-05-14 18:47:03,862 INFO sqlalchemy.engine.Engine [no key 0.00007s] ()
2025-05-14 18:47:03,863 INFO sqlalchemy.engine.Engine INSERT INTO _alembic_tmp_document_annotations (id, span_rowid, document_position, name, label, score, explanation, metadata, annotator_kind, created_at, updated_at, user_id, identifier, source) SELECT document_annotations.id, document_annotations.span_rowid, document_annotations.document_position, document_annotations.name, document_annotations.label, document_annotations.score, document_annotations.explanation, document_annotations.metadata, document_annotations.annotator_kind, document_annotations.created_at, document_annotations.updated_at, document_annotations.user_id, document_annotations.identifier, document_annotations.source
FROM document_annotations
2025-05-14 18:47:03,863 INFO sqlalchemy.engine.Engine [generated in 0.00006s] ()
2025-05-14 18:47:03,863 INFO sqlalchemy.engine.Engine
DROP TABLE document_annotations
2025-05-14 18:47:03,863 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,863 INFO sqlalchemy.engine.Engine ALTER TABLE _alembic_tmp_document_annotations RENAME TO document_annotations
2025-05-14 18:47:03,863 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,864 INFO sqlalchemy.engine.Engine CREATE INDEX ix_document_annotations_span_rowid ON document_annotations (span_rowid)
2025-05-14 18:47:03,864 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine
CREATE TABLE annotation_configs (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	config JSONB NOT NULL,
	CONSTRAINT pk_annotation_configs PRIMARY KEY (id),
	CONSTRAINT uq_annotation_configs_name UNIQUE (name)
)


2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine [no key 0.00003s] ()
2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine
CREATE TABLE project_annotation_configs (
	id INTEGER NOT NULL,
	project_id INTEGER NOT NULL,
	annotation_config_id INTEGER NOT NULL,
	CONSTRAINT pk_project_annotation_configs PRIMARY KEY (id),
	CONSTRAINT uq_project_annotation_configs_project_id_annotation_config_id UNIQUE (project_id, annotation_config_id),
	CONSTRAINT fk_project_annotation_configs_project_id_projects FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE,
	CONSTRAINT fk_project_annotation_configs_annotation_config_id_annotation_configs FOREIGN KEY(annotation_config_id) REFERENCES annotation_configs (id) ON DELETE CASCADE
)


2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine [no key 0.00004s] ()
2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine CREATE INDEX ix_project_annotation_configs_project_id ON project_annotation_configs (project_id)
2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine CREATE INDEX ix_project_annotation_configs_annotation_config_id ON project_annotation_configs (annotation_config_id)
2025-05-14 18:47:03,865 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,866 INFO sqlalchemy.engine.Engine UPDATE alembic_version SET version_num='2f9d1a65945f' WHERE alembic_version.version_num = 'bc8fea3c2bc8'
2025-05-14 18:47:03,866 INFO sqlalchemy.engine.Engine [generated in 0.00004s] ()
2025-05-14 18:47:03,866 INFO sqlalchemy.engine.Engine
CREATE TABLE project_trace_retention_policies (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	cron_expression VARCHAR NOT NULL,
	rule JSONB NOT NULL,
	CONSTRAINT pk_project_trace_retention_policies PRIMARY KEY (id)
)


2025-05-14 18:47:03,866 INFO sqlalchemy.engine.Engine [no key 0.00003s] ()
2025-05-14 18:47:03,866 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("projects")
2025-05-14 18:47:03,866 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("projects")
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine PRAGMA temp.foreign_key_list("projects")
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("projects")
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("projects")
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_projects_1")
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,867 INFO sqlalchemy.engine.Engine [raw sql] ('projects',)
2025-05-14 18:47:03,868 INFO sqlalchemy.engine.Engine
CREATE TABLE _alembic_tmp_projects (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	description VARCHAR,
	gradient_start_color VARCHAR DEFAULT '#5bdbff' NOT NULL,
	gradient_end_color VARCHAR DEFAULT '#1c76fc' NOT NULL,
	created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	trace_retention_policy_id INTEGER,
	CONSTRAINT pk_projects PRIMARY KEY (id),
	CONSTRAINT uq_projects_name UNIQUE (name),
	CONSTRAINT fk_projects_trace_retention_policy_id_project_trace_retention_policies FOREIGN KEY(trace_retention_policy_id) REFERENCES project_trace_retention_policies (id) ON DELETE SET NULL
)


2025-05-14 18:47:03,868 INFO sqlalchemy.engine.Engine [no key 0.00003s] ()
2025-05-14 18:47:03,869 INFO sqlalchemy.engine.Engine INSERT INTO _alembic_tmp_projects (id, name, description, gradient_start_color, gradient_end_color, created_at, updated_at) SELECT projects.id, projects.name, projects.description, projects.gradient_start_color, projects.gradient_end_color, projects.created_at, projects.updated_at
FROM projects
2025-05-14 18:47:03,869 INFO sqlalchemy.engine.Engine [generated in 0.00004s] ()
2025-05-14 18:47:03,869 INFO sqlalchemy.engine.Engine
DROP TABLE projects
2025-05-14 18:47:03,869 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,869 INFO sqlalchemy.engine.Engine ALTER TABLE _alembic_tmp_projects RENAME TO projects
2025-05-14 18:47:03,869 INFO sqlalchemy.engine.Engine [no key 0.00004s] ()
2025-05-14 18:47:03,870 INFO sqlalchemy.engine.Engine CREATE INDEX ix_projects_trace_retention_policy_id ON projects (trace_retention_policy_id)
2025-05-14 18:47:03,870 INFO sqlalchemy.engine.Engine [no key 0.00012s] ()
2025-05-14 18:47:03,870 INFO sqlalchemy.engine.Engine UPDATE alembic_version SET version_num='bb8139330879' WHERE alembic_version.version_num = '2f9d1a65945f'
2025-05-14 18:47:03,870 INFO sqlalchemy.engine.Engine [generated in 0.00004s] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("prompt_versions")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ('prompt_versions',)
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("prompt_versions")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ('prompt_versions',)
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("prompt_versions")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompt_versions_prompt_id")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompt_versions_user_id")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("prompt_versions")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompt_versions_prompt_id")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompt_versions_user_id")
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,871 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,872 INFO sqlalchemy.engine.Engine [raw sql] ('prompt_versions',)
2025-05-14 18:47:03,872 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("prompts")
2025-05-14 18:47:03,872 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,872 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,872 INFO sqlalchemy.engine.Engine [raw sql] ('prompts',)
2025-05-14 18:47:03,872 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("prompts")
2025-05-14 18:47:03,872 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ('prompts',)
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("prompts")
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompts_source_prompt_id")
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompts_name")
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("prompts")
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompts_source_prompt_id")
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_prompts_name")
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,873 INFO sqlalchemy.engine.Engine [raw sql] ('prompts',)
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("users")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("users")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("users")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_email")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_user_role_id")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_user_id")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_username")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_client_id")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("users")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_email")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_user_role_id")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_user_id")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_username")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_users_oauth2_client_id")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("sqlite_autoindex_users_1")
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,874 INFO sqlalchemy.engine.Engine [raw sql] ('users',)
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("user_roles")
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine PRAGMA main.foreign_key_list("user_roles")
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine PRAGMA temp.foreign_key_list("user_roles")
2025-05-14 18:47:03,875 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("user_roles")
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_user_roles_name")
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine PRAGMA main.index_list("user_roles")
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine PRAGMA main.index_info("ix_user_roles_name")
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine [raw sql] ()
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
2025-05-14 18:47:03,876 INFO sqlalchemy.engine.Engine [raw sql] ('user_roles',)
2025-05-14 18:47:03,877 INFO sqlalchemy.engine.Engine
CREATE TABLE _alembic_tmp_prompt_versions (
	id INTEGER NOT NULL,
	prompt_id INTEGER NOT NULL,
	description VARCHAR,
	user_id INTEGER,
	template_type VARCHAR NOT NULL,
	template_format VARCHAR NOT NULL,
	template NUMERIC NOT NULL,
	invocation_parameters NUMERIC NOT NULL,
	tools JSON,
	response_format JSON,
	model_provider VARCHAR NOT NULL,
	model_name VARCHAR NOT NULL,
	metadata NUMERIC NOT NULL,
	created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT "ck_prompt_versions_`template_format`" CHECK (template_format IN ('F_STRING', 'MUSTACHE', 'NONE')),
	CONSTRAINT "ck_prompt_versions_`template_type`" CHECK (template_type IN ('CHAT', 'STR')),
	CONSTRAINT fk_prompt_versions_prompt_id_prompts FOREIGN KEY(prompt_id) REFERENCES prompts (id) ON DELETE CASCADE,
	CONSTRAINT fk_prompt_versions_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
)


2025-05-14 18:47:03,877 INFO sqlalchemy.engine.Engine [no key 0.00006s] ()
2025-05-14 18:47:03,878 INFO sqlalchemy.engine.Engine INSERT INTO _alembic_tmp_prompt_versions (id, prompt_id, description, user_id, template_type, template_format, template, invocation_parameters, tools, response_format, model_provider, model_name, metadata, created_at) SELECT prompt_versions.id, prompt_versions.prompt_id, prompt_versions.description, prompt_versions.user_id, prompt_versions.template_type, prompt_versions.template_format, prompt_versions.template, prompt_versions.invocation_parameters, prompt_versions.tools, prompt_versions.response_format, prompt_versions.model_provider, prompt_versions.model_name, prompt_versions.metadata, prompt_versions.created_at
FROM prompt_versions
2025-05-14 18:47:03,878 INFO sqlalchemy.engine.Engine [generated in 0.00007s] ()
2025-05-14 18:47:03,878 INFO sqlalchemy.engine.Engine
DROP TABLE prompt_versions
2025-05-14 18:47:03,878 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,878 INFO sqlalchemy.engine.Engine ALTER TABLE _alembic_tmp_prompt_versions RENAME TO prompt_versions
2025-05-14 18:47:03,878 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,879 INFO sqlalchemy.engine.Engine CREATE INDEX ix_prompt_versions_prompt_id ON prompt_versions (prompt_id)
2025-05-14 18:47:03,879 INFO sqlalchemy.engine.Engine [no key 0.00005s] ()
2025-05-14 18:47:03,879 INFO sqlalchemy.engine.Engine CREATE INDEX ix_prompt_versions_user_id ON prompt_versions (user_id)
2025-05-14 18:47:03,879 INFO sqlalchemy.engine.Engine [no key 0.00002s] ()
2025-05-14 18:47:03,880 INFO sqlalchemy.engine.Engine UPDATE alembic_version SET version_num='8a3764fe7f1a' WHERE alembic_version.version_num = 'bb8139330879'
2025-05-14 18:47:03,880 INFO sqlalchemy.engine.Engine [generated in 0.00004s] ()
2025-05-14 18:47:03,880 INFO sqlalchemy.engine.Engine COMMIT
---------------------------
✅ Migrations completed in 0.126 seconds.
INFO:     Started server process [48856]
INFO:     Waiting for application startup.


██████╗ ██╗  ██╗ ██████╗ ███████╗███╗   ██╗██╗██╗  ██╗
██╔══██╗██║  ██║██╔═══██╗██╔════╝████╗  ██║██║╚██╗██╔╝
██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║██║ ╚███╔╝
██╔═══╝ ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║██║ ██╔██╗
██║     ██║  ██║╚██████╔╝███████╗██║ ╚████║██║██╔╝ ██╗
╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝ v9.3.0

|
|  🌎 Join our Community 🌎
|  https://join.slack.com/t/arize-ai/shared_invite/zt-1px8dcmlf-fmThhDFD_V_48oU7ALan4Q
|
|  ⭐️ Leave us a Star ⭐️
|  https://github.com/Arize-ai/phoenix
|
|  📚 Documentation 📚
|  https://docs.arize.com/phoenix
|
|  🚀 Phoenix Server 🚀
|  Phoenix UI: http://0.0.0.0:6006
|  Authentication: False
|  Log traces:
|    - gRPC: http://0.0.0.0:4317
|    - HTTP: http://0.0.0.0:6006/v1/traces
|  Storage: sqlite:////Users/welcome/.phoenix/phoenix.db
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:6006 (Press CTRL+C to quit)
^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D^[[D

```
