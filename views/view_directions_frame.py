'''
Docstring for img_recipe_extractor.gui.v3.view_directions_frame

Frame that contains the Directions header and the list of directions for the recipe
'''

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import constants
import utils

class DirectionsFrame(ctk.CTkFrame):

    #def __init__(self, master = None, *, border = ..., borderwidth = ..., class_ = "", cursor = "", height = 0, name = ..., padding = ..., relief = ..., style = "", takefocus = "", width = 0):
    #    super().__init__(master, border=border, borderwidth=borderwidth, class_=class_, cursor=cursor, height=height, name=name, padding=padding, relief=relief, style=style, takefocus=takefocus, width=width)
    # The parent is the scrollable frame
    def __init__(self, parent):
        super().__init__(parent, fg_color=constants.Color.BEIGE.value, border_width=1)
        self.pack(padx=10, pady=10, fill='x')
        self.button_font = ctk.CTkFont(*constants.CTK_BUTTON_FONT)

        style = ttk.Style()
        style.configure('OrderedBullet.TLabel', background = constants.Color.CREAM.value, font = constants.ORDERED_LIST_MARKER_FONT)

        # header
        #self.directions_header = ttk.Label(self, text='Directions', font= constants.HEADER_2_FONT, background= constants.Color.LIGHT_SAND.value)
        self.directions_header = ctk.CTkLabel(self, text='Directions', **constants.CTK_SECTION_LABEL_STYLES)
        self.directions_header.pack(side='top', padx=10, pady=10)

        self._make_directions_container()

    def _make_directions_container(self):
        #self.directions_container = ttk.Frame(self, style='Container.Ingredient.TFrame')
        self.directions_container = ctk.CTkFrame(self, **constants.CTK_SECTION_SUBFRAME)
        self.directions_container.pack(padx=10, pady=20, fill='x')
        self.direction_list = []
        for i in range(3):
            self._add_direction(index=i, content= f'Step #{i}')

    def _on_remove_button_clicked(self, object1):
        print('remove button clicked')
        print('Deleteing item...')
        size = len(self.direction_list)
        if size <= 1:
            print("can't remove last item")
            return
        index = object1['index']
        object1['sub_frame'].destroy()
        self.direction_list.remove(object1)
        self._update_indexes(index)

    def _on_insert_button_clicked(self, object1):
        print(f'insert button clicked for {object1}')
        new_index = object1['index'] + 1
        print(f'children are...')
        print(object1['sub_frame'].winfo_children()[0])
        self._add_direction(index=new_index, insert_after=object1)
        self._update_indexes(new_index + 1)

    def _add_direction(self, index, insert_after=None, content='Step'):
        prev_frame = None
        if insert_after:
            prev_frame = insert_after['sub_frame']
        #sub_frame = ttk.Frame(self.directions_container, style='Ingredient.TFrame')
        sub_frame = ctk.CTkFrame(self.directions_container, **constants.CTK_SECTION_SUBFRAME)
        sub_frame.pack(side='top', padx=10, pady=10, fill='x', after = prev_frame) # must fill x so that the grid inside can expand
        sub_frame.grid_columnconfigure(0, weight=1)
        sub_frame.grid_columnconfigure(1, weight=19)
        #d_label = ttk.Label(sub_frame, text=f'{index + 1}.', style='OrderedBullet.TLabel')
        d_label = ctk.CTkLabel(sub_frame, text=f'{index + 1}.', font= constants.CTK_ORDERED_LIST_MARKER_FONT)
        d_label.grid(row=0, column=0, sticky='e', padx=10)
        direction = utils.AutoSizingTextbox(sub_frame, 53)
        direction.configure(font = constants.CTK_SMALL_FONT, fg_color = constants.Color.MUTED_SAGE.value, border_width = 1)
        direction.insert('end', content)
        direction.grid(row=0, column=1, sticky='ew', pady=10)
        
        #minus_b = ttk.Button(sub_frame, text='x', width=2, style='Remove.TButton')
        minus_b = ctk.CTkButton(sub_frame, **constants.CTK_REMOVE_BUTTON)
        plus_b = ctk.CTkButton(sub_frame, **constants.CTK_ADD_BUTTON)
        #plus_b = ttk.Button(sub_frame, text='+', width=2, style='Add.TButton')

        minus_b.grid(row=0, column=2, padx=10, pady=5)
        plus_b.grid(row=0, column=3, padx=(0, 10), pady=5)

        record = {
            'sub_frame': sub_frame,
            'index': index,
            'direction': direction
        }
        if insert_after:
            self.direction_list.insert(index, record)
        else:  
            self.direction_list.append(record)
        minus_b.configure(command= lambda step=record: self._on_remove_button_clicked(step))
        plus_b.configure(command= lambda step=record: self._on_insert_button_clicked(step))

    '''
        Called when a direction is inserted or removed.
        Updates the visual and internal records of direction indexes to match the 
        new indexes that have changed due to insertion or deletion
    '''
    def _update_indexes(self, starting_index):
        end = len(self.direction_list)
        print(end)
        for i in range(starting_index, end):
            record = self.direction_list[i]
            record['index'] = i
            index_label: ttk.Label = record['sub_frame'].winfo_children()[0]
            index_label.configure(text = f'{i + 1}.')
    
    def get_directions(self):
        directions = []
        for record in self.direction_list:
            direction_text = record['direction'].get('1.0', 'end-1c')
            directions.append(direction_text)
        return directions
    
    def set_directions(self, new_directions):
        for sub_frame in self.directions_container.winfo_children():
            sub_frame.destroy()
        self.direction_list.clear()

        for i, step in enumerate(new_directions):
            self._add_direction(index= i, content= step)

    def disable_directions(self):
        for record in self.direction_list:
            direction: utils.AutoSizingTextbox = record['direction']
            direction.configure(state='disabled')
            sub_frame = record['sub_frame']
            for widget in sub_frame.winfo_children():
                if isinstance(widget, (tk.Button, ttk.Button, ctk.CTkButton)):
                    widget.grid_remove()

    def enable_directions(self):
        for record in self.direction_list:
            direction: utils.AutoSizingTextbox = record['direction']
            direction.configure(state='normal')
            sub_frame = record['sub_frame']
            for widget in sub_frame.winfo_children():
                if isinstance(widget, (tk.Button, ttk.Button, ctk.CTkButton)):
                    widget.grid()






  
        


    def _tkr(self, event):
        #print(self.tb.count("1.0", tk.END, "displaylines"))
        #self.tb.search
        f = self.tb.cget('font')
        print(f.metrics('linespace'))
        print(f.metrics('descent'))
        print(f._family)
        print(f._size)
        print('border width is: ', self.tb.cget('border_width'))
        print('border spacing is: ', self.tb.cget('border_spacing'))
        print(f'highlight thickness is: {self.tb._textbox.cget("highlightthickness")}')
        print(f'internal pady is: {self.tb._textbox.cget("pady")}')
        print(self.tb._w)
        num_lines = self.tb._textbox.count('1.0', 'end', 'update', 'displaylines')
        print('numlines is: ', num_lines)
        print('_textbox height is: ', self.tb._textbox.cget('height'))
        print('ctextbox height is: ', self.tb.cget('height'))
        cuurent_height = self.tb._textbox.cget('height')
        if cuurent_height <= num_lines + 1:
            self.tb._textbox.configure(height= num_lines + 1)
        elif cuurent_height > num_lines + 1:
            self.tb._textbox.configure(height= num_lines + 1)

        #self.tb._textbox.configure(height= num_lines + 1)

        #print(dir(f))
        '''
        self.tb = ctk.CTkTextbox(self.directions_container, font= ctk.CTkFont(family='Serif', size=12))
        tb_font = self.tb.cget('font')
        line_height = tb_font.metrics('linespace')
        three_lines = 3 * line_height
        print(f'three lines is {three_lines} pixels')
        print(f'border spacing is: {self.tb.cget("border_spacing")}')
        self.tb.configure(height= 1)
        self.tb._textbox.configure(height=2)
        self.tb.update_idletasks()
        self.tb.pack(side='top', padx=10, pady=20, fill='x')
        self.tb.bind('<KeyRelease>', self._tkr)
        print(f'height is {self.tb.cget("height")}')
        '''

