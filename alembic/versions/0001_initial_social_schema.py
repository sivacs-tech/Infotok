"""initial social schema

Revision ID: 0001_initial_social_schema
Revises:
Create Date: 2026-05-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_social_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_guest", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "reels",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("author_id", sa.String(), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("hashtags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("layers", sa.JSON(), nullable=True),
        sa.Column("thumbnail_url", sa.String(), nullable=True),
        sa.Column("background_audio_url", sa.String(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reels_author_id"), "reels", ["author_id"], unique=False)
    op.create_index(op.f("ix_reels_created_at"), "reels", ["created_at"], unique=False)
    op.create_index(op.f("ix_reels_id"), "reels", ["id"], unique=False)
    op.create_index(op.f("ix_reels_is_deleted"), "reels", ["is_deleted"], unique=False)

    op.create_table(
        "interactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("reel_id", sa.String(), nullable=False),
        sa.Column("interaction_type", sa.String(), nullable=False),
        sa.Column("view_time_ms", sa.Integer(), nullable=True),
        sa.Column("hashtags_involved", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["reel_id"], ["reels.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interactions_id"), "interactions", ["id"], unique=False)
    op.create_index(op.f("ix_interactions_interaction_type"), "interactions", ["interaction_type"], unique=False)
    op.create_index(op.f("ix_interactions_reel_id"), "interactions", ["reel_id"], unique=False)
    op.create_index(op.f("ix_interactions_user_id"), "interactions", ["user_id"], unique=False)

    for table_name, user_col, target_col, unique_name in [
        ("likes", "user_id", "reel_id", "uq_like_user_reel"),
        ("bookmarks", "user_id", "reel_id", "uq_bookmark_user_reel"),
        ("follows", "follower_id", "following_id", "uq_follow_pair"),
        ("blocks", "blocker_id", "blocked_id", "uq_block_pair"),
    ]:
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column(user_col, sa.String(), nullable=False),
            sa.Column(target_col, sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(user_col, target_col, name=unique_name),
        )
        op.create_index(op.f(f"ix_{table_name}_{user_col}"), table_name, [user_col], unique=False)
        op.create_index(op.f(f"ix_{table_name}_{target_col}"), table_name, [target_col], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("reel_id", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["reel_id"], ["reels.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_created_at"), "comments", ["created_at"], unique=False)
    op.create_index(op.f("ix_comments_reel_id"), "comments", ["reel_id"], unique=False)
    op.create_index(op.f("ix_comments_user_id"), "comments", ["user_id"], unique=False)

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reporter_id", sa.String(), nullable=False),
        sa.Column("reel_id", sa.String(), nullable=True),
        sa.Column("target_user_id", sa.String(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reports_reel_id"), "reports", ["reel_id"], unique=False)
    op.create_index(op.f("ix_reports_reporter_id"), "reports", ["reporter_id"], unique=False)
    op.create_index(op.f("ix_reports_target_user_id"), "reports", ["target_user_id"], unique=False)


def downgrade() -> None:
    for table_name in [
        "reports",
        "comments",
        "blocks",
        "follows",
        "bookmarks",
        "likes",
        "interactions",
        "reels",
        "users",
    ]:
        op.drop_table(table_name)
