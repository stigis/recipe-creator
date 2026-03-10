'''
Docstring for img_recipe_extractor.gui.v3.view_header_frame

header frame that contains th titlle label, time, and serving field
'''
import tkinter as tk
import customtkinter as ctk
import constants
from tkinter import filedialog
from PIL import Image, ImageTk
import logging
logger = logging.getLogger(__name__)

class HeaderFrame(ctk.CTkFrame):
    HEADER_BACKGROUND = constants.Color.MUTED_SAGE.value

    def __init__(self, parent):
        super().__init__(parent, fg_color=self.HEADER_BACKGROUND)
        self.pack(padx=15, pady=15, fill='x', ipady=25)
        self.image_label = None
        self.min_entry_width = 175
        self._make_title_entry()
        self._make_image_component()
        self._make_time_component()
        self._make_serving_component()
    
        logger.info(f'entry scaling is: {ctk.ScalingTracker.get_widget_scaling(self.time_value)}')
        logger.info(f'header frame scaling is: {ctk.ScalingTracker.get_widget_scaling(self)}')
        
    
    def _make_title_entry(self):
        #self.title_entry = tk.Entry(self, font = constants.HEADER_1_FONT, justify='center', bg = self.HEADER_BACKGROUND)
        self.title_entry = ctk.CTkEntry(self, font=constants.HEADER_1_FONT, fg_color= self.HEADER_BACKGROUND, justify='center', placeholder_text='Insert Recipe Title here')
        self.title_entry.pack(ipady=5, padx=10, pady=20, fill='x', side='top', anchor='center')
        #self.title_entry.insert('end', 'Insert Recipe Title here')
    
    # makes the Label for the time, and the Entry to modify the time
    def _make_time_component(self):
        #self.time_label = tk.Label(self, text='Time:', font = constants.HEADER_2_FONT, bg = self.HEADER_BACKGROUND)
        self.time_label = ctk.CTkLabel(self, text='Time:', font=constants.HEADER_2_FONT, fg_color=self.HEADER_BACKGROUND)
        self.time_label.pack(side='left', padx=(10, 5), pady=5)

        #self.time_value = tk.Entry(self, font = constants.HEADER_2_FONT)
        label2_font = constants.HEADER_2_FONT
        self.time_value = ctk.CTkEntry(self, font = ctk.CTkFont(label2_font[0], label2_font[1]), placeholder_text='time', width= self.min_entry_width)
        self.time_value.pack(side='left', padx=10, pady=5, ipady=2, fill='x')

        self.time_value.bind('<KeyRelease>', lambda event: self.on_time_entry_key_released(event))

    # makes the Label for the Serving info, and the entry to modify it
    def _make_serving_component(self):
        label2_font = constants.HEADER_2_FONT
        #self.serve_label = tk.Label(self, text='Serves:', font = constants.HEADER_2_FONT, bg = self.HEADER_BACKGROUND)
        self.serve_label = ctk.CTkLabel(self, text='Serves:', font= constants.HEADER_2_FONT, fg_color= self.HEADER_BACKGROUND)

        #self.serve_value = tk.Entry(self, font = constants.HEADER_2_FONT)
        self.serve_value = ctk.CTkEntry(self, font= ctk.CTkFont(label2_font[0], label2_font[1]), placeholder_text='# of servings', width = self.min_entry_width)
        #self.serve_value._entry.
        #self.serve_value.configure(width=len('Insert Serving info here '))
        #self.serve_value.configure(width = len('Insert Serving info here '), bg = self.cget('bg')) # same background as parent

        # Because these are packed to the right, first pack the entry widget, then the label
        self.serve_value.pack(side='right', padx=10, pady=5, ipady=2)
        self.serve_value.bind('<KeyRelease>', lambda event: self.on_serving_entry_key_released(event))
        self.serve_label.pack(side='right', padx=10, pady=5)

    def _make_image_component(self):
        self.img_frame = ctk.CTkFrame(self, fg_color=self.HEADER_BACKGROUND)
        self.img_frame.pack(side='top', fill='x')
        self.image_button = ctk.CTkButton(self.img_frame, text='Upload Image', command= self.on_img_button_clicked)
        self.image_button.pack(side='top')

    # Used to expand and shrink the entry widget for time as the user adds and removes text
    def on_time_entry_key_released(self, event):
        logger.debug(f'Event triggered: {event}')
        entry = event.widget.master # to get the ctk widget
        text = entry.get()
        entry_scaling = ctk.ScalingTracker.get_widget_scaling(entry)
        #logger.debug(f'measure is {self.time_value._font.measure(text)}')
        # must scale the font text and minimum entry width, but all other measurements are already scaled
        new_width = int((entry._font.measure(text) + 40) * entry_scaling)
        end_x = entry.winfo_x() + new_width
        #midpoint = entry.master.winfo_width() // 2
        logger.debug(f'entry start point is: {entry.winfo_x()}, frame start point is: {self.winfo_x()}')
        midpoint = self.winfo_width() // 2
        logger.debug(f'the midpoint is {midpoint}, the entry would end at {end_x}. New width would be {new_width}')
        min_entry_width_scaled = int(self.min_entry_width * entry_scaling)
        if new_width >= min_entry_width_scaled and end_x <= midpoint:
            # we remove the scaling here because it will be applied again when using configure()
            entry.configure(width= new_width // entry_scaling)
        # triggered when a lot of text is deleted at once
        # if the actual width is large, but the required width is less then min_width, reset the width to min_width
        elif new_width < min_entry_width_scaled and entry.winfo_x() + entry.winfo_width() > min_entry_width_scaled:
             entry.configure(width= self.min_entry_width)

    # makes the servings entry box grow. calculations are a little different from the
    # time entry, because the server entry field grows backwards, and the 'Serves' label will 
    # cross the midpoint first
    def on_serving_entry_key_released(self, event):
        logger.debug(f'Event triggered: {event}')
        entry = event.widget.master # to get the ctk widget
        text = entry.get()
        current_width = entry.winfo_width()
        entry_scaling = ctk.ScalingTracker.get_widget_scaling(entry)
        new_width = int((entry._font.measure(text) + 40) * entry_scaling)
        current_start_x = entry.winfo_x()
        width_diff = new_width - current_width
        new_start_x = current_start_x - width_diff
        midpoint = self.winfo_width() // 2
        breakpoint = midpoint + self.serve_label.winfo_width()
        logger.debug(f'the midpoint is {midpoint}, current_start_x is {current_start_x}. New width would be {new_width}, new_start_x would be {new_start_x}')
        min_entry_width_scaled = int(self.min_entry_width * entry_scaling)
        if new_width >= min_entry_width_scaled and new_start_x > breakpoint:
            entry.configure(width = new_width // entry_scaling)
        # triggered when a lot of text is deleted at once
        # if the actual width is large, but the required width is less then min_width, reset the width to min_width
        elif new_width < min_entry_width_scaled and entry.winfo_x() + entry.winfo_width() > min_entry_width_scaled:
            entry.configure(width = self.min_entry_width)

    def on_img_button_clicked(self):
        img_file = filedialog.askopenfilename(
            title='Choose an Image',
            filetypes=[('Image files', '*.png *jpg *jpeg')]
        )
        logger.info(f'the file you chose was: {img_file}')
        if not img_file:
            return
        
        if self.image_label: # if it already exists
            self.image_label.destroy()

        original_img = Image.open(img_file)
        #resized_img = original_img.resize((200, 200)) # optional resize
        #tk_img = ImageTk.PhotoImage(resized_img)
        logger.debug(f'img_frame width is {self.img_frame.winfo_width()}')
        logger.debug(f'img_frame height is {self.img_frame.winfo_reqheight()}')
        ctk_img = ctk.CTkImage(original_img, size=(500, 500))
        self.image_label = ctk.CTkLabel(self.img_frame, image=ctk_img, text='')
        #ctk.CTkImage()
        self.image_label.pack(side='top', padx= 20, pady=10, fill='x', expand=True)

        


    def get_title(self):
        return self.title_entry.get()
    
    def get_time(self):
        return self.time_value.get()
    
    def get_serving(self):
        return self.serve_value.get()
    
    def set_title(self, title):
        self.title_entry.delete('0', 'end')
        self.title_entry.insert('end', title)

    def set_time(self, time):
        self.time_value.delete('0', 'end')
        self.time_value.insert('end', time)

    def set_serving(self, serving):
        self.serve_value.delete('0', 'end')
        self.serve_value.insert('end', serving)

    def disable(self):        
        self.title_entry.configure(state='disabled')
        self.time_value.configure(state='disabled')
        self.serve_value.configure(state='disabled')

    def enable(self):
        self.title_entry.configure(state='normal')
        self.time_value.configure(state='normal')
        self.serve_value.configure(state='normal')


    

