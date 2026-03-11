'''
Docstring for img_recipe_extractor.gui.v3.controller

Controller for reading/writing JSON recipe files, and reading/writing them to the GUI
'''

from models.model import ModelRecipe
from views.view import View
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
import utils
import os.path
import subprocess
import requests
import threading
from controllers.api_key_controller import APIKeyController

import logging
logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) # the directory containing this file
# get the parent directory that contains this file
PARENT_DIR = os.path.dirname(CURRENT_DIR)
PROGRAMS_DIR = os.path.join(PARENT_DIR, "programs")
WEBSITE_PROCCESING_SCRIPT = os.path.join(PROGRAMS_DIR, "extract_recipe_from_website.py")
WEBSITE_JSON_OUTPUT_NAME = os.path.join(PROGRAMS_DIR, "output", "website", "gemma_output.json")

IMG_PROCESSING_SCRIPT = os.path.join(PROGRAMS_DIR, "img_recipe_extractor.py")
IMG_OUTPUT_DIR = os.path.join(PROGRAMS_DIR, "output", "img")
IMG_JSON_OUTPUT_NAME = os.path.join(PROGRAMS_DIR, "output", "img", "output_filename.txt") 

class Controller:
    def __init__(self):
        #self.model = Model()
        # create other controllers first since the views reference on them. Avoid null pointer exceptions
        self.api_key_controller = APIKeyController()
        self.view = View(self)
        self.api_key_controller.set_view(self.view) # set here to avoid a Null pointer exception
        
        self.current_file = None
        self.temp_image_path = None
        self.current_image_path = None
        recents_list = ModelRecipe.recent_file_manager.recent_files
        self.view.init_recents_list(recents_list)
        snapshot: dict = self.build_json()
        ModelRecipe.set_snapshot(snapshot)


        logger.debug(f'Snapshot: {snapshot}')
        logger.info(f'CURRENT_DIR in controller.py is: {CURRENT_DIR}')
        logger.info(f'PROGRAMS_DIR is: {PROGRAMS_DIR}')
        logger.info(f'The Website processing script is located at: {WEBSITE_PROCCESING_SCRIPT}')
        logger.info(f'The Website processing script is outputting to: {WEBSITE_JSON_OUTPUT_NAME}')


    def main(self):
        logger.info('starting main in controller..')
        self.view.main()

    def open_file(self, file_path=None):
        logger.info('ran open_file()')
        if not file_path: # ask for a file
            file_path = filedialog.askopenfilename(
                title='Choose a Recipe to open',
                filetypes=[('JSON Files', '*json')]
            )
            if not file_path:
                return
        try:
            json_data = ModelRecipe.read_file(file_path) # validates the model schema
        except FileNotFoundError as e:
            print(e.strerror)

            self.view.show_error(error_message=e, msg_title='File Not Found')
        else:
            self.load_json_file(json_data, file_path)


    # Return True if a file was saved, false otherwise
    def save(self, event=None):
        logger.info('ran save()')
        if not self.current_file:
            logger.info('no current file to save, running save_as()')
            return self.save_as()
        else:
            json_data = self.build_json()
            recipe_model = ModelRecipe(**json_data)
            recipe_model.save_file(self.current_file, self.temp_image_path)
            
            self.view.status_bar.configure(text=f'Saved {self.get_basename(self.current_file)}   ')
            #ModelRecipe.set_snapshot(json_data)
            ModelRecipe.set_snapshot(recipe_model.model_dump(by_alias=True))
            if recipe_model.image_ref:
                self.current_image_path = recipe_model.image_ref
            self.set_temp_img_path(None) # image has been saved, reset
            return True

            
    # Return True if a file was saved, false otherwise
    def save_as(self):
        logger.info('ran save_as()')
        file_path = filedialog.asksaveasfilename(
            title='Save Recipe As',
            filetypes=[('JSON Files', '*.json')]
        )
        if not file_path:
            return False
        
        json_data = self.build_json()
        logger.debug(f'json data to save: {json_data}')
        recipe_model = ModelRecipe(**json_data)
        recipe_model.save_file(file_path, self.temp_image_path)
        if recipe_model.image_ref:
            self.current_image_path = recipe_model.image_ref


        self.current_file = file_path
        self.view.status_bar.configure(text=f'Saved {self.get_basename(self.current_file)}   ')
        #ModelRecipe.set_snapshot(json_data)
        ModelRecipe.set_snapshot(recipe_model.model_dump(by_alias=True))
        self.set_temp_img_path(None) # image has been saved, reset
        return True

    def open_chat(self):
        logger.info('ran open_chat()')
        self.view.open_chat()

    def import_image(self):
        """
        Opens up a dialog for the user to select an image file.
        Runs 'recipe_extractor.py' with the image as input to generate a 
        JSON file of the recipe. Then imports that JSON recipe file into the GUI view
        """
        logger.info('ran import_image()')
        messagebox.showinfo('Import Recipe Picture', 'Select an image file to convert into a recipe.\nThis will consume one API request')
        file_path = filedialog.askopenfilename(
            title='Select an image of a recipe',
            filetypes=[('Image files', '*jpg *jpeg *png')]
            )
        if not file_path:
            return
        
        try:
            result = subprocess.run(
                ['python', IMG_PROCESSING_SCRIPT, '-i', file_path, '-o', IMG_OUTPUT_DIR],
                cwd= PROGRAMS_DIR,
                text=True,
                check=True
            )
            messagebox.showinfo('Img Script Completed', 'Image script completed... importing recipe file into viewer')
        except subprocess.CalledProcessError as e:
            messagebox.showerror(f'Img Script error', 'There was an error in the image processing script\nOutput was:\n{e}')
            return
        
        with open(IMG_JSON_OUTPUT_NAME, 'r') as temp_file:
            output_name = temp_file.read()
            if not output_name:
                return
        # TODO use model to read the data
        json_file_path = os.path.join(IMG_OUTPUT_DIR, output_name)
        logger.info("the json file generated from the image is: ", json_file_path)

        recipe_json = ModelRecipe.read_file(json_file_path)
        self.load_json_file(recipe_json, json_file_path)

    def import_website(self):
        logger.info('ran import_website()')
        url = self.view.show_url_input_box()
        if not url:
            return
        
        self.view.make_popup(label_msg= 'Importing recipe from website')
        thread = threading.Thread(target= lambda: self.import_website_thread(url), daemon=True)
        thread.start()

    def import_website_thread(self, url):
        try:
            result = subprocess.run(
                ['python', WEBSITE_PROCCESING_SCRIPT, url],
                cwd= PROGRAMS_DIR,
                text=True,
                check=True
            )
            self.view.after(0, self.after_import_website_thread)
        except subprocess.CalledProcessError as e:
            self.view.after(0, self.after_import_website_thread, e)

    def after_import_website_thread(self, error=None):
        if error:
            self.view.update_popup_status(message= f'There was an error extracting the recipe from the given website\nError...\n{error}')
            self.view.finish_popup_progress()
            return
        else:
            self.view.update_popup_status(message='content parsed successfully. Beginning import...')
            recipe_json = ModelRecipe.read_file(WEBSITE_JSON_OUTPUT_NAME)
            self.load_json_file(recipe_json, WEBSITE_JSON_OUTPUT_NAME)
            self.view.update_popup_status(message= 'Import Completed')
            self.view.finish_popup_progress()
        

        

    def run_subprocess(self, msg, process, callback):
        self.view.make_popup(msg)
        def run_thread(process, callback):
            try:
                process()
                self.view.after(0, callback)
            except subprocess.CalledProcessError as e:
                self.view.after(0, callback, e)

        thread = threading.Thread(target=lambda: run_thread(process, callback), daemon=True)
        thread.start()


    
    def import_ai_recipe(self, recipe_json_str):
        json_object = ModelRecipe.read_json_str(recipe_json_str)
        self.load_json_file(json_object, file_path=None)

    def load_json_file(self, recipe_json, file_path):
        """Populate the view with JSON data validated by the Model"""
        view = self.view
        mode = view.menu_bar.get_mode().get()
        logger.info(f'mode is: {mode}')
        if mode == 'View':
            view.switch_to_edit()
        header = view.header_frame
        header.set_title(recipe_json['title'])
        header.set_time(recipe_json['time'] or "")
        header.set_serving(recipe_json['serving size'] or "")
        if recipe_json["image ref"]:
            self.current_image_path = recipe_json["image ref"]
            image = ModelRecipe.get_image(self.current_image_path)
            if image:
                header.set_image(image)
            else:
                header.show_img_error()
        view.ingredients_frame.set_ingredients(recipe_json['ingredients'])
        view.directions_frame.set_directions(recipe_json['directions'])
        view.description_frame.set_description(recipe_json['description'] or "")
        if file_path:
            self.current_file = file_path
            self.view.status_bar.configure(text=f'Opened {self.get_basename(self.current_file)}   ')
            self.view.add_recent_file(file_path, ModelRecipe.recent_file_manager.MAX)
            ModelRecipe.set_snapshot(recipe_json) # only change the snapshot if we are loading from a file (saved data)

        self._update_visibility()
        if mode == 'View':
            view.switch_to_view()


    def build_json(self):
        '''
            builds a JSON object from the contents of the view Gui
        '''
        logger.info('building json...')
        view = self.view
        header = view.header_frame
        title = header.get_title()
        time = header.get_time()
        serving = header.get_serving()
        ingredients = view.ingredients_frame.get_ingredients()
        directions = view.directions_frame.get_directions()
        description = view.description_frame.get_description()
        image_ref = self.current_image_path
       
        recipe_json = {
            'title': title,
            'time': time,
            'serving size': serving,
            'ingredients': ingredients,
            'directions': directions,
            'description': description,
            'image ref': image_ref
        }
        return recipe_json
    
    def compare_to_snapshot(self):
        last_snapshot = ModelRecipe.snapshot
        current_snapshot = self.build_json()
        logger.debug(f'are the snapshots the same?: {last_snapshot == current_snapshot}')
        return last_snapshot == current_snapshot
    
    def set_temp_img_path(self, img_path):
        self.temp_image_path = img_path
        logger.info(f'temp image path is: {img_path}, the image will not be copied and saved until the recipe is saved')
        
    def export_to_mongo(self):
        result = messagebox.askyesno(title='Export to Database', message='Are you sure you want to add this Recipe to the database?')
        if not result:
            return
        payload = self.build_json()
        response = requests.post('http://localhost:5000/api/data', json= payload)
        logger.info(f'status is: {response.status_code}')
        logger.debug(response)
        if response.status_code == 409:
            override = messagebox.askretrycancel(title='Override existing recipe', message='A recipe with this name already exists in the database. Would you like to override it?')
            if override:
                response = requests.put('http://localhost:5000/api/data', json= payload)
    
    # update all widgets to perform any necessary resizing, ect...
    def _update_visibility(self):
        self.view.update()
        self.update_widgets(self.view)
        
        #self.view.description_frame.description_text._update_height(event=None)

    '''
        Recursively serach through the widget tree
        Call _update_height for any AutoSizingTextbox widgets
        Uses DFS
    '''
    def update_widgets(self, parent):
        for child in parent.winfo_children():
            if isinstance(child, utils.AutoSizingTextbox):
                child._update_height(event=None)
            
            self.update_widgets(child)

    def get_basename(self, absolute_filepath: str):
        return os.path.basename(absolute_filepath).split('.json')[0]

        

if __name__ == '__main__':
    logger.info('running program from Controller')
    controller = Controller()
    controller.main()