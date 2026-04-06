'''
Docstring for img_recipe_extractor.gui.v3.view_menu

Contains the menu bar gui for the program
'''
import tkinter as tk
import customtkinter as ctk
from tkinter import font
from pathlib import Path

import platform
import subprocess
import os
from platformdirs import PlatformDirs
import constants

import logging
logger = logging.getLogger()

class MenuBar(tk.Menu):
    def __init__(self, parent, controller):
        super().__init__(parent)
        menu_font = font.nametofont('TkMenuFont')
        ctk_window_scaling = ctk.ScalingTracker.get_window_scaling(parent)
        #font_family = menu_font.actual('family')
        font_size = int(11 * ctk_window_scaling)
        menu_font.configure(size= font_size)
        #self.scaled_font = (font_family, font_size)
        parent.option_add('*Menu.Font', menu_font)
        self.controller = controller
        self.api_key_controller = self.controller.api_key_controller
        self.ai_controller = self.controller.ai_controller
        self.mode = tk.StringVar()
        self.mode.set('Edit')
        self.menu_font = menu_font
        self.configure(font= menu_font)

        
        #self.configure(font=self.scaled_font)

        self.file_menu = self._make_file_menu()
        self.mode_menu = self._make_mode_menu()
        self.api_key_menu = self._make_api_key_menu()
        self.ai_menu = self._make_ai_menu()
        

        #self.chat_menu = self._make_chat_menu()
        #font.names
        
        self.add_cascade(label='File', menu= self.file_menu)
        self.add_cascade(label='Mode', menu= self.mode_menu)
        #self.add_cascade(label='Chat', menu=)
        self.add_command(label='Chat', command= self.controller.open_chat)
        self.add_cascade(label='API Key', menu= self.api_key_menu)
        self.add_cascade(label='AI', menu= self.ai_menu)

    def _make_file_menu(self):
        file_menu = tk.Menu(self)
        file_menu.add_command(label='New')
        file_menu.add_command(label='Open', command= self.controller.open_file, accelerator='Ctrl + O')
        file_menu.add_command(label='Open Image Folder', command= self.open_image_file_explorer)
        

        import_menu = tk.Menu(self)
        import_menu.add_command(label='Import from Image', command= self.controller.import_image)
        import_menu.add_command(label='Import from Website', command= self.controller.import_website)

        #file_menu.add_cascade(label='Open Recent', menu=recents_menu)
        #file_menu.add_command(label='Import', accelerator='Ctrl + I', command= self.controller.import_picture)
        file_menu.add_cascade(label='Import', menu = import_menu)
        file_menu.add_command(label='Save', accelerator='Ctrl + S', command= self.controller.save)
        file_menu.add_command(label='Save As', command= self.controller.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command= self.master.quit)
        return file_menu
    
    def _make_mode_menu(self):
        mode_menu = tk.Menu(self)
        mode_menu.add_radiobutton(label='Edit', variable= self.mode, value='Edit', command= self.switch_mode)
        mode_menu.add_radiobutton(label='View', variable= self.mode, value='View', command= self.switch_mode)

        return mode_menu
    
    def _make_chat_menu(self):
        chat_menu =  tk.Menu(self)
        return chat_menu
    
    def _make_api_key_menu(self):
        api_key_menu = tk.Menu(self)
        api_key_menu.add_command(label='Set/Test API Key', command= self.api_key_controller.open_view)
        api_key_menu.add_command(label='Help', command= self.api_key_controller.get_help)
        return api_key_menu
    
    def _make_ai_menu(self):
        ai_menu = tk.Menu(self)
        ai_menu.add_command(label='Set AI Model', command= self.ai_controller.open_ai_window)
        ai_menu.add_command(label='About AI Models')
        return ai_menu
        
    
    # return the stringvar for use elsewhere
    def get_mode(self):
        return self.mode
    
    def switch_mode(self):
        new_mode = self.mode.get()
        logger.info(f'new_mode is: {new_mode}')
        # Expects the parent to be the root view/Frame!
        if new_mode == 'Edit':
            root = self.master
            root.switch_to_edit()
        elif new_mode == 'View':
            root = self.master
            root.switch_to_view()

    def disable_ai_buttons(self):
        self.file_menu.entryconfig('Import', state='disabled')
        self.entryconfig('Chat', state='disabled')

    def enable_ai_buttons(self):
        self.file_menu.entryconfig('Import', state='normal')
        self.entryconfig('Chat', state='normal')

    def init_recents_list(self, recents_list):
        self.recents_menu = tk.Menu(self)
        for file_path in recents_list:
            basename = Path(file_path).name
            display_name = basename.removesuffix('.json')
            self.recents_menu.add_command(label= display_name, command= lambda file=file_path : self.controller.open_file(file_path = file))
        self.file_menu.insert_cascade(index=2, label='Open Recent', menu=self.recents_menu)
        self.recents_menu.deletecommand

    def add_recent(self, file, max_recents):
        basename = Path(file).name
        display_name = basename.removesuffix('.json')

        # check if this file is already in the 'recently opened' list and remove it if it is, so it can be re-added at the top
        last_index = self.recents_menu.index('end')
        for i in range(last_index + 1):
            label = self.recents_menu.entrycget(i, 'label')
            if label == display_name:
                self.recents_menu.delete(i)
                break

        self.recents_menu.insert_command(index=0, label = display_name, command= lambda file=file : self.controller.open_file(file_path = file))
        num_recents = self.recents_menu.index('end') + 1
        logger.debug(f'number of recent files is {num_recents}')
        if num_recents > max_recents:
            self.recents_menu.delete('end')

    def open_image_file_explorer(self):
        app_dir = PlatformDirs(appname=constants.APP_NAME, appauthor=False, ensure_exists=True)
        img_path = app_dir.user_data_path / 'images'
        path_string = str(img_path)
        try:
            if platform.system() == 'Windows':
                os.startfile(path_string)
            elif platform.system() == 'Darwin': # macos
                subprocess.Popen(['open', path_string], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else: # Linux
                subprocess.Popen(['xdg-open', path_string], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f'Failed to open file exlorer on images folder: {e}')

