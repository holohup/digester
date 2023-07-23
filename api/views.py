from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from news.models import Digest, User
from api.serializers import DigestSerializer
from django.shortcuts import get_object_or_404
from api.utils import fill_digest
from datetime import datetime
from api.tasks import parse_news


@api_view(('GET',))
def generate_digest(request, pk):
    reader = get_object_or_404(User, pk=pk)
    new_digest = Digest.objects.create(reader=reader)
    result = parse_news(
        [source.parser_class for source in reader.subscription_sources],
        reader.latest_article_parsed
    )
    return Response({
        'message': f'Digest creation has started. Digest id = {new_digest.pk}'
    })


class DigestViewSet(ReadOnlyModelViewSet):
    queryset = Digest.objects.prefetch_related('posts')
    serializer_class = DigestSerializer
