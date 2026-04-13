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
from pathlib import Path
import sys
import subprocess
import requests
import threading
from controllers.api_key_controller import APIKeyController
from controllers.ai_controller import AIController

import programs.img_recipe_extractor
import programs.extract_recipe_from_website

import logging
logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # running from a bundle in pyinstaller
    ROOT_DIR = Path(sys._MEIPASS).resolve().parent
    PROGRAMS_DIR = ROOT_DIR
else:
    # running locally in python script
    # this gives the programs directory
    ROOT_DIR = Path(__file__).resolve().parent.parent
    PROGRAMS_DIR = ROOT_DIR / 'programs'

#CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) # the directory containing this file
# get the parent directory that contains this file
#PARENT_DIR = os.path.dirname(CURRENT_DIR)
#PROGRAMS_DIR = ROOT_DIR / 'programs' #os.path.join(PARENT_DIR, "programs")
#WEBSITE_PROCCESING_SCRIPT = PROGRAMS_DIR / 'extract_recipe_from_website.py' #os.path.join(PROGRAMS_DIR, "extract_recipe_from_website.py")
WEBSITE_OUTPUT_DIR = PROGRAMS_DIR / 'output' / 'website'
WEBSITE_JSON_OUTPUT_NAME =  PROGRAMS_DIR / 'output' / 'website' / 'gemma_output.json' #os.path.join(PROGRAMS_DIR, "output", "website", "gemma_output.json")
WEBSITE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

#IMG_PROCESSING_SCRIPT = PROGRAMS_DIR / 'img_recipe_extractor.py' #os.path.join(PROGRAMS_DIR, "img_recipe_extractor.py")
IMG_OUTPUT_DIR = PROGRAMS_DIR / 'output' / 'img' #os.path.join(PROGRAMS_DIR, "output", "img")
IMG_JSON_OUTPUT_NAME = PROGRAMS_DIR / 'output' / 'img' / 'output_filename.txt' #os.path.join(PROGRAMS_DIR, "output", "img", "output_filename.txt") 
IMG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class Controller:
    def __init__(self):
        #self.model = Model()
        # create other controllers first since the views reference on them. Avoid null pointer exceptions
        self.api_key_controller = APIKeyController()
        self.ai_controller = AIController()
        self.view = View(self)
        self.api_key_controller.set_view(self.view) # set here to avoid a Null pointer exception
        self.api_key_controller.check_api_key()
        self.ai_controller.set_view(self.view)

        self.current_file = None
        self.has_new_image = False
        self.current_image_path = None
        self.new_image_path = None
        recents_list = ModelRecipe.recent_file_manager.recent_files
        self.view.init_recents_list(recents_list)
        snapshot: dict = self.build_json()
        ModelRecipe.set_snapshot(snapshot)


        logger.debug(f'Snapshot: {snapshot}')
        #logger.info(f'CURRENT_DIR in controller.py is: {CURRENT_DIR}')
        logger.info(f'ROOT_DIR is: {ROOT_DIR}')
        #logger.info(f'PROGRAMS_DIR is: {PROGRAMS_DIR}')
        #logger.info(f'The Website processing script is located at: {WEBSITE_PROCCESING_SCRIPT}')
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
            logger.info(f'is there a new image: {self.new_image_path != None and self.new_image_path != ''}')
            if self.new_image_path:
                # get the pil image object and save it
                new_image = self.view.header_frame.original_pil
                recipe_model.save_file(self.current_file, new_image_path= self.new_image_path, image_pil = new_image, old_image_path= self.current_image_path)
            else:
                recipe_model.save_file(self.current_file)

            if recipe_model.image_ref:
                self.current_image_path = recipe_model.image_ref
            
            self.view.status_bar.configure(text=f'Saved {self.get_basename(self.current_file)}   ')
            #ModelRecipe.set_snapshot(json_data)
            ModelRecipe.set_snapshot(recipe_model.model_dump(by_alias=True))
            if recipe_model.image_ref:
                self.current_image_path = recipe_model.image_ref
            self.new_image_path = None # reset
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
        if self.new_image_path:
            # get the pil image object and save it
            new_image = self.view.header_frame.original_pil
            recipe_model.save_file(file_path, new_image_path= self.new_image_path, image_pil = new_image)
        else:
            recipe_model.save_file(file_path)
        if recipe_model.image_ref:
            self.current_image_path = recipe_model.image_ref


        self.current_file = file_path
        self.view.status_bar.configure(text=f'Saved {self.get_basename(self.current_file)}   ')
        #ModelRecipe.set_snapshot(json_data)
        ModelRecipe.set_snapshot(recipe_model.model_dump(by_alias=True))
        self.new_image_path = None # image has been saved, reset
        return True
    
    def clear_json(self):
        '''Clears all data loaded into the Gui to start a new recipe'''
        #are_snapshots_identical = self.compare_to_snapshot()
        #if not are_snapshots_identical:
        #    response = messagebox.askyesnocancel(title='Clear', message='Would you like to save your changes before clearing?')
        #    if response == None:
        #        return # cancel operation
        #    elif response == True: # user wants to save
        #        saved = self.save()
        #        if not saved:
        #            return
        #    # if response is false, user does not want to sae, continue operation
        proceed = self.check_save_prompt(message='Would you like to save your changes before Clearing')
        if not proceed:
            return
        logger.info('Clearing content from the gui')
        self.view.clear_json()
        self.current_file = None
        self.current_image_path = None
        self.new_image_path = None
        new_snapshot = self.build_json()
        ModelRecipe.set_snapshot(new_snapshot)

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
        
        self.view.make_popup(label_msg= 'Importing recipe from image')
        thread = threading.Thread(target= lambda: self.import_image_thread(image_path= file_path))
        thread.start()

    def import_image_thread(self, image_path):
        try:
            result = programs.img_recipe_extractor.import_image(image_path, output_dir= IMG_OUTPUT_DIR, ai_model=self.ai_controller.get_image_import_model(), debug=False)
            self.view.after(0, self.after_import_image_thread)
        except Exception as e:
            self.view.after(0, self.after_import_image_thread, e)
    
    def after_import_image_thread(self, error=None):
        if error:
            self.view.update_popup_status(message= f'There was an error extracting the recipe from the given website\nError...\n{error}')
            self.view.finish_popup_progress()
            return
        else:
            self.view.update_popup_status(message='content parsed successfully. Beginning import...')
            with open(IMG_JSON_OUTPUT_NAME, 'r') as temp_file:
                output_name = temp_file.read()
            if not output_name:
                return
            # TODO use model to read the data
            json_file_path = os.path.join(IMG_OUTPUT_DIR, output_name)
            logger.info(f"the json file generated from the image is: {json_file_path}" )

            recipe_json = ModelRecipe.read_file(json_file_path)
            self.load_json_file(recipe_json, json_file_path)
            self.view.update_popup_status(message= 'Import Completed')
            self.view.finish_popup_progress()



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
            #result = subprocess.run(
            #    ['python', WEBSITE_PROCCESING_SCRIPT, url],
            #    cwd= PROGRAMS_DIR,
            #    text=True,
            #    check=True
            #)
            result = programs.extract_recipe_from_website.import_recipe(url)
            self.view.after(0, self.after_import_website_thread)
        except Exception as e:
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
            except Exception as e:
                self.view.after(0, callback, e)

        thread = threading.Thread(target=lambda: run_thread(process, callback), daemon=True)
        thread.start()


    
    def import_ai_recipe(self, recipe_json_str):
        json_object = ModelRecipe.read_json_str(recipe_json_str)
        self.load_json_file(json_object, filepath=None)
    
    def load_json_file(self, recipe_json, filepath):
        """Populate the view with JSON data validated by the Model"""
        image = None
        image_error = False
        if recipe_json.get('image ref', None):
            self.current_image_path = recipe_json['image ref']
            image = ModelRecipe.get_image(self.current_image_path)
            if not image: # error loading image
                image_error = True
        else:
            self.current_image_path = None # no image present
        
        if filepath:
            self.current_file = filepath
            #self.view.add_recent_file(filepath, ModelRecipe.recent_file_manager.MAX)
            ModelRecipe.set_snapshot(recipe_json) # only change the snapshot if we are loading from a file (saved data)

        # TODO view.load_json(recipeJson, filepath)
        self.view.load_json(recipe_json, image=image, image_error=image_error, filepath=filepath, max_recents=ModelRecipe.recent_file_manager.MAX)

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
        logger.debug(f'last snapshot: {last_snapshot}')
        logger.debug(f'current snapshot: {current_snapshot}')
        return last_snapshot == current_snapshot
    
    def check_save_prompt(self, message):
        """Checks if the current snapshot is identical to the previous one, and provides a prompt if it's not
        Returns True if the user has saved, or allowed the program to continue without saving.
        Returns False if the user does not want to continue the operation"""
        are_snapshots_identical = self.compare_to_snapshot()
        if are_snapshots_identical:
            return True
        
        response = messagebox.askyesnocancel(message= message)
        if response == True: # perform a save operation
            saved = self.save()
            return saved
        elif response == False: # user does not care about saving and wants to proceed
            return True
        else:
            return False # when user clicks 'Cancel', response == None


                
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