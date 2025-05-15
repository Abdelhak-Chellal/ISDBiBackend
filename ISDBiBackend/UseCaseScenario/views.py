from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ISDBiBackend.utils.model import LLMHandler

class UseCaseScenarioPromptView(APIView):
    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "Missing 'question'"}, status=status.HTTP_400_BAD_REQUEST)

        llm = LLMHandler()
        answer = llm.answer(question, topic="use_case_scenario")

        return Response({"answer": answer}, status=status.HTTP_200_OK)
