from abc import ABC, abstractmethod, abstractproperty
import feedparser
import httpx
from datetime import datetime, timedelta, timezone
from typing import NamedTuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Article(NamedTuple):
    link: str
    created_at: datetime
    text: str
    title: str
    tag: str


class Parser(ABC):
    time_format = '%a, %d %b %Y %H:%M:%S %z'

    def __init__(self, latest_timestamp) -> None:
        self._timestamp = latest_timestamp
        self._client = httpx.Client()
        self._results = None
        super().__init__()

    def parse(self):
        response = self._download_data(self._rss_url)
        parsed_response = feedparser.parse(response)['entries']
        new_news = [
            n
            for n in parsed_response
            if datetime.strptime(n['published'], self.time_format)
            > self._timestamp
        ]
        articles = self._get_news(new_news)
        if articles:
            self._results = [article._asdict() for article in articles]
            self._parse_popularity()

    def _parse_popularity(self):
        max_rating = 0
        for result in self._results:
            page = self._download_data(result['link'])
            seconds_from_publish = (
                datetime.now(timezone.utc) - result['created_at']
            ).total_seconds()
            absolute_rating = self._get_rating(page) / seconds_from_publish
            if absolute_rating > max_rating:
                max_rating = absolute_rating
            result.update({'absolute rating': absolute_rating})
        if max_rating == 0:
            return
        for result in self._results:
            result.update(
                {
                    'popularity': int(
                        100 * result['absolute rating'] / max_rating
                    )
                }
            )
            result.pop('absolute rating')

    def _download_data(self, url):
        return self._client.get(url)

    # @abstractmethod
    def _get_rating(self, page):
        return 5

    @property
    def result(self):
        return self._results

    @abstractmethod
    def _get_news(self):
        pass

    @abstractproperty
    def _rss_url(self):
        pass


class LentaParser(Parser):
    """Lenta RSS parser."""

    def _get_news(self, news):
        result = [
            Article(
                link=n['link'],
                created_at=datetime.strptime(n['published'], self.time_format),
                text=n['summary'],
                title=n['title'],
                tag=n['tags'][0]['term'],
            )
            for n in news
        ]
        return result

    @property
    def _rss_url(self):
        return 'https://lenta.ru/rss/last24'


class RBCParser(Parser):
    """RBC RSS parser."""

    def _get_news(self, news):
        result = [
            Article(
                link=n['link'],
                created_at=datetime.strptime(n['published'], self.time_format),
                text=n['rbc_news_anons'],
                title=n['title'],
                tag=n['tags'][0]['term'],
            )
            for n in news
        ]
        return result

    @property
    def _rss_url(self):
        return 'https://rssexport.rbc.ru/rbcnews/news/20/full.rss'


class IXBTParser:
    """IXBT Parser class."""

    time_format = '%a, %d %b %Y %H:%M:%S %z'

    def __init__(self, latest_timestamp) -> None:
        self._timestamp = latest_timestamp
        self._client = httpx.Client()
        self._results = []
        self._rss_results = None
        self._html_results = None

    def parse(self):
        self._parse_rss()
        if self._rss_results:
            self._parse_html()
            self._merge_results()
            self._normalize_popularity()

    def _merge_results(self):
        self._results = [
            article
            | {
                'tags': self._html_results[article['link']][1],
                'absolute rating': self._html_results[article['link']][0],
            }
            for article in self._rss_results
        ]

    def _parse_rss(self):
        response = self._download_data(self._rss_url)
        parsed_response = feedparser.parse(response)['entries']
        new_news = [
            n
            for n in parsed_response
            if datetime.strptime(n['published'], self.time_format)
            > self._timestamp
        ]
        articles = self._get_news(new_news)
        if articles:
            self._rss_results = articles

    def _parse_html(self):
        response = self._download_data(self._html_url).text
        soup = BeautifulSoup(response, 'html.parser')
        parts = soup.find_all('div', class_='item')
        entities = {}
        for part in parts:
            link_element = part.find('h2', class_='no-margin').find('a')
            relative_link = link_element['href']
            absolute_link = urljoin(self._html_url, relative_link)
            try:
                comments_element = part.find('a', class_='comments_link')
                num_comments = int(
                    comments_element.find('span', class_='b-num').text
                )
            except AttributeError:
                num_comments = 0
            tags_element = part.find('p', class_='b-article__tags__list')
            tags = [tag.text for tag in tags_element.find_all('a')]
            entities.update({absolute_link: (num_comments, tags)})
        self._html_results = entities

    def _normalize_popularity(self):
        max_rating = 0
        for result in self._results:
            seconds_from_publish = (
                datetime.now(timezone.utc) - result['created_at']
            ).total_seconds()
            absolute_rating = result['absolute rating'] / seconds_from_publish
            if absolute_rating > max_rating:
                max_rating = absolute_rating
            result['absolute rating'] = absolute_rating
        if max_rating == 0:
            return
        for result in self._results:
            result.update(
                {
                    'popularity': int(
                        100 * result.pop('absolute rating') / max_rating
                    )
                }
            )

    def _download_data(self, url):
        return self._client.get(url)

    @property
    def result(self):
        return self._results

    def _get_news(self, news):
        result = [
            dict(
                link=n['link'],
                created_at=datetime.strptime(n['published'], self.time_format),
                text=self._clean_text(n['summary']),
                title=n['title'],
            )
            for n in news
        ]
        return result

    @property
    def _rss_url(self):
        return 'https://www.ixbt.com/export/news.rss'

    @property
    def _html_url(self):
        return 'https://www.ixbt.com/news/?show=tape'

    def _clean_text(self, html_text):
        soup = BeautifulSoup(html_text, 'lxml')
        clean_text = soup.get_text()
        clean_text = ' '.join(clean_text.split())
        return clean_text
