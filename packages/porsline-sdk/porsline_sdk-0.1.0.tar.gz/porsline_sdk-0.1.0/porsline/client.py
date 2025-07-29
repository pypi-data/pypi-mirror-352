import requests
from .form import Form

class Porsline:
    BASE_URL = "https://survey.porsline.ir"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"API-Key {api_key}",
            "Content-Type": "application/json"
        }

    def get_forms(self):
        response = requests.get(f"{self.BASE_URL}/api/folders/", headers=self.headers)
        response.raise_for_status()
        forms = []
        for folder in response.json():
            folder_id = folder["id"]
            form_list = requests.get(f"{self.BASE_URL}/api/folders/{folder_id}/", headers=self.headers)
            if form_list.status_code == 200 and "surveys" in form_list.json():
                for survey in form_list.json()["surveys"]:
                    forms.append(Form(survey["id"], survey["name"], self.api_key))
        return forms

    def get_form(self, form_id):
        response = requests.get(f"{self.BASE_URL}/api/v2/surveys/{form_id}/", headers=self.headers)
        response.raise_for_status()
        survey_data = response.json()
        return Form(form_id, survey_data.get("name", "Unnamed Survey"), self.api_key)
