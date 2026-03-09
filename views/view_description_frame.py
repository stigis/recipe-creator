'''
    A frame containing the Description section of a recipe
'''

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import constants
import utils

class DescriptionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='Ingredient.TFrame')
        self.pack(padx=10, pady=10, fill='x')
        # header
        #self.description_header = ttk.Label(self, text='Description', font = constants.HEADER_2_FONT, background= constants.Color.LIGHT_SAND.value)
        self.description_header = ctk.CTkLabel(self, text='Description', **constants.CTK_SECTION_LABEL_STYLES)
        self.description_header.pack(side='top', padx=10, pady=20)

        # description text
        self.description_text = utils.AutoSizingTextbox(self, 53)
        self.description_text.configure(font= constants.CTK_SMALL_FONT, fg_color = constants.Color.LIGHT_GRAYISH_BLUE.value, border_width = 3)
        #self.description_text = ctk.CTkTextbox(self, wrap='word', height=50, font = constants.CTK_SMALL_FONT, fg_color= constants.Color.LIGHT_GRAYISH_BLUE.value, activate_scrollbars=False, border_width=3)
        self.description_text.pack(padx=10, pady=20, fill='x')
    
    def get_description(self):
        return self.description_text.get('1.0', 'end-1c')
    
    def set_description(self, new_description):
        self.description_text.delete('1.0', 'end')
        self.description_text.insert('end', new_description)