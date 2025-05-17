from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat.models import ChatMessage
from llm_instance import fraud_detect_llm  

class FraudDetectionPromptView(APIView):
    def post(self, request):
        question = request.data.get("question")
        chat_id = request.data.get("chat_id")

        if not chat_id or not question:
            return Response({"error": "Missing 'chat_id' or 'question'"}, status=status.HTTP_400_BAD_REQUEST)

        llm = fraud_detect_llm()
        answer = llm.invoke(question) 
        ChatMessage.objects.create(
            chat_id=chat_id,
            question=question,
            answer=answer
        )

        return Response({"answer": answer}, status=status.HTTP_200_OK)
