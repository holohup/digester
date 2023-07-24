from news.models import Digest, Post
from django.db.models import Avg
from datetime import datetime


def fill_digest(digest_id: int) -> None:
    digest = Digest.objects.get(id=digest_id)
    user = digest.reader
    qs = Digest.objects.all()
    if len(qs) > 1:
        previous_digest_creation_time = (
            Digest.objects.filter(reader=user).order_by('-pk')[1].created_at
        )
    else:
        previous_digest_creation_time = datetime(1, 1, 1, 0, 0, 0)
    avg_popularity = Post.objects.aggregate(avg_popularity=Avg('popularity'))[
        'avg_popularity'
    ]
    filtered_posts = Post.objects.filter(
        source__subscriptions__subscriber=user,
        tags__interested_users=user,
        popularity__gt=avg_popularity,
        created_at__gt=previous_digest_creation_time,
    )
    digest.posts.set(filtered_posts)
