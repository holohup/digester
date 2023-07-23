from abc import ABC, abstractmethod, abstractproperty
import feedparser
import httpx
from datetime import datetime
from typing import NamedTuple
from bs4 import BeautifulSoup


class Article(NamedTuple):
    link: str
    published: datetime
    text: str
    title: str
    tag: str


class Parser(ABC):
    time_format = '%a, %d %b %Y %H:%M:%S %z'

    def __init__(self, latest_timestamp) -> None:
        self._timestamp = latest_timestamp
        self._client = httpx.Client()
        super().__init__()

    def parse(self):
        response = self._client.get(self._rss_url)
        parsed_response = feedparser.parse(response)['entries']
        new_news = [
            n
            for n in parsed_response
            if datetime.strptime(n['published'], self.time_format)
            > self._timestamp
        ]
        articles = self._get_news(new_news)

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
                published=datetime.strptime(n['published'], self.time_format),
                text=n['summary'],
                title=n['title'],
                tag=n['tags'][0]['term']
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
                published=datetime.strptime(n['published'], self.time_format),
                text=n['rbc_news_anons'],
                title=n['title'],
                tag=n['tags'][0]['term']
            )
            for n in news
        ]
        return result

    @property
    def _rss_url(self):
        return 'https://rssexport.rbc.ru/rbcnews/news/20/full.rss'


class IXBTParser(Parser):
    """IXBT Parser class.
    The feed does not provide tags, therefore the only tag is 'ixbt'.
    """

    def _get_news(self, news):
        result = [
            Article(
                link=n['link'],
                published=datetime.strptime(n['published'], self.time_format),
                text=self._clean_text(n['summary']),
                title=n['title'],
                tag='ixbt'
            )
            for n in news
        ]
        return result

    @property
    def _rss_url(self):
        return 'https://www.ixbt.com/export/news.rss'

    def _clean_text(self, html_text):
        soup = BeautifulSoup(html_text, 'lxml')
        clean_text = soup.get_text()
        clean_text = ' '.join(clean_text.split())
        return clean_text
