from views.view_api_key import APIKeyWindow
from tkinter import messagebox
from google import genai
from google.genai import errors

import socket
import os
import keyring
import time
import threading
import logging
logger = logging.getLogger(__name__)

APP_NAME = "RecipeBuilder_v1"
USERNAME = "default_user"

class APIKeyController:

    def __init__(self):
        self.view = None
        self.api_window = None
    
    # separated from the constructor so it can be called after the view has been created
    def set_view(self, view):
        self.view = view

    def check_api_key(self):
        key = self.get_api_key()
        if not key:
            logger.warning('No API Key found!')
            # disable buttons that use API
            # self.disable_ai()
            msg = '''
            No API Key was found. An API key is required to access AI features.
            Would you like to add one now? You can add API Keys and learn more about them in the menu
            '''
            add_key = messagebox.askyesno(icon='warning', title='No API Key', message= msg)
            if add_key:
                self.open_view()
            else:
                return
        
        elif key:
            logger.info('Found an API key. Loading it into an environment variable')
            os.environ['GEMINI_API_KEY'] = key
            logger.info('testing API Key...')
            self.test_api_key()
        # The test runs in a background thread
        # results of the test and the follow up actions are implemented in a callback
        

    def disable_ai(self):
        self.view.disable_ai()

    def enable_ai(self):
        self.view.enable_ai()

    # open a view window for setting and testing the API key
    # called from the menu
    def open_view(self):
        if self.api_window == None or not self.api_window.winfo_exists():
            self.api_window = APIKeyWindow(self)
            self.api_window.attributes('-topmost', True)
            self.api_window.focus()
        else:
            self.api_window.focus()
        
    def get_help(self):
        print('user asked for help with api keys')
    
    def set_api_key(self, value):
        print('clicked Set api key button')
        keyring.set_password(APP_NAME, USERNAME, value)
        logger.info('set API Key using keyring')
        logger.info('setting api key environment variable')
        os.environ['GEMINI_API_KEY'] = value
        logger.info('set key environment variable')

    def get_api_key(self):
        return keyring.get_password(APP_NAME, USERNAME)
    
    def has_api_key(self):
        return keyring.get_password(APP_NAME, USERNAME) != None
    
    def test_api_key(self, from_button=False):
        #print('clicked test api key button')
        thread = threading.Thread(target=self.key_test, args=(from_button,), daemon=True)
        thread.start()


    # run in a background thread!
    def key_test(self, from_button=False):
        test_client = genai.Client()
        backoff = 2
        num_attempts = 3
        logger.info('starting api key test')
        for attempt in range(num_attempts):
            try:
                models = test_client.models.list()
                logger.info(f'available models are {models}')
                logger.info('API Key is valid')
                self.view.after(0, lambda: self.on_finish_test(passed=True, from_button= from_button))
                test_client.close()
                return True
            except (errors.ClientError, errors.ServerError) as e:
                error_msg = str(e)
                if '400' in error_msg or '401' in error_msg or '403' in error_msg or 'unauthenticated' in error_msg or 'not valid' in error_msg:
                    logger.error(e)
                    logger.error('API Key is Present but not valid. Please check/reset credentials')
                    self.view.after(0, lambda: self.on_finish_test(passed=False, failed_auth=True, from_button = from_button))
                    test_client.close()
                    return False
            except Exception as e:
                error_msg = str(e)
                logger.warning(f'API connection failed for non-auth reasons: {error_msg}')
                logger.warning(f'retries left: {num_attempts - attempt - 1}')
                time.sleep(backoff) # only safe to do in a background thread
                backoff = backoff ** 2 # exponential backoff
        
        test_client.close()
        logger.warning(f'No successful response after {num_attempts} attempts')
        self.view.after(0, lambda: self.on_finish_test(passed=False, failed_auth=False, from_button= from_button))
        return False
    
    def on_finish_test(self, passed: bool, failed_auth:bool = False, from_button=False):
        if not passed and failed_auth:
            #self.disable_ai()
            if not from_button:
                add_key = messagebox.askyesno(title='API Key Invalid', message="The API key was not valid, would you like to open the API Key Menu?")
                if add_key:
                    self.open_view()
        
        if from_button:
            self.api_window.update_with_test_result(passed, failed_auth)






    