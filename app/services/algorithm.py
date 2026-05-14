from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.domain import Interaction, Reel
import random
from typing import List

def get_for_you_feed(db: Session, user_id: str) -> List[Reel]:
    # 1. Fetch user's interactions
    interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
    
    # 2. Calculate hashtag frequencies and weight interactions
    hashtag_scores = {}
    for inter in interactions:
        weight = 1
        if inter.interaction_type == 'like':
            weight = 5
        elif inter.interaction_type == 'share':
            weight = 10
        elif inter.interaction_type == 'view_time' and inter.view_time_ms:
            # 1 point per second of view time, max 10 points
            weight = min(inter.view_time_ms // 1000, 10)
            
        if inter.hashtags_involved:
            for tag in inter.hashtags_involved:
                hashtag_scores[tag] = hashtag_scores.get(tag, 0) + weight

    # Extract the top 5 most engaged hashtags
    top_hashtags = sorted(hashtag_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    top_tags = [tag for tag, score in top_hashtags]
    
    # 3. Fetch 15 related reels matching these exact hashtags
    related_reels = []
    if top_tags:
        # Fetching recent reels to filter matches
        recent_reels = db.query(Reel).order_by(Reel.created_at.desc()).limit(200).all()
        scored_reels = []
        for r in recent_reels:
            if not r.hashtags: continue
            overlap = set(r.hashtags).intersection(set(top_tags))
            if overlap:
                scored_reels.append(r)
        
        random.shuffle(scored_reels)
        related_reels = scored_reels[:15]
    
    # 4. Fetch 5 random/trending reels outside their filter bubble
    related_ids = [r.id for r in related_reels]
    random_reels = db.query(Reel).filter(
        ~Reel.id.in_(related_ids) if related_ids else True
    ).order_by(func.random()).limit(5).all()
    
    # 5. Assemble and shuffle the final feed
    feed = related_reels + random_reels
    random.shuffle(feed)
    return feed
