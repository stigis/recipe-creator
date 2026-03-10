'''
    util functions
'''

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import logging
logger = logging.getLogger(__name__)

'''
    A CTK textbox that automatically grows and shrinks in size as new characters are typed in.
    Resizing is triggered automatically via the <KeyRelease> event, but it can also be done manually
    by calling self.update_height()

    @author Shalom
'''
class AutoSizingTextbox(ctk.CTkTextbox):
    #def __init__(self, master, width = 200, height = 200, corner_radius = None, border_width = None, border_spacing = 3, bg_color = "transparent", fg_color = None, border_color = None, text_color = None, scrollbar_button_color = None, scrollbar_button_hover_color = None, font = None, activate_scrollbars = True, **kwargs):
    #    super().__init__(master, width, height, corner_radius, border_width, border_spacing, bg_color, fg_color, border_color, text_color, scrollbar_button_color, scrollbar_button_hover_color, font, activate_scrollbars, **kwargs)
    def __init__(self, parent, min_height, extra_height=20):
        super().__init__(parent, activate_scrollbars=False, wrap='word', height=min_height)
        self.bind('<KeyRelease>', lambda event: self._update_height(event))
        self.min_height = min_height
        self.extra_height = extra_height

    def _update_height(self, event):
        logger.debug(f'event: {event}')
        text_pixel_height = self._textbox.count('1.0', 'end', 'ypixels')
        scaling = ctk.ScalingTracker.get_widget_scaling(self._textbox)
        logger.debug(f'text pixel height is: {text_pixel_height}, scaling is: {scaling}')
        if isinstance(text_pixel_height, tuple):
            text_pixel_height = text_pixel_height[0] # if it's a tuple, take the 1st value
        '''
            Since text_pixel_height is scaled by ctk, but min_height and extra_height are not,
            and a descaled value is needed for configure(), remove the scaling from text_pixel_height
        '''
        unscaled_height = text_pixel_height // scaling
        new_height = max(self.min_height, unscaled_height + self.extra_height)
        self.configure(height = new_height)
        
        


