from rest_framework import status
from rest_framework.reverse import reverse
from news.models import Digest, User
import pytest


def test_api_is_available(client):
    assert client.get(reverse('api-root')).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_generate_digest_is_unavailable_with_nonexisting_user_id(client):
    last_user = User.objects.last()
    last_id = 0 if not last_user else last_user.pk
    url = reverse('generate_digest', kwargs={'pk': last_id + 1})
    assert client.get(url).status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_new_digest_starts_being_generated_after_request(client):
    last_digest = Digest.objects.last()
    digests_amount = Digest.objects.count()
    last_id = 0 if not last_digest else last_digest.pk
    user = User.objects.create()
    url = reverse('generate_digest', kwargs={'pk': user.pk})
    r = client.get(url)
    assert r.status_code == status.HTTP_200_OK
    assert (
        r.data['message']
        == f'Digest creation has started. Digest id = {last_id + 1}'
    )
    assert Digest.objects.count() == digests_amount + 1
