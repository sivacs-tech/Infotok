import random
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.domain import Block, Follow, Interaction, Like, Reel


def _blocked_author_ids(db: Session, user_id: str) -> list[str]:
    return [
        block.blocked_id
        for block in db.query(Block).filter(Block.blocker_id == user_id).all()
    ]


def _base_visible_reels(db: Session, user_id: str):
    query = db.query(Reel).filter(Reel.is_deleted == False)  # noqa: E712
    blocked_ids = _blocked_author_ids(db, user_id)
    if blocked_ids:
        query = query.filter(~Reel.author_id.in_(blocked_ids))
    return query


def get_for_you_feed(
    db: Session,
    user_id: str,
    page: int = 1,
    page_size: int = 20,
) -> List[Reel]:
    interactions = (
        db.query(Interaction).filter(Interaction.user_id == user_id).limit(500).all()
    )

    hashtag_scores: dict[str, int] = {}
    for interaction in interactions:
        weight = 1
        if interaction.interaction_type == "like":
            weight = 5
        elif interaction.interaction_type == "comment":
            weight = 7
        elif interaction.interaction_type == "share":
            weight = 10
        elif interaction.interaction_type == "view_time" and interaction.view_time_ms:
            weight = min(interaction.view_time_ms // 1000, 10)

        for tag in interaction.hashtags_involved or []:
            hashtag_scores[tag] = hashtag_scores.get(tag, 0) + weight

    top_tags = [
        tag
        for tag, _score in sorted(
            hashtag_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:6]
    ]

    offset = max(page - 1, 0) * page_size
    recent_reels = (
        _base_visible_reels(db, user_id)
        .order_by(Reel.created_at.desc())
        .offset(offset)
        .limit(200)
        .all()
    )

    if not recent_reels:
        return []

    scored: list[tuple[int, Reel]] = []
    following_ids = {
        follow.following_id
        for follow in db.query(Follow).filter(Follow.follower_id == user_id).all()
    }
    seen_reel_ids = {
        interaction.reel_id
        for interaction in interactions
        if interaction.interaction_type in {"like", "comment", "view_time"}
    }

    for reel in recent_reels:
        score = 1
        tags = set(reel.hashtags or [])
        score += len(tags.intersection(top_tags)) * 8
        if reel.author_id in following_ids:
            score += 5
        if reel.id in seen_reel_ids:
            score -= 3
        score += db.query(Like).filter(Like.reel_id == reel.id).count() * 2
        scored.append((score, reel))

    scored.sort(key=lambda item: item[0], reverse=True)
    top_slice = [reel for _score, reel in scored[: page_size * 2]]
    random.shuffle(top_slice)
    return top_slice[:page_size]


def get_trending_reels(db: Session, page: int = 1, page_size: int = 20) -> List[Reel]:
    offset = max(page - 1, 0) * page_size
    return (
        db.query(Reel)
        .outerjoin(Like, Like.reel_id == Reel.id)
        .filter(Reel.is_deleted == False)  # noqa: E712
        .group_by(Reel.id)
        .order_by(func.count(Like.id).desc(), Reel.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
