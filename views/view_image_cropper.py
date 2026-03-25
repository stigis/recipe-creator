import constants
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import utils
import logging
logger = logging.getLogger(__name__)

class ImageCropper(ctk.CTkToplevel):
    def __init__(self, master, pil_image, callback):
        super().__init__()
        self.title("Select Area")
        self.callback = callback #None # Function to send the cropped image back
        self.original_pil: Image = pil_image
        self.preview_pil: Image = None
        self.tk_image = None #ImageTk.PhotoImage(self.original_pil)
        self.resized_image = None
        self.scale = 0
        
        
        # Load the original image
        #self.original_image = ctk_image
        #self.original_image = ImageTk.PhotoImage(self.original_image)
        # In your Toplevel __init__
        #self.focus()
        #self.lift()
        self.attributes("-topmost", True)    # Force to absolute top
        self.after(10, lambda: self.attributes("-topmost", False)) # Unpin immediately
        self.after(20, utils.zoom_window, self)
        #self.after(1000, self.delayed_setup)
        self.after(1000, self.fit_image) # resize image
        #self.grab_set()
        #self.after(5000, self.grab_release)

        #self.after(1000, utils.zoom_window, self)
        #self.geometry()
        self.canvas = tk.Canvas(self, bg='blue')
        self.canvas.pack(fill='both', expand=True)


        #self.canvas.create_image(0, 0, anchor='nw', image=  self.tk_image)


        #
        # Selection variables
        self.rect_id = None
        self.start_x = None
        self.start_y = None
        self.selection_coords = None
#
        # # Setup Canvas
        #self.canvas = ctk.CTkCanvas(self, width=self.original_image.width, 
        #                           height=self.original_image.height,
        #                           highlightthickness=0)
        #self.canvas.pack()
        #self.canvas.create_image(0, 0, anchor="nw", image=self.original_image)

        ## Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        
        # Action Button
        self.btn_use = ctk.CTkButton(self, text="Use Selection", command=self.crop_and_save, fg_color=constants.Color.FERN_GREEN.value, text_color='#FFFFFF')
        self.btn_use.pack(pady=10)

    def delayed_setup(self):
        original_width, original_height = self.pil_image.size
        self.update()
        frame_width = self.canvas.winfo_width()
        logger.debug(f'canvas width is: {frame_width}')
        if original_width > frame_width:
            logger.info(f'Scaling image. Image width is {original_width}, but frame width is {frame_width}')
            # Will always be a fraction < 1, because the image's width (original width) is bigger
            # Ex: If the image is twice as wide as the frame, the ratio will be 0.5, and the image's width will be halved, allowing it to fit in the frame
            ratio = frame_width / original_width 
            original_width = original_width * ratio
            original_height = original_width * ratio
        self.resized_image: Image = self.pil_image.resize((int(original_width), int(original_height)), Image.LANCZOS)
        #tk_img = ImageTk.PhotoImage(resized_img)
        #scaling = ctk.ScalingTracker.get_widget_scaling(self)
        logger.debug(f'img_frame width is {self.canvas.winfo_width()}')
        logger.debug(f'img_frame height is {self.canvas.winfo_reqheight()}')
        #ctk_img = ctk.CTkImage(resized, size=(resized.width // scaling, resized.height // scaling))
        self.tk_image = ImageTk.PhotoImage(self.resized_image)

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
        # TODO only create/delete rectangle if event coordinates are within the image boundary
        #img_bbox = self.canvas.bbox(self.image_id)
        #click_in_image = (event.x >= img_bbox[0] and event.x <= img_bbox[2]) and (event.y >= img_bbox[1] and event.y <= img_bbox[3])
        click_in_image = self.is_inside_image(event.x, event.y)
        if not click_in_image:
            return
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_drag(self, event):
        # TODO only create/delete rectangle if event coordinates are within the image boundary
        #img_bbox = self.canvas.bbox(self.image_id)
        #drag_in_image = (event.x >= img_bbox[0] and event.x <= img_bbox[2]) and (event.y >= img_bbox[1] and event.y <= img_bbox[3])
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
            
            # Crop the PIL image
            #cropped_img = self.resized_pil.crop((left, top, right, bottom))
            #logger.debug(f'cropped rectangle: left:{left}, top:{top}, right:{right}, bottom:{bottom}')
            
            # Send back to main app and close
            self.callback((left, top, right, bottom), self.preview_pil, self.scale)
            self.destroy()