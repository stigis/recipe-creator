'''
Docstring for img_recipe_extractor.gui.v3.view_header_frame

header frame that contains th titlle label, time, and serving field
'''
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import constants
from tkinter import filedialog
from PIL import Image, ImageTk
from .view_image_cropper import ImageCropper
import logging
logger = logging.getLogger(__name__)

class HeaderFrame(ctk.CTkFrame):
    HEADER_BACKGROUND = constants.Color.MUTED_SAGE.value

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=self.HEADER_BACKGROUND)
        self.pack(padx=15, pady=15, fill='x', ipady=25)
        self.image_label = None
        self.original_pil = None
        self.preview_pil = None # contains the PIL that has been resized to fit inside the gui
        self.min_entry_width = 175
        self.controller = controller 
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
        self.image_button = ctk.CTkButton(self.img_frame, text='Upload Image', command= self.on_img_button_clicked, fg_color='#4F7942', text_color='#FFFFFF')
        self.image_button.pack(side='top')
        self.update()
        logger.debug(f'img frame width is {self.img_frame.winfo_width()}')

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
        img_file: str = filedialog.askopenfilename(
            title='Choose an Image',
            filetypes=[('Image files', '*.png *jpg *jpeg')]
        )
        logger.info(f'the file you chose was: {img_file}')
        if not img_file:
            return

        self.original_pil = Image.open(img_file)
        #self.create_resized_img()
        #ctk_image = self.display_image(self.original_pil)
        self.controller.new_image_path = img_file
        self.update()
        ImageCropper(self, self.original_pil, self.crop_callback)

    # creates a PIL scaled to fit within the screen/gui
    def create_resized_img(self):
        self.update()
        if not self.original_pil:
            return
        
        logger.debug(f'image original size is: {self.original_pil.size}')
        orig_w, orig_h = self.original_pil.size
        frame_width = self.img_frame.winfo_width()
        ratio = frame_width / self.original_pil.width
        new_width = int(orig_w * ratio)
        new_height = int(orig_h * ratio)
        self.preview_pil = self.original_pil.resize(size=(new_width, new_height))
        logger.debug(f'scaling ratio is: {ratio}')
        logger.debug(f'the scaled size is: {self.preview_pil.size}')

    
    # displays the image pil stored in self.original_pil
    # before displaying, it resizes the pil to fit the frame's width and screen height,
    # Then it take ctk scaling into account
    # the self.original_pil object is unchanged
    def display_image(self):
        if self.image_label: # if an image is already being diplayed
            self.image_label.destroy()

        self.update()
        orig_w, orig_h = self.original_pil.size
        frame_width = self.img_frame.winfo_width()
        screen_height = self.winfo_screenheight()
        logger.debug(f'original size is: {self.original_pil.size}')
        scale = min(frame_width / orig_w, screen_height / orig_h)
        logger.debug(f'frame width is {frame_width}, screen height is {screen_height}')
        logger.debug(f'width scaling is {frame_width / orig_w}, height scaling is {screen_height / orig_h}, min is {scale}')

        new_width = int(orig_w * scale)
        new_height = int(orig_h * scale)
        resized_pil: Image = self.original_pil.resize((new_width, new_height))
        ctk_scaling = ctk.ScalingTracker.get_widget_scaling(self.img_frame)
        ctk_img = ctk.CTkImage(resized_pil, size=(resized_pil.width // ctk_scaling, resized_pil.height // ctk_scaling))
        self.image_label = ctk.CTkLabel(self.img_frame, image=ctk_img, text='')
        self.image_label.pack(side='top', padx= 20, pady=10, fill='x', expand=True)



    def display_callback(self, cropped_image):
        if self.image_label: # if an image is already being diplayed
            self.image_label.destroy()


        ctk_image = ctk.CTkImage(cropped_image, size = (500, 500))
        self.image_label = ctk.CTkLabel(self.img_frame, image=ctk_image, text='')
        self.image_label.pack(side='top', padx=20, pady=10, fill='x', expand=True)

    def crop_callback(self, cropped_coords, preview_pil, scale):
        logger.debug(f'cropped coords: {cropped_coords}')
        self.preview_pil = preview_pil
        # r for the resized pil
        rx1, ry1, rx2, ry2 = cropped_coords
        ox1 = rx1 / scale
        ox2 = rx2 / scale
        oy1 = ry1 / scale
        oy2 = ry2 / scale
        logger.debug(f'original cropped conversion: {(ox1, oy1, ox2, oy2)}')
        self.original_pil = self.original_pil.crop((ox1, oy1, ox2, oy2))
        #self.display_image(self.original_pil)
        self.display_image()
        #new_original_pil = self.original_pil.crop((ox1, oy1, ox2, oy2))
        #self.original_pil = new_original_pil
        #self.display_image(self.original_pil)

    def get_image(self):
        '''Returns a PIL image of the image on display in the header, or None if there is no image'''
        if not self.image_label or not self.image_label.winfo_exists():
            return None
        
        image_object: ctk.CTkImage = self.image_label.cget('image')
        pil_image = image_object._light_image or image_object._dark_image
        logger.info(f'image object is: {image_object}')
        logger.info(f'pil image object is {pil_image}')

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

    def set_image(self, image: Image):
        self.original_pil = image
        self.display_image()

    def remove_image(self):
        if self.image_label:
            self.image_label.destroy()
            self.image_label = None
        
    def show_img_error(self):
        messagebox.showerror(title='Image Error', message='The image of the dish could not be loaded. See logs for more details')

    def disable(self):        
        self.title_entry.configure(state='disabled')
        self.time_value.configure(state='disabled')
        self.serve_value.configure(state='disabled')

    def enable(self):
        self.title_entry.configure(state='normal')
        self.time_value.configure(state='normal')
        self.serve_value.configure(state='normal')


    

