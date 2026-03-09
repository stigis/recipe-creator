'''
Docstring for img_recipe_extractor.gui.v3.view_chat_window
Chat window with a gemma model for generating an recipe to import
'''
import tkinter as tk
import customtkinter as ctk
import constants
import threading
import time
import queue
from recipe_chat import RecipeChat
from enum import Enum

class Side(Enum):
    SENT = 0
    RECEIVED = 1

class ChatWindow(ctk.CTkToplevel):
    def __init__(self, controller, *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)

        self.title('Recipe Chat')
        #self.geometry("400x400+400+150")
        self.controller = controller
        self.thread_queue = queue.Queue()
        #self.configure(fg_color = constants.Color.CREAM.value)

        # center the new window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_width = screen_width // 2
        center_height = screen_height // 2
        width = 400
        height = 400
        x_offset = center_width - width // 2
        y_offset = center_height - height // 2
        self.geometry(f'{width}x{height}+{x_offset}+{y_offset}')


        self.message_container = ctk.CTkScrollableFrame(self)
        self.textbox = ctk.CTkTextbox(self, font= constants.CTK_SMALL_FONT, height=70)
        self.chat_btn = ctk.CTkButton(self, text='Send', command= self.on_send_clicked)
        self.textbox.bind('<Return>', lambda e: self.on_enter_pressed(event=e))

        self.message_container.pack(fill='both', expand=True)
        self.message_container.bind('<Configure>', self.on_resize, add='+')
        
        self.botton_panel = ctk.CTkFrame(self)
        self.import_btn = ctk.CTkButton(self.botton_panel, text='Import Recipe', command= self.on_import_clicked)
        self.show_btn = ctk.CTkButton(self.botton_panel, text='Show Current Recipe', command= self.on_show_clicked)
        self.reset_btn = ctk.CTkButton(self.botton_panel, text='Reset Info')
        self.botton_panel.pack(side='bottom', fill='y', padx=10, pady=10)
        self.import_btn.pack(side='left', padx=20, pady=10, anchor='center')
        self.show_btn.pack(side='left', padx=20, pady=10, anchor='center')
        self.reset_btn.pack(side='left', padx=20, pady=10, anchor='center')

        self.textbox.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        self.chat_btn.pack(side='left', padx=10, pady=10)
        self.latest_response = None

        #self.add_message_to_display('Starting AI Chat...')
        self.chatbot = RecipeChat()
        self.full_send(message= self.chatbot.intro_prompt, init_response_text='Starting AI Chat, Please wait...')
        self._prev_width = self.message_container.cget('width')
        print(f'prev width is {self._prev_width}')

        self.textbox.focus()

    def add_message_to_display(self, message, side):
        # adds a chat message to the display. But does not actually send a message behind the scenes
        # When adding a message that is 'received', a slight delay is added before the message becomes visible
        fg_color = "#1f6aa5" if side == Side.SENT else "#3d3d3d"
        bubble = ctk.CTkFrame(self.message_container, fg_color= fg_color, corner_radius=15)
        if side == Side.RECEIVED:
            bubble.pack(padx=(10, 60), pady=20, anchor='w')
        else:
            bubble.pack(padx=(60, 10), pady=20, anchor='e')
        message_width = int(self.winfo_width() * 0.6)
        label = ctk.CTkLabel(bubble, text=message, text_color='white', wraplength= message_width, font= constants.CTK_SMALL_FONT)

        if side == Side.RECEIVED:
            self.latest_response = label
            self.after(500, self.make_message_visible, label)
        else:
            self.make_message_visible(label)

    def make_message_visible(self, label):
        label.pack(padx=10, pady=5)
        self.message_container.update_idletasks()
        self.message_container._parent_canvas.yview_moveto(1.0)



    def send_message(self, text):
        self.add_message_to_display(text, Side.SENT)

    def on_send_clicked(self):
        message_text = self.textbox.get('1.0', 'end-1c')
        if message_text:
            self.textbox.delete('1.0', 'end')
            self.full_send(message= message_text, show_sending=True)

    def on_import_clicked(self):
        self.full_send(message='[GENERATE_RECIPE_JSON]', init_response_text='Generating import data...', callback = self.listen_for_import)
        #self.add_message_to_display(message='Importing current recipe...', side='received')

    def on_show_clicked(self):
        self.full_send(message='[SHOW_CURRENT_RECIPE]', init_response_text='Generating Current Recipe...')
    
    def listen_for_result(self):
        # If the queue has an item (a response from the API), process it
        # If the queue is empty, raises an exception, and schedules this polling function again 
        try:
            result = self.thread_queue.get(block= False) 
            # modify widgets
            if self.latest_response:
                self.latest_response.configure(text= result)
            self.enable_buttons()
        except queue.Empty:
            self.after(100, self.listen_for_result)

    def listen_for_import(self):
        try:
            recipe_json_str = self.thread_queue.get(block= False)
            # controller import
            self.controller.import_ai_recipe(recipe_json_str)
            if self.latest_response:
                self.latest_response.configure(text='Import completed. Check the regular application window for results')
            self.enable_buttons()
        except queue.Empty:
            self.after(100, self.listen_for_import)



    def on_enter_pressed(self, event):
        # tkinter events have a bitmask to indicate if certain keys are pressed at the tim of event firing
        # the first bit indicates if 'Shift' was pressed, so we can compare it using a bitmask of 1
        is_shift_pressed = event.state & 0x0001
        if is_shift_pressed:
            return # do nothing, treat like a regular press of 'Enter'
        else: 
            self.on_send_clicked()
            return 'break' # stop normal processing, do not create a newline from the 'Enter' keypress
    
    def send_to_model(self, message, queue: queue.Queue):
        # This function must be called in a separate thread
        print(f'inside thread, message is {message}')
        print('sending message to model')
        response = self.chatbot.send_message(message)
        print(response.text)
        #time.sleep(5)
        print('received response')
        # When the model responds, place the response on the queue
        print('finishing thread')
        queue.put(response.text)

    def full_send(self, message, init_response_text='Generating response...', show_sending=False, callback=None):
        if callback == None:
            callback = self.listen_for_result

        self.disable_buttons()
        if show_sending:
            self.add_message_to_display(message= message, side= Side.SENT)
        self.add_message_to_display(message= init_response_text, side= Side.RECEIVED)
        thread = threading.Thread(target=self.send_to_model, daemon=True, kwargs={"message": message, "queue": self.thread_queue})
        thread.start()
        self.after(100, callback)

    def on_resize(self, event):
        print(event)
        print(event.widget)
        if event.widget != self.message_container:
            print(' not the message container, returning')
            return
        changed_size = self._prev_width != event.width
        if changed_size:
            self._prev_width = event.width
            new_message_width = int(event.width * 0.6)
            children = self.message_container.winfo_children()
            print('children:')
            for child in children: # BFS
                #print(child)
                if isinstance(child, ctk.CTkLabel):
                    print(child)
                    child.configure(wraplength = new_message_width)
                children.extend(child.winfo_children())
        print('Did the window change size? ', 'Yes' if changed_size else 'No')
        
        #print(f'children are:\n{event.widget.winfo_children()}')
        '''
        children = self.message_container.winfo_children()
        print('children:')
        for child in children: # BFS
            #print(child)
            if isinstance(child, ctk.CTkLabel):
                print(child)
                #child.configure(wraplength = message_width)
            children.extend(child.winfo_children())
        '''
        
    def disable_buttons(self):
        buttons = {self.import_btn, self.show_btn, self.reset_btn, self.chat_btn}
        for button in buttons:
            button.configure(state='disabled')

    def enable_buttons(self):
        buttons = {self.import_btn, self.show_btn, self.reset_btn, self.chat_btn}
        for button in buttons:
            button.configure(state='normal')


            


