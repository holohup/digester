from datetime import datetime
import zoneinfo
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from news.models import Digest, User
from api.serializers import DigestSerializer
from django.shortcuts import get_object_or_404
from api.tasks import parse_news
from api.helpers import SourceInfo

MOSCOW_ZONE = zoneinfo.ZoneInfo('Europe/Moscow')


@api_view(('GET',))
def generate_digest(request, pk):
    reader = get_object_or_404(User, pk=pk)
    new_digest = Digest.objects.create(reader=reader)
    sources_to_parse = [
        SourceInfo(source.parser_class, source.pk)
        for source in reader.subscription_sources
    ]
    new_digest_id = new_digest.id
    parse_news.delay(
        sources_to_parse,
        reader.latest_article_parsed or datetime(1, 1, 1, tzinfo=MOSCOW_ZONE),
        new_digest_id
    )
    return Response(
        {
            'message': 'Digest creation has started. '
            f'Digest id = {new_digest_id}'
        }
    )


class DigestViewSet(ReadOnlyModelViewSet):
    queryset = Digest.objects.prefetch_related('posts')
    serializer_class = DigestSerializer
