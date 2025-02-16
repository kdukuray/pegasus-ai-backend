from django.db import models

class ChatThread(models.Model):
    name = models.CharField(max_length=100, default="random")


class Message(models.Model):
    role = models.CharField(max_length=100)
    content = models.TextField()
    associated_thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)