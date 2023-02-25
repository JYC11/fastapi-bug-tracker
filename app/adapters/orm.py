from collections import deque
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import registry, relationship

from app.domain import models

metadata = sa.MetaData()
mapper_registry = registry(metadata=metadata)


users = sa.Table(
    "bug_tracker_users",
    mapper_registry.metadata,
    sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    ),
    sa.Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "update_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
        server_default=sa.func.now(),
    ),
    sa.Column("username", sa.String(length=100), nullable=False),
    sa.Column("email", sa.String(length=100), nullable=False),
    sa.Column("password", sa.Text, nullable=False),
    sa.Column("user_type", sa.String(length=50), nullable=False),
    sa.Column("user_status", sa.String(length=50), nullable=False),
    sa.Column("is_admin", sa.Boolean),
    sa.Column("security_question", sa.Text, nullable=False),
    sa.Column("security_question_answer", sa.Text, nullable=False),
)

tags = sa.Table(
    "bug_tracker_tags",
    mapper_registry.metadata,
    sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    ),
    sa.Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "update_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
        server_default=sa.func.now(),
    ),
    sa.Column("name", sa.String(length=50), nullable=False),
)

bugs = sa.Table(
    "bug_tracker_bugs",
    mapper_registry.metadata,
    sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    ),
    sa.Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "update_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
        server_default=sa.func.now(),
    ),
    sa.Column("title", sa.String(length=50), nullable=False),
    sa.Column(
        "author_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(f"{users.name}.id", ondelete="cascade"),
        index=True,
        nullable=False,
    ),
    sa.Column(
        "assigned_user_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(f"{users.name}.id", ondelete="cascade"),
        index=True,
        nullable=True,
    ),
    sa.Column("description", sa.Text, nullable=False),
    sa.Column("edited", sa.Boolean),
    sa.Column("images", sa.ARRAY(sa.String(255)), nullable=True),
    sa.Column("urgency", sa.String(length=50), nullable=False),
    sa.Column("status", sa.String(length=50), nullable=False),
    sa.Column("record_status", sa.String(length=50), nullable=False),
    sa.Column("version", sa.Integer, nullable=False, default=1),
)

comments = sa.Table(
    "bug_tracker_comments",
    mapper_registry.metadata,
    sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    ),
    sa.Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "update_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "bug_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(f"{bugs.name}.id"),
        index=True,
        nullable=False,
    ),
    sa.Column(
        "author_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(f"{users.name}.id"),
        index=True,
        nullable=False,
    ),
    sa.Column("text", sa.Text, nullable=False),
    sa.Column("vote_count", sa.Integer, nullable=False),
    sa.Column("edited", sa.Boolean),
)

bug_tags = sa.Table(
    "bug_tracker_bug_tag",
    mapper_registry.metadata,
    sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    ),
    sa.Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "update_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "tag_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(f"{tags.name}.id", ondelete="cascade"),
        index=True,
    ),
    sa.Column(
        "bug_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(f"{bugs.name}.id", ondelete="cascade"),
        index=True,
    ),
)

event_store = sa.Table(
    "bug_tracker_event_store",
    mapper_registry.metadata,
    sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    ),
    sa.Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "aggregate_id",
        postgresql.UUID(as_uuid=True),
        index=True,
    ),
    sa.Column("event_name", sa.String(length=255), nullable=False),
    sa.Column("event_data", sa.JSON, nullable=False),
)


@sa.event.listens_for(models.Bugs, "load")
def receive_load_bugs_application_queue(bugs: models.Bugs, _):
    bugs.events = deque()


@sa.event.listens_for(models.Users, "load")
def receive_load_user_application_queue(users: models.Users, _):
    users.events = deque()


def start_mappers():
    mapper_registry.map_imperatively(
        models.Users,
        users,
        properties={
            "comments": relationship(
                models.Comments,
                back_populates="author",
            ),
            "raised_bugs": relationship(
                models.Bugs,
                back_populates="author",
                foreign_keys=[bugs.c.author_id],
            ),
            "assigned_bugs": relationship(
                models.Bugs,
                back_populates="assigned_to",
                foreign_keys=[bugs.c.assigned_user_id],
            ),
        },
    )
    mapper_registry.map_imperatively(
        models.Tags,
        tags,
        properties={
            "bug_tags": relationship(models.BugTags, back_populates="tag"),
        },
    )
    mapper_registry.map_imperatively(
        models.Comments,
        comments,
        properties={
            "bug": relationship(
                models.Bugs,
                back_populates="comments",
            ),
            "author": relationship(
                models.Users,
                back_populates="comments",
            ),
        },
    )
    mapper_registry.map_imperatively(
        models.BugTags,
        bug_tags,
        properties={
            "tag": relationship(
                models.Tags,
                back_populates="bug_tags",
            ),
            "bug": relationship(
                models.Bugs,
                back_populates="bug_tags",
            ),
        },
    )
    mapper_registry.map_imperatively(
        models.Bugs,
        bugs,
        properties={
            "author": relationship(
                models.Users,
                back_populates="raised_bugs",
                foreign_keys=[bugs.c.author_id],
            ),
            "assigned_to": relationship(
                models.Users,
                back_populates="assigned_bugs",
                foreign_keys=[bugs.c.assigned_user_id],
            ),
            "bug_tags": relationship(
                models.BugTags,
                back_populates="bug",
            ),
            "comments": relationship(
                models.Comments,
                back_populates="bug",
            ),
        },
    )
    mapper_registry.map_imperatively(
        models.EventStore,
        event_store,
    )
