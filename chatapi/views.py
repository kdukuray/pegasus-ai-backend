from django.shortcuts import render
from rest_framework.decorators import api_view
import ollama
from django.http.response import StreamingHttpResponse
from rest_framework import status
from typing import List, Dict
from . import models
from . import serializers
from rest_framework.response import Response

def get_streaming_response(all_messages: List[Dict]):
    api_response = ollama.chat(
        model="llama3.2:1b",
        messages=all_messages,
        stream=True
    )
    for chunk in api_response:
        if chunk:
            yield chunk.message.content


@api_view(['POST'])
def chat_api(request):
    print(request.data)
    # Chang this later, for now we can jus experiment with using the 1 and only chat thread
    chat_thread_id = int(request.data.get('chatThreadId', 1))
    if chat_thread_id == -1:
        new_thread = models.ChatThread()
        new_thread.save()
        chat_thread_id = new_thread.pk
    else:
        chat_thread_id = models.ChatThread.objects.get(pk=chat_thread_id)

    # Get all the 
    all_messages = models.Message.objects.filter(associated_thread=chat_thread_id)
    all_messages_serialized  = serializers.MessageSerializer(all_messages, many=True).data
    all_messages_list = [{"role": message.get("role"), "content": message.get("content")} for message in all_messages_serialized]
    new_user_message_as_dict = {"role": "user", "content": request.data.get('messageContent', "---1MessageError1---")}

    if new_user_message_as_dict["content"] == "---1MessageError1---":
        return Response({}, status=status.HTTP_400_BAD_REQUEST)



    # Normally, this is where we would use the id to get new messages from the database
    all_messages_list.append(new_user_message_as_dict)


    ai_response_chunk_list = []

    def stream_and_capture_ai_response(all_messages_list_: List[Dict]):
        try:
            # print(all_messages_list_)
            for ai_response_chunk in get_streaming_response(all_messages_list_):
                if ai_response_chunk:
                    ai_response_chunk_list.append(ai_response_chunk)
                    yield ai_response_chunk

        finally:
            # if the AI response is successful, save the user's response to the db as well as the AI
            # response. This is how it is done in chatGPT because they don't want dangling prompts
            new_user_message = models.Message(role="user", content=new_user_message_as_dict["content"],
                                              associated_thread=chat_thread_id)
            new_user_message.save()
            new_ai_message = models.Message(role="assistant", content="".join(ai_response_chunk_list),
                                            associated_thread=chat_thread_id)
            new_ai_message.save()


    return StreamingHttpResponse(stream_and_capture_ai_response(all_messages_list),
                                 status=status.HTTP_200_OK,
                                 content_type="text/plain")


@api_view(['GET'])
def get_chat_thread_messages(request, chat_thread_id):
    chat_thread = models.ChatThread.objects.get(pk=chat_thread_id)
    all_messages = models.Message.objects.filter(associated_thread=chat_thread)
    all_messages_serialized = serializers.MessageSerializer(all_messages, many=True).data
    return Response({"messages": all_messages_serialized}, status=status.HTTP_200_OK)

