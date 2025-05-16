from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.model import RAGModel

class StandardsEnhacementsPromptView(APIView):
    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "Missing 'question'"}, status=status.HTTP_400_BAD_REQUEST)

        llm = RAGModel()
        answer = llm.answer(question, topic="standards_enhancements")

        return Response({"answer": answer}, status=status.HTTP_200_OK)
