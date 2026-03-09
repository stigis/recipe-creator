'''
Docstring for img_recipe_extractor.gui.v3.view_scrollable_frame

Creates a scrollable frame with a scrollbar. The frame will automatically expand vertically
as necessary to fit new widgets added to it.

Behind the scenes, this is really a scrollbar and a canvas that contains a window that contains a frame.
The canvas is also wrapped in a parent frame. This is the structure:

parent_frame (this is self):
    scrollbar
    canvas:
        scrollable frame
        canvas window linked to scrollable frame
'''
import tkinter as tk
import constants

class ScrollableFrameContainer(tk.Frame):

    # the parent used here is the parent of the actual parent frame (i.e. root), not of the scrollable frame
    # self (this object) is the parent frame that contains the canvas and scrollbar
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief='solid') # this is the parent frame
        #self.parent_frame = tk.Frame(parent, borderwidth=1, relief='solid')
        self.pack(fill=tk.BOTH, expand=True) # fill everything

        self.canvas = tk.Canvas(self, bg='red') # if you see red in the GUI, it's the canvas and should be covered up
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command = self.canvas.yview)
        self.canvas.config(yscrollcommand = self.scrollbar.set)

        # the actual scrollable frame widget
        self.scrollable_frame = tk.Frame(self.canvas, bg = constants.Color.BEIGE.value)
        # create the window inside the canvas and link it to the scrollable frame
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self._make_bindings()

        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill=tk.BOTH, expand=True)
        #self.scrollable_frame.pack(fill='both', expand=True)

    # Always sets the window inside the canvas to have the same width as the canvas
    # This window contains the frame, allowing the frame to cover the entirety of the canvas  
    def on_canvas_configure(self, event):
        print('canvas event is.. ', event)
        canvas_width = event.width
        canvas_height = event.height
        self.canvas.itemconfig(self.canvas_window_id, width = canvas_width)
        self.canvas.itemconfig(self.canvas_window_id, height = canvas_height)


    # called when the actual scrollable frame inside the canvas is configured
    def on_frame_configure(self, event):
        print('scrollable frame event is.. ', event)
        # Update the canvas window height to match the frame's new required height
        self.canvas.itemconfig(self.canvas_window_id, height = self.scrollable_frame.winfo_reqheight())
        #self.canvas.itemconfig(self.canvas_window_id, width = self.canvas.winfo_reqwidth()) does not give desired results

        # Update scrollbar area to match the new window size
        self.canvas.configure(scrollregion = self.canvas.bbox('all'))

    def _make_bindings(self):
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind_all('<MouseWheel>', lambda e: self.canvas.yview_scroll(int(-1 * e.delta / 120), "units"))
        self.scrollable_frame.bind('<Configure>', self.on_frame_configure)

        #self.scrollable_frame.bind('<<UpdateCanvasWindow>>', lambda e : self.on_frame_configure(event=e))