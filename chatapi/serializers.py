from .models import Message,ChatThread
from rest_framework.serializers import ModelSerializer

class MessageSerializer(ModelSerializer):
    class Meta:
        fields = ["role", "content"]
        model = Message


class ChatThreadSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ChatThread
