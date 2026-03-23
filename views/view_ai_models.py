import customtkinter as ctk
import webbrowser
import utils


class AIWindow(ctk.CTkToplevel):

    info_text_1 = '''Choose an AI model to use for converting images into recipes'''
    info_text_2 = '''The Gemini models are more accurate, but have limits on how many times they can be used each day.

The Gemma model has very high daily limits so it's a good fallback option, but it's not as accurate when converting images to recipes.'''

    
    def __init__(self, ai_controller, ai_models, current_model):
        super().__init__()
        self.ai_controller = ai_controller
        self.ai_models = ai_models

        self.title('AI Model')
        utils.center_toplevel(self, width=500, height=300)

        self.choose_label = ctk.CTkLabel(self, text= self.info_text_1)
        self.info_label = ctk.CTkLabel(self, text=self.info_text_2, wraplength=400, justify='left')
        self.choose_label.pack(pady = 10)
        self.model_options = ctk.CTkOptionMenu(self, values=self.ai_models, command= self.on_ai_chosen)
        self.model_options.set(current_model)
        self.model_options.pack(pady=20)
        self.info_label.pack(padx = 10, pady = 10)
        self.limits_info = ctk.CTkTextbox(self, width= 420, height=70, wrap='word')


        self.limits_info.tag_config('link', foreground='#1f538d', underline=True)
        self.limits_info.insert('end', 'Click Here', 'link')
        self.limits_info.insert('end', ' to view the limits for different AI models. The Requests Per Day limit is under the RPD column. Click the "All Models" button to view details for all models')
        
        self.limits_info.tag_bind('link', '<Enter>', lambda e: self.limits_info.configure(cursor='hand2'))
        self.limits_info.tag_bind('link', '<Leave>', lambda e: self.limits_info.configure(cursor='xterm'))
        self.limits_info.tag_bind('link', '<Button-1>', self.open_rate_limits)

        self.limits_info.configure(state='disabled')
        self.limits_info.pack(padx=10, pady=10)

    def on_ai_chosen(self, choice):
        self.ai_controller.set_ai_model(choice)

    def open_rate_limits(self, event=None):
        webbrowser.open_new_tab('https://aistudio.google.com/rate-limit?timeRange=last-28-days')
