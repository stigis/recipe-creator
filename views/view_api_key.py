import customtkinter as ctk
import utils
import os
import logging
logger = logging.getLogger(__name__)

class APIKeyWindow(ctk.CTkToplevel):
    def __init__(self, api_key_controller):
        super().__init__()
        self.api_key_controller = api_key_controller

        self.title('Set API Keys')
        # center window
        utils.center_toplevel(toplevel= self, width=400, height=200)
        api_key = os.getenv('GEMINI_API_KEY')
        self.has_api_key = api_key != None
        message = ''
        if api_key:
            message = 'You have an API Key set'
        else:
            message = 'You have not set an API Key'
        logger.debug(f'toplevel width is {self.winfo_width()}')
        window_width = 400
        self.header = ctk.CTkLabel(self, text=message, width= window_width - 10, wraplength= window_width - 10)
        self.entry_frame = ctk.CTkFrame(self)
        self.key_entry = ctk.CTkEntry(self.entry_frame, show='*', placeholder_text='Enter your API Key from Google AI Studio')
        self.is_key_visible = ctk.BooleanVar()
        self.checkbox = ctk.CTkCheckBox(self.entry_frame, text='Show Key', variable=self.is_key_visible, command= self.toggle_key_visible, checkbox_width=18, checkbox_height=18)
        self.button_frame = ctk.CTkFrame(self)
        self.set_button = ctk.CTkButton(self.button_frame, text='Set API Key', command= self.set_api_key)
        self.test_button = ctk.CTkButton(self.button_frame, text='Test API Key', command= self.test_api_key)

        if not self.has_api_key:
            self.test_button.configure(state='disabled')

        self.header.pack(padx=10, pady=20, fill='x', expand=False)
        self.entry_frame.pack(fill='x', padx=5)
        self.key_entry.pack(side='left', padx=10, pady=10, fill='x', expand=True)
        self.checkbox.pack(side='right')
        self.button_frame.pack(padx=10, pady=10, fill='x')
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.set_button.grid(padx=10, pady=10, row=0, column=0)
        self.test_button.grid(padx=10, pady=10, row=0, column=1)
    
    def toggle_key_visible(self):
        if self.is_key_visible.get():
            self.key_entry.configure(show='')
        else:
            self.key_entry.configure(show='*')

    def set_api_key(self):
        value = self.key_entry.get().strip()
        if not value:
            return
        self.set_button.configure(state='disabled')
        self.test_button.configure(state='disabled')
        try:
            self.api_key_controller.set_api_key(value)
            self.header.configure(text='You set an API key. Testing the key...')
            self.has_api_key = True
            self.api_key_controller.test_api_key(from_button=True) # buttons are re-enabled in a callback
            
        except Exception as e:
            logger.error(f'Could not set the API Key: {str(e)}')
            self.header.configure(text='Error setting API key')
            self.set_button.configure(state='normal')
            self.test_button.configure(state= 'normal' if self.has_api_key else 'disabled')

    
    def test_api_key(self):
        self.header.configure(text='Testing API Key...')
        self.test_button.configure(state='disabled')
        self.set_button.configure(state='disabled')
        self.api_key_controller.test_api_key(from_button=True) # buttons are re-enabled in a callback
    
    def update_with_test_result(self, passed, failed_auth):
        if passed:
            self.header.configure(text='Your API Key is working properly')
        elif not passed and not failed_auth:
            self.header.configure(text=f'The API key test was not successful, but it may be due to connection reasons. If you retry it, it might be successful. Check your internet connection')
        else:
            self.header.configure(text='The API Key was not valid')

        self.set_button.configure(state='normal') # re-enable the buttons in the callback
        self.test_button.configure(state='normal')

        
    

