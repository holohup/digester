# import pytest
# from news.models import Tag, Source, User, Subscription, Post, Digest


# @pytest.fixture
# def tags():
#     return [Tag.objects.create(name=name) for name in ('1', '2', '3')]


# @pytest.fixture
# def sources():
#     return [
#         Source.objects.create(title=title, url=url)
#         for title, url in (
#             ('Lenta', 'http://lenta.ru'),
#             ('RBC', 'http://rbc.ru'),
#         )
#     ]


# @pytest.fixture
# def user(tags):
#     u = User.objects.create()
#     return u


# @pytest.fixture
# def subscription(user):
#     s = Subscription.objects.create()
#     return s



# @pytest.fixture
# def posts(sources):
#     p1 = Post.objects.create(popularity=50, source=sources[0])
#     p2 = Post.objects.create(popularity=60, source=sources[1])
#     return p1, p2
