'''
    The frame that contains the list of ingredients for the recipe

    Structure:
    Ingredients Frame (this is self):
        ingredients header
        ingredients grid container
        TODO use pack instead of grid, to allow for easier insertion and deletion
        use another frame if needed to allow for grid behavior
'''

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import utils
import constants
import logging
logger = logging.getLogger(__name__)

class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None
    
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def __len__(self):
        return self.size

    def append(self, data):
        new_node = Node(data)
        if self.head == None: # first node
            self.head = new_node
            self.tail = new_node
            self.size += 1
            return new_node
        
        self.tail.next = new_node
        new_node.prev = self.tail
        self.tail = new_node
        self.size += 1
        return new_node

    # insert after the given node
    def insert(self, current_node, data):
        new_node = Node(data)
        new_node.prev = current_node
        new_node.next = current_node.next
        current_node.next = new_node
        self.size += 1
        if current_node == self.tail:
            self.tail = new_node
        return new_node

    def remove_node(self, node):
        prev = node.prev
        next = node.next
        if prev:
            prev.next = next
        else: # if there is no previous node, the head is being removed, reset it
            self.head = next
        if next:
            next.prev = prev
        else:
            self.tail = prev
        self.size -= 1

    def as_list(self):
        result_list = []
        current_node = self.head
        while current_node:
            result_list.append(current_node.data)
            current_node = current_node.next
        return result_list


class IngredientsFrame(ctk.CTkFrame):
    
    # The parent is the scrollable frame
    def __init__(self, parent):
        super().__init__(parent, fg_color=constants.Color.BEIGE.value, border_width=1)
        self.pack(padx=10, pady=10, fill='x')
        #self.scrollable_container = scrollable_container
        #self.canvas: tk.Canvas = self.scrollable_container.canvas

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('SectionParent.TFrame',background= constants.Color.BEIGE.value, borderwidth=1, relief='solid')
        style.configure('Ingredient.TFrame', borderwidth=0, relief='solid')
        #style.configure('Container.Ingredient.TFrame', background = constants.Color.BEIGE.value)
        style.configure('Container.Ingredient.TFrame', background = constants.Color.BEIGE.value, borderwidth=0)
        style.configure('Bullet.TLabel', background = constants.Color.CREAM.value, font = constants.LIST_MARKER_FONT)
        style.configure('Ingredient.TEntry', padding=(10, 5), fieldbackground='#CAD9E0')
        style.configure('Remove.TButton', background="#C24343", font= constants.BUTTON_FONT)
        style.configure('Add.TButton', background="#20B972", font = constants.BUTTON_FONT)
        # red C43741
        # green 5D7836
        self.button_font = ctk.CTkFont(*constants.CTK_BUTTON_FONT)
        self.list_marker_font = ctk.CTkFont(*constants.CTK_LIST_MARKER_FONT)

        self._make_ingredients_header()
        self._make_ingredients_container()

    def _make_ingredients_header(self):
        #self.ingredients_header = ttk.Label(self, text='Ingredients', font = constants.HEADER_2_FONT, background = constants.Color.LIGHT_SAND.value, padding=(50, 5))
        self.ingredients_header = ctk.CTkLabel(self, text='Ingredients', **constants.CTK_SECTION_LABEL_STYLES)
        self.ingredients_header.pack(side='top', padx=10, pady=10)

    def _make_ingredients_container(self):
        #self.ingredients_container = ttk.Frame(self, style='Container.Ingredient.TFrame')
        self.ingredients_container = ctk.CTkFrame(self, **constants.CTK_SECTION_SUBFRAME)
        self.ingredients_container.pack(padx=10, pady=20, fill='x')
        #self.ingredient_list = []
        # each node in the list contains a subframe that contains an individual ingredient
        self.linked_list = LinkedList() 
        for i in range(3):
            self._add_ingredient(content = f'Ingredient #{i}')
        '''
        grid container - Frame , gridcolumnconfigure
            ingredient.grid()

        ingredient container - Frame
            sub frame.pack() - Frame, gridcolumnconfiguer
                label.grid(col = 0)
                ingredient.grid(col = 1)

        '''

    def _on_remove_button_clicked(self, node):
        logger.info(f'clicked X button')
        logger.info(f'size is {len(self.linked_list)}, deleting item...')
        size = len(self.linked_list)
        if size <= 1:
            logger.info("can't delete last item")
            return
        
        self.linked_list.remove_node(node)
        node.data['sub_frame'].destroy()
    
    def _on_insert_button_clicked(self, node):
        logger.info('clicked + button')
        self._add_ingredient(insert_after_node = node)

    def _add_ingredient(self, insert_after_node: Node = None, content: str = 'Ingredient'):
        prev_frame = None
        if insert_after_node:
            prev_frame = insert_after_node.data['sub_frame']
        #sub_frame = ttk.Frame(self.ingredients_container, style='Ingredient.TFrame')
        sub_frame = ctk.CTkFrame(self.ingredients_container, **constants.CTK_SECTION_SUBFRAME)
        sub_frame.pack(side='top', padx=10, pady=10, fill='x', after=prev_frame) # must fill x so that the grid inside can expand
        sub_frame.grid_columnconfigure(0, weight=1)
        sub_frame.grid_columnconfigure(1, weight=9)
        #i_label = ttk.Label(sub_frame, text='\u2022', style='Bullet.TLabel')
        i_label = ctk.CTkLabel(sub_frame, text='\u2022', font= self.list_marker_font)
        i_label.grid(row=0, column=0, sticky='e')
        #ingredient = ttk.Entry(sub_frame, font = constants.SMALL_FONT, style='Ingredient.TEntry')
        ingredient = ctk.CTkEntry(sub_frame, font=constants.CTK_SMALL_FONT, fg_color=constants.Color.LIGHT_GRAYISH_BLUE.value)
        ingredient.insert('end', content)
        ingredient.grid(row=0, column=1, sticky='ew', padx=10)
        #minus_b = ttk.Button(sub_frame, text='x', width=2, style='Remove.TButton')
        minus_b = ctk.CTkButton(sub_frame, **constants.CTK_REMOVE_BUTTON)
        plus_b = ctk.CTkButton(sub_frame, **constants.CTK_ADD_BUTTON)
        #plus_b = ttk.Button(sub_frame, text='+', width=2, style='Add.TButton')

        minus_b.grid(row=0, column=2, padx=(0, 10), pady=5)
        plus_b.grid(row=0, column=3, padx=(0, 10), pady=5)

        # create a linked list of the ingredients
        record = {
            'sub_frame': sub_frame,
            'ingredient': ingredient
        }
        if insert_after_node:
            node = self.linked_list.insert(insert_after_node, record)
        else:
            node = self.linked_list.append(record)
        #print(node.data)
        minus_b.configure(command = lambda ingredient_record=node: self._on_remove_button_clicked(ingredient_record))
        plus_b.configure(command= lambda ingredient_record=node: self._on_insert_button_clicked(ingredient_record))

        #self.master.event_generate('<<UpdateCanvasWindow>>')
        #self.on_widget_added()
        #self.master.update()  

    def get_ingredients(self):
        record_list = self.linked_list.as_list()
        ingredient_list = []
        for record in record_list:
            ingredient_text = record['ingredient'].get()
            ingredient_list.append(ingredient_text)
        
        return ingredient_list
    
    def set_ingredients(self, new_ingredients):
        current_node = self.linked_list.head
        while current_node:
            next_node = current_node.next
            self.linked_list.remove_node(current_node)
            current_node.data['sub_frame'].destroy()
            current_node = next_node

        for i, ingredient in enumerate(new_ingredients):
            self._add_ingredient(content=ingredient)

    def disable_ingredients(self):
        current_node = self.linked_list.head
        while current_node:
            next_node = current_node.next
            sub_frame = current_node.data['sub_frame']
            ingredient: tk.Entry = current_node.data['ingredient']
            ingredient.configure(state='disabled')
            for widget in sub_frame.winfo_children():
                if isinstance(widget, (tk.Button, ttk.Button, ctk.CTkButton)):
                    logger.debug(' widget is a button')
                    widget.grid_remove() # hide buttons, but remember their configuration
            current_node = next_node

    def enable_ingredients(self):
        current_node = self.linked_list.head
        while current_node:
            next_node = current_node.next
            sub_frame = current_node.data['sub_frame']
            ingredient: tk.Entry = current_node.data['ingredient']
            ingredient.configure(state='normal')
            for widget in sub_frame.winfo_children():
                if isinstance(widget, (tk.Button, ttk.Button, ctk.CTkButton)):
                    widget.grid() # put the buttons back in the grid
            current_node = next_node

            

    
    
