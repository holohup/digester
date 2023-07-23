from rest_framework import serializers
from news.models import Digest, Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('text', 'link')


class DigestSerializer(serializers.ModelSerializer):
    posts = PostSerializer(read_only=True, many=True)

    class Meta:
        model = Digest
        fields = ('id', 'posts', 'created_at')
