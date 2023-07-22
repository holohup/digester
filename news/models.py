from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Subscription(models.Model):
    source_name = models.CharField('Source name', max_length=100)
    subscribers = models.ManyToManyField(
        User,
        verbose_name='Subscribers to the source',
        related_name='subscriptions',
    )


class Post(models.Model):
    popularity = models.IntegerField('Post popularity')
    created_at = models.DateTimeField(
        'Creation time', default=timezone.now, db_index=True
    )
    text = models.TextField('Post text', blank=False)


class Digest(models.Model):
    reader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='digests',
        verbose_name='Digest',
    )
    posts = models.ManyToManyField(
        Post,
        verbose_name='Posts included in the digest',
        related_name='digests',
    )
