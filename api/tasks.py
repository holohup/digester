from celery import shared_task
from datetime import datetime
from importlib import import_module
from api.producer import publish_to_rabbitmq
from celery.signals import task_success
from django.db import transaction
from api.helpers import SourceInfo
from news.models import Source, Post, Tag


@shared_task
def parse_news(sources: list, last_timestamp: datetime):
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
        return result
    return None


def create_posts_with_tags(source_id, posts):
    with transaction.atomic():
        for post in posts:
            post_tags = post.pop('tags')
            tags = [
                Tag.objects.get_or_create(name=post_tag)[0]
                for post_tag in post_tags
            ]
            # tag, _ = Tag.objects.get_or_create(name=post_tag)
            new_post = Post.objects.create(
                **post,
                source_id=source_id,
            )
            new_post.tags.set(tags)


@task_success.connect(sender=parse_news)
def finish_digest_creation(sender, result, **kwargs):
    if not result:
        publish_to_rabbitmq(
            'no new posts in your subscriptions', 'sad but true'
        )
        return
    for source_id, posts in result.items():
        create_posts_with_tags(source_id, posts)
    publish_to_rabbitmq('digest creation complete', 'ready to roll')
