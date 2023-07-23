from news.models import Digest, Post
from django.db.models import Avg
from datetime import datetime

# fill_digest(new_digest)


def fill_digest(digest: Digest) -> None:
    user = digest.reader
    previous_digest = Digest.objects.filter(reader=user).last()
    if previous_digest:
        previous_digest_creation_time = previous_digest.created_at
    else:
        previous_digest_creation_time = datetime(1, 1, 1, 0, 0, 0)
    avg_popularity = Post.objects.aggregate(avg_popularity=Avg(
        'popularity'
    ))['avg_popularity']

    filtered_posts = Post.objects.filter(
        source__subscriptions__subscribers=user,
        tags__interested_users=user,
        popularity__gt=avg_popularity,
        created_at__gt=previous_digest_creation_time
    )
    digest.posts.set(filtered_posts)
