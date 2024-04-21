from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Short, Client


class ClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = Client
        fields = ["username", "email", "rating"]


class ShortSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Short
        fields = ["title", "image", "rating", "created", "client"]


    def to_representation(self, instance):
        res = super().to_representation(instance)
        urlImage = res["image"]
        res["image"] = f"http://127.0.0.1:8000{urlImage}"
        return res
    