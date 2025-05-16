from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from llm_instance import use_case_llm 

class UseCaseScenarioPromptView(APIView):
    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "Missing 'question'"}, status=status.HTTP_400_BAD_REQUEST)
        llm = use_case_llm()
        answer = llm.invoke(question) 
        return Response({"answer": answer}, status=status.HTTP_200_OK)
