import tkinter as tk
import customtkinter as ctk
import threading
import logging
logger = logging.getLogger(__name__)

class WaitingPopup(ctk.CTkToplevel):
    def __init__(self, message, operation = None): #*args, fg_color = None, **kwargs):
        super().__init__()
        width = 300
        height = 250
        self.title('Performing Operation...')
        self.attributes("-topmost", True)
        self.message = message
        self.operation = operation

        # center the popup
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        logger.debug(f'screen width: {screen_width}px, sscreen height: {screen_height}px')
        center_width = screen_width // 2
        center_height = screen_height // 2
        x_offset = center_width - width // 2
        y_offset = center_height - height // 2
        self.geometry(f"{width}x{height}+{x_offset}+{y_offset}")
        logger.debug(f'width: {width}, height: {height}, x_offset: {x_offset}, y_offset: {y_offset}')

        self.grab_set() # makes it modal

        self.label = ctk.CTkLabel(self, text= self.message)
        self.label.pack(padx=10, pady=20)
        self.wait_label = ctk.CTkLabel(self, text= 'Please Wait...')
        self.wait_label.pack(padx=10, pady=20)

        self.progress_bar = ctk.CTkProgressBar(self, mode='indeterminate')
        self.progress_bar.pack(padx=10, pady=20)
        self.progress_bar.start()

    def update_wait_label(self, message):
        self.wait_label.configure(text= message)

    def finish_progress(self):
        self.progress_bar.stop()
        self.progress_bar.set(1)

    def run_operation(self):
        thread = threading.Thread(target= self.operation, daemon=True)
        thread.start()
        self.check_thread(thread)

    def check_thread(self, thread):
        if self.thread.is_alive():
            self.after(100, lambda: self.check_thread(thread))
        else:
            self.wait_label.destroy()
            self.label.configure(text='Done')

    
