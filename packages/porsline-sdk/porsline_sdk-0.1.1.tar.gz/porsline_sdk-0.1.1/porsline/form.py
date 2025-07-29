import requests
from .jalali_to_gregorian import jconvert

class Form:
    BASE_URL = "https://survey.porsline.ir"

    def __init__(self, form_id: int, name: str, api_key: str):
        self.id = form_id
        self.name = name
        self.api_key = api_key
        self.headers = {
            "Authorization": f"API-Key {api_key}",
            "Content-Type": "application/json"
        }
        self._cols = None

    @property
    def cols(self):
        if self._cols is None:
            response = requests.get(f"{self.BASE_URL}/api/v2/surveys/{self.id}/", headers=self.headers)
            response.raise_for_status()
            all_questions = response.json().get("questions", [])
            questions = []
            for q in all_questions:
                questions.append({
                    "id": q["id"],
                    "text": q["title"],
                    "type": q["type"],
                    "options": [{"id": ch["id"], "name": ch["name"]} for ch in q.get("choices", [])]
                })
            self._cols = questions
        return self._cols

    def responses(self, timestamp: str = None):
        url = f"{self.BASE_URL}/api/v2/surveys/{self.id}/responses/results-table/"
        if timestamp:
            url += f"?since={timestamp}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return [{"response": item["data"][2:-2], "submitted_at": jconvert(item["data"][-1])} for item in response.json()["body"]]
