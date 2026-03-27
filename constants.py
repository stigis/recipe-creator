'''
Docstring for img_recipe_extractor.gui.v3.constants
'''

from enum import Enum
import customtkinter as ctk

APP_NAME = 'RecipeViewer'

class Color(Enum):
    BEIGE = '#F5F5DC'
    CREAM = '#FFFDD0'
    SOFT_SAGE = '#E2EAD3'
    MUTED_SAGE = '#D1D7BE'
    LIGHT_SAND = '#F7F1E3'
    LIGHT_GRAYISH_BLUE = '#CAD9E0'
    READING_GRAY_BG = '#2F2F2F'
    READING_GRAY_TEXT = '#E0E0E0'
    FERN_GREEN = '#4F7942'

    #CAD9E0 soft blue-gray
    #D1D7BE muted sage
'''
    Store fonts as tuples. The format is (<family>, <size>, <styling (bold, italic, ....)>)
    Use tuples instead of Font objects, because Font objects require a TK() instance to exist
    before they cann be created, and this adds unnecessary complexity
'''
HEADER_1_FONT = ('Terminal', 24
                 )
HEADER_2_FONT = ('Terminal', 20 )
SMALL_FONT = ('Serif', 12)
CTK_SMALL_FONT = ('Serif', 16)
LIST_MARKER_FONT = ('Serif', 24)
CTK_LIST_MARKER_FONT = ('Serif', 30)
CTK_ORDERED_LIST_MARKER_FONT = ('Serif', 24)
ORDERED_LIST_MARKER_FONT = ('Serif', 16)
BUTTON_FONT = ('Serif', 16, 'bold')
CTK_BUTTON_FONT = ('Serif', 24, 'bold')

CTK_SECTION_LABEL_STYLES = {
    'padx': 50,
    'pady': 10,
    'fg_color': Color.LIGHT_SAND.value,
    'font': ('Terminal', 22)
}

CTK_SECTION_SUBFRAME = {
    'fg_color': Color.CREAM.value
}

#minus_b = ctk.CTkButton(sub_frame, text='x', width=35, font= self.button_font, border_width=2, anchor='center')
ADD_REMOVE_BUTTON = {
    'width': 35,
    'font': CTK_BUTTON_FONT,
    'border_width': 2,
    'anchor': 'center',
    'text_color': '#000000',
}

CTK_REMOVE_BUTTON = {
    **ADD_REMOVE_BUTTON,
    'text': 'x',
    'fg_color': '#C24343'
}

CTK_ADD_BUTTON = {
    **ADD_REMOVE_BUTTON,
    'text': '+',
    'fg_color': '#20B972'
}

def init_fonts():
    global BUTTON_FONT
    BUTTON_FONT = ctk.CTkFont(*BUTTON_FONT)






