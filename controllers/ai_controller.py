from views.view_ai_models import AIWindow
from google import genai

import logging
logger = logging.getLogger(__name__)

class AIController():

    def __init__(self):
        self.ai_window = None
        self.view = None
        self.allowed_models = None
        self.image_import_model = 'gemini-2.5-flash' # default
        self.get_ai_models()

    def set_view(self, view):
        self.view = view

    def open_ai_window(self):
        if not self.allowed_models:
            self.get_ai_models()
        if self.ai_window == None or not self.ai_window.winfo_exists():
            self.ai_window = AIWindow(self, self.allowed_models, self.image_import_model)
            self.ai_window.attributes('-topmost', True)
            self.ai_window.focus()
        else:
            self.ai_window.focus()

    def get_ai_models(self):
        client = genai.Client()
        model_list = client.models.list()
        supported_models = (model.name for model in model_list if 'generateContent' in model.supported_actions)
        clean_names = (model_name.replace('models/', '') for model_name in supported_models)
        allowed_models = [model_name for model_name in clean_names if 'gemini'  in model_name or model_name == 'gemma-3-27b-it']
        if 'gemma-3-27b-it' in allowed_models:
            allowed_models.remove('gemma-3-27b-it')
            allowed_models.insert(1, 'gemma-3-27b-it') # make gemma the 2nd option in the list

        logger.info(f'available models are: {allowed_models}')
        self.allowed_models = allowed_models

    def set_ai_model(self, model_name):
        self.image_import_model = model_name
        logger.info(f'The AI model for image import has been set to {self.image_import_model}')

    def get_image_import_model(self) -> str:
        return self.image_import_model


    