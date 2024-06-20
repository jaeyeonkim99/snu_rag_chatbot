import requests
from django.conf import settings
from django.http import JsonResponse

COLAB_URL = "https://119d-34-44-144-14.ngrok-free.app"
headers = {"Content-Type": "application/json; chartset=utf-8"}


# Create your views here.
def rag_chat(request):
    if request.method == "GET":
        rag_search = settings.RAG_SEARCH_INSTANCE
        query = request.GET.get("query")
        print(f"Query recevied: {query}")
        rag_result = rag_search.rag_search(query)
        response = {"rules": rag_result[1]}
        prompt = rag_result[0]
        colab_uri = COLAB_URL + "/llm_inference"
        llm_response = requests.post(
            colab_uri, json={"prompt": prompt}, headers=headers
        )
        response_data = llm_response.json()
        response["answer"] = response_data["answer"].strip()

        return JsonResponse(response)

    return JsonResponse({"message": "Only GET method is allowed"}, status=405)
