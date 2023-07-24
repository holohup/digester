from datetime import datetime
from importlib import import_module

from celery import shared_task
from celery.signals import task_success
from django.db import transaction
from rest_framework.reverse import reverse

from api.helpers import SourceInfo
from api.producer import publish_to_rabbitmq
from api.utils import fill_digest
from news.models import Post, Tag


@shared_task
def parse_news(sources: list, last_timestamp: datetime, new_digest_id: int):
    """Parses news using the class names from sources."""

    sources_to_parse = [SourceInfo(*src) for src in sources]
    module = import_module('api.parsers')
    result = {}
    for s in sources_to_parse:
        c = getattr(module, s.parser_class)
        parser = c(last_timestamp)
        parser.parse()
        r = parser.result
        if r:
            result.update({s.source_id: r})
    if result:
        return result, new_digest_id
    return None, new_digest_id


def create_posts_with_tags(source_id, posts):
    """Serializers dictionaries to posts."""

    with transaction.atomic():
        for post in posts:
            post_tags = post.pop('tags')
            tags = [
                Tag.objects.get_or_create(name=post_tag.lower())[0]
                for post_tag in post_tags
            ]
            new_post = Post.objects.create(
                **post,
                source_id=source_id,
            )
            new_post.tags.set(tags)


@task_success.connect(sender=parse_news)
def finish_digest_creation(sender, result, **kwargs):
    """Finishes the job creating posts, the digest and sending the message."""

    res, new_digest_id = result
    if not res:
        publish_to_rabbitmq(
            'no new posts in your subscriptions', 'sad but true'
        )
        return
    for source_id, posts in res.items():
        create_posts_with_tags(source_id, posts)
    fill_digest(new_digest_id)
    digest_url = reverse('digests-detail', kwargs={'pk': new_digest_id})
    publish_to_rabbitmq('digest creation complete', f'welcome to {digest_url}')
