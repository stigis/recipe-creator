import constants
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import utils
import logging
logger = logging.getLogger(__name__)

class ImageCropper(ctk.CTkToplevel):
    def __init__(self, master, pil_image, callback, whole_callback):
        super().__init__()
        self.title("Select Area")
        self.callback = callback #None # Function to send the cropped image back
        self.whole_img_callback = whole_callback
        self.original_pil: Image = pil_image
        self.preview_pil: Image = None
        self.tk_image = None #ImageTk.PhotoImage(self.original_pil)
        self.resized_image = None
        self.scale = 0
        
        # Create the canvas now, but the image will only be added later
        # in a callback that executes after the toplevel has been fully created, zoomed, and the canvas expanded
        self.canvas = tk.Canvas(self, bg=constants.Color.CREAM.value)
        self.canvas.pack(fill='both', expand=True)

        # Selection variables
        self.rect_id = None
        self.start_x = None
        self.start_y = None
        self.selection_coords = None

        ## Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        
        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color=constants.Color.MUTED_SAGE.value)
        self.btn_frame.pack(fill='x')
        self.btn_use = ctk.CTkButton(self.btn_frame, text="Use Selection", command=self.crop_and_save, fg_color=constants.Color.FERN_GREEN.value, text_color='#FFFFFF')
        self.btn_use_whole = ctk.CTkButton(self.btn_frame, text='Use the entire image', command=self.use_whole_image, fg_color=constants.Color.FERN_GREEN.value, text_color='#FFFFFF')
        
        self.btn_frame.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_columnconfigure(3, weight=1)
        self.btn_use.grid(row=0, column=1, padx=5, pady=10, sticky='ew')
        self.btn_use_whole.grid(row=0, column=2, padx=5, pady=10, sticky='ew')

        # maximize window and add image. Is called after the window loads using after_idle()
        self.after_idle(self.maximize_window)

    def maximize_window(self):
        self.lift()
        self.attributes('-topmost', True)
        self.focus_set()
        utils.zoom_window(self)
        self.after_idle(self.fit_image)

    def fit_image(self):
        self.update()
        # Get current canvas size
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        logger.debug(f'canvas width is: {canvas_w}')
        logger.debug(f'canvas height is: {canvas_h}')
        
        # Original dimensions
        img_w, img_h = self.original_pil.size

        # 3. Calculate scale factor to fit inside canvas
        # Use min() to ensure neither dimension exceeds the canvas
        scale = min(canvas_w / img_w, canvas_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        self.scale = scale

        # 4. Resize and Update
        self.preview_pil = self.original_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        #self.resized_pil = self.original_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.preview_pil)
        
        # Clear and Draw (Centered)
        self.canvas.delete("all")
        self.image_id = self.canvas.create_image(canvas_w//2, canvas_h//2, anchor='center', image=self.tk_image)
        logger.debug(f'image coords are {self.canvas.coords(self.image_id)}')
        

    def on_press(self, event):
        # Reset/Start new rectangle
        self.start_x = event.x
        self.start_y = event.y

        # only create/delete rectangle if event coordinates are within the image boundary
        click_in_image = self.is_inside_image(event.x, event.y)
        if not click_in_image:
            return
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_drag(self, event):
        # only create/delete rectangle if event coordinates are within the image boundary
        drag_in_image = self.is_inside_image(event.x, event.y)
        if not drag_in_image:
            return

        # Update rectangle size as mouse moves
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)
        self.selection_coords = (self.start_x, self.start_y, event.x, event.y)

    def is_inside_image(self, x, y):
        img_bbox = self.canvas.bbox(self.image_id)
        is_inside_image = (x >= img_bbox[0] and x <= img_bbox[2]) and (y >= img_bbox[1] and y <= img_bbox[3])
        return is_inside_image


    def crop_and_save(self):
        self.update()
        # 1. Get the canvas coordinates of the image object
        img_x, img_y = self.canvas.coords(self.image_id)
        

        # 2. Adjust for the anchor point 
        # (By default, images are anchored at the 'center')
        width = self.preview_pil.width
        height = self.preview_pil.height
        top_left_x = img_x - (width / 2)
        top_left_y = img_y - (height / 2)
        if self.selection_coords:
            # Normalize coords (in case user drags backwards)
            x1, y1, x2, y2 = self.selection_coords
            left, right = sorted([x1, x2])
            top, bottom = sorted([y1, y2])

            # Calculate relative coordinates
            left = left - top_left_x
            right = right - top_left_x
            top = top - top_left_y
            bottom = bottom - top_left_y
                        
            # Send back to main app and close
            # The main app will perform calculations to scale the coordinates on the resized image to the original image
            self.callback((left, top, right, bottom), self.preview_pil, self.scale)
            self.destroy()

    def use_whole_image(self):
        self.whole_img_callback()
        self.destroy()