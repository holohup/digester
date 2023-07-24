from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class Tag(models.Model):
    name = models.CharField('Tag', max_length=100)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """Custom User model."""

    interests = models.ManyToManyField(
        Tag, verbose_name='Interests', related_name='interested_users'
    )

    @property
    def latest_article_parsed(self):
        qs = Post.objects.filter(source__in=self.subscription_sources)
        return qs.aggregate(max_timestamp=models.Max('created_at'))[
            'max_timestamp'
        ]

    @property
    def subscription_sources(self):
        return Source.objects.filter(
            pk__in=self.subscriptions.values_list('source__pk', flat=True)
        )


class Source(models.Model):
    title = models.CharField('News Site Title', max_length=100)
    url = models.URLField('News site URL')
    parser_class = models.CharField(
        'Parser class for the source', max_length=100
    )

    def __str__(self) -> str:
        return self.title


class Subscription(models.Model):
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        verbose_name='News source',
        related_name='subscriptions',
    )
    subscriber = models.ForeignKey(
        User,
        verbose_name='Subscriber to the source',
        related_name='subscriptions',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.subscriber} subscription on {self.source}'

    class Meta:
        unique_together = ('source', 'subscriber',)


class Post(models.Model):
    title = models.CharField('Title', max_length=100)
    popularity = models.IntegerField('Post popularity', default=50)
    created_at = models.DateTimeField(
        'Creation time', default=timezone.now, db_index=True
    )
    text = models.TextField('Post text', blank=False)
    link = models.URLField('Post URL')
    tags = models.ManyToManyField(
        Tag, related_name='posts', verbose_name='Tags'
    )
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        verbose_name='Post source',
        related_name='posts',
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ('-created_at',)


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
    created_at = models.DateTimeField(
        'Creation time', default=timezone.now, db_index=True
    )

    def __str__(self) -> str:
        c_time = self.created_at.strftime('%d-%m-%y, %H:%M:%S')
        return f'Digest for {self.reader} created at {c_time}'
