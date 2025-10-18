"""add_performance_indexes

Revision ID: d6bc2fd0fc19
Revises: f15a527e3486
Create Date: 2025-10-18 08:49:31.025891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6bc2fd0fc19'
down_revision: Union[str, Sequence[str], None] = 'f15a527e3486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for faster queries."""
    
    # RestaurantCache table indexes
    op.create_index('ix_restaurant_cache_location_code', 'restaurant_cache', ['location_code'])
    op.create_index('ix_restaurant_cache_rating', 'restaurant_cache', ['rating'])
    op.create_index('ix_restaurant_cache_review_count', 'restaurant_cache', ['review_count'])
    
    # Reviews table indexes
    op.create_index('ix_reviews_yelp_id', 'reviews', ['yelp_id'])
    op.create_index('ix_reviews_user_id', 'reviews', ['user_id'])
    
    # User Restaurant Flags table indexes
    op.create_index('ix_user_restaurant_flags_yelp_id', 'user_restaurant_flags', ['yelp_id'])

def downgrade() -> None:
    """Remove performance indexes."""
    
    # Drop indexes in reverse order
    op.drop_index('ix_user_restaurant_flags_yelp_id', 'user_restaurant_flags')
    op.drop_index('ix_reviews_user_id', 'reviews')
    op.drop_index('ix_reviews_yelp_id', 'reviews')
    op.drop_index('ix_restaurant_cache_review_count', 'restaurant_cache')
    op.drop_index('ix_restaurant_cache_rating', 'restaurant_cache')
    op.drop_index('ix_restaurant_cache_location_code', 'restaurant_cache')