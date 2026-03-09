'''
Docstring for img_recipe_extractor.gui.v3.view

Creates a Tkinter GUI for viewing and editing JSON files containing a recipe
'''

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
from views.view_menu import MenuBar
from views.view_scrollable_frame import ScrollableFrameContainer
from views.view_header_frame import HeaderFrame
from views.view_ingredients_frame import IngredientsFrame
from views.view_directions_frame import DirectionsFrame
from views.view_description_frame import DescriptionFrame
from views.view_ctk_scrollable_frame import ScrollableFrame
from views.view_chat_window import ChatWindow
from views.view_waiting_popup import WaitingPopup
import constants
import platform # used to determine OS
import logging
logger = logging.getLogger(__name__)

class View(ctk.CTk):
    
    #def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title('Recipe Viewer')
        self.geometry('500x500+300-150')
        self.chat_window = None
        #ctk.deactivate_automatic_dpi_awareness() # used for other ctk windows that are created
        logger.info('the platform is: ', platform.system())
        if platform.system() == 'Windows':
            self.after(0, lambda: self.state('zoomed'))
        elif platform.system == 'Linux':
            self.after(0, lambda: self.attributes('-zoomed', True))
        else:
            self.after(0, lambda: self.state('zoomed')) # fallback for MacOs or others

        self._make_menu_bar()
        self._make_menu_bindings()

        self._make_scrollable_frame()
        # the rest of the widgets will go inside the parent frame/canvas/scrollable window
        # UPDATE: scrollable frame is now donnen using CustomTkinter
        self._make_header_frame()
        self._make_ingredients_frame()
        self._make_directions_frame()
        self._make_description_frame()

        self._make_status_bar()

        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def _make_menu_bar(self):
        self.option_add('*tearOff', False)
        self.menu_bar = MenuBar(self, self.controller, self._get_window_scaling())
        self.config(menu= self.menu_bar)

    def _make_menu_bindings(self):
        self.bind('<Control-o>', lambda event: self.controller.open_file())
        self.bind('<Control-s>', lambda event: self.controller.save(event))
        self.bind('<Control-i>', lambda event: self.controller.import_picture(event))

    def _make_scrollable_frame(self):
        #self.scrollable_frame_container = ScrollableFrameContainer(self)
        #self.scrollable_frame = self.scrollable_frame_container.scrollable_frame
        self.scrollable_frame = ScrollableFrame(self)

    def _make_header_frame(self):
        self.header_frame = HeaderFrame(self.scrollable_frame) #tk.Frame(self.scrollable_frame, width=300, bg='green')

    def _make_ingredients_frame(self):
        self.ingredients_frame = IngredientsFrame(self.scrollable_frame)

    def _make_directions_frame(self):
        self.directions_frame = DirectionsFrame(self.scrollable_frame)

    def _make_description_frame(self):
        self.description_frame = DescriptionFrame(self.scrollable_frame)

    def _make_footer_frame(self):
        self.footer_frame = None
    
    def _make_status_bar(self):
        # status bar at bottom
        self.status_bar = ctk.CTkLabel(self, text='Ready   ', anchor='e')
        self.status_bar.pack(fill='x', side='right', ipady=5)

        self.mode_status_label = ctk.CTkLabel(self, text='Mode: ', anchor='e')
        self.mode_status_label.pack(fill='x', side='left', ipady=5, ipadx=5)
        self.mode_status = ctk.CTkLabel(self, textvariable=self.menu_bar.get_mode(), anchor='e')
        self.mode_status.pack(fill='x', side='left', ipady=5)

    def show_url_input_box(self) -> str:
        #ctk.deactivate_automatic_dpi_awareness()
        #ctk.set_widget_scaling(1.0) 
        #ctk.set_window_scaling(1.0)
        dialog = ctk.CTkInputDialog(text='Provide a website url that contains a recipe', title='Import from Website')
        url = dialog.get_input()
        #self.attributes('-alpha', 1.0) # force the root back to opaque
        print('url is: ', url)
        return url
    
    def switch_to_view(self):
        print('in switch_to_view()')
        # disable entry labels in header
        self.header_frame.disable()
        # disable entry labels and remove buttons in ingredients 
        self.ingredients_frame.disable_ingredients()

        # disable textboxes and remove buttons in Directions
        self.directions_frame.disable_directions()

        # disable textbox in Description
        self.description_frame.description_text.configure(state='disabled')

    def switch_to_edit(self):
        self.header_frame.enable()
        self.ingredients_frame.enable_ingredients()
        self.directions_frame.enable_directions()
        self.description_frame.description_text.configure(state='normal')

    def init_recents_list(self, recents_list):
        self.menu_bar.init_recents_list(recents_list)

    def add_recent_file(self, file, max_recents):
        self.menu_bar.add_recent(file, max_recents)

    def on_close(self):
        are_snapshots_identical = self.controller.compare_to_snapshot()
        if are_snapshots_identical:
            self.destroy()
        else:
            response = messagebox.askyesnocancel(title='Quit', message='Would you like to save your changes before quitting?')
            if response == True:
                saved = self.controller.save()
                if saved:
                    self.destroy()
            elif response == False:
                self.destroy()
            # else if cancel is clicked, do nothing
    
    def show_error(self, error_message, msg_title=''):
        messagebox.showerror(title= msg_title, message=error_message)

    def open_chat(self):
        
        if self.chat_window is None or not self.chat_window.winfo_exists():
            self.chat_window = ChatWindow(controller= self.controller)
            self.chat_window.focus()
        else:
            self.chat_window.focus()

    def make_popup(self, label_msg):
        self.popup = WaitingPopup(message= label_msg)

    def update_popup_status(self, message):
        self.popup.update_wait_label(message)

    def finish_popup_progress(self):
        self.popup.finish_progress()


    def main(self):
        print('in main of view')
        self.mainloop()
