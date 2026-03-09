'''
Docstring for img_recipe_extractor.gui.v3.view_ctk_scrollable_frame

Creates a scrollable frame as a parent for all other widgets
'''

import tkinter as tk
import customtkinter as ctk
import constants

class ScrollableFrame(ctk.CTkScrollableFrame):
    #def __init__(self, master, width = 200, height = 200, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = None, border_color = None, scrollbar_fg_color = None, scrollbar_button_color = None, scrollbar_button_hover_color = None, label_fg_color = None, label_text_color = None, label_text = "", label_font = None, label_anchor = "center", orientation = "vertical"):
    #    super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, scrollbar_fg_color, scrollbar_button_color, scrollbar_button_hover_color, label_fg_color, label_text_color, label_text, label_font, label_anchor, orientation)
    def __init__(self, parent):
        super().__init__(parent, fg_color= constants.Color.BEIGE.value)
        self.pack(side='top', fill='both', expand=True)