'''
Docstring for img_recipe_extractor.gui.v3.model

JSON model for recipes
'''
from pydantic  import BaseModel, Field
from typing import List, Optional, ClassVar
import os
import json
import re
from pathlib import Path
import sys
import time
import shutil
from PIL import Image
from platformdirs import PlatformDirs
from models.model_recent_files import RecentFileManager
import constants
import logging
logger = logging.getLogger(__name__)

# Define the JSON schema using Pydantic
class ModelRecipe(BaseModel):
    recent_file_manager: ClassVar[RecentFileManager] = RecentFileManager()
    snapshot: ClassVar[dict] = None
    PROJECT_ROOT: ClassVar[Path] = None # set at the bottom of the file #Path(__file__).resolve().parent.parent #recipe_builder
    image_dir: ClassVar[Path] = None #PROJECT_ROOT / 'images' # recipe_builder/images
    dirs: ClassVar[PlatformDirs] = None
    #image_dir.mkdir(exist_ok=True)


    title: str = Field(description="The title of the recipe")
    time: Optional[str] = Field(description="The amount of time the recipe takes, if it is present")
    serving_size: Optional[str] = Field(alias="serving size", description="The serving size or number of servings, if present")
    ingredients: List[str] = Field(description="An array containing all the ingredients for the recipe")
    directions: List[str] = Field(description="An array containing the step-by-step directions for the recipe")
    description: Optional[str] = Field(description="Any longer description that is provided in the recipe")
    image_ref: Optional[str] = Field(default=None, alias="image ref", description="Optional link to an image of the dish")

    def save_file(self, filepath: str, new_image_path: str = None, image_pil: Image = None, old_image_path=None):
        if new_image_path:
            self.save_image(new_image_path, image_pil, old_image_path)
        
        logger.info(f'saving to {filepath}')
        json_string: str = self.model_dump_json(by_alias=True, indent=4)
        with open(filepath, 'w', encoding='utf-8') as json_file:
            json_file.write(json_string)

        ModelRecipe.recent_file_manager.add_file(filepath)
        logger.info(f'saved file {filepath}')
        #return json.loads(json_string)

    def copy_image(self, temp_image):
        original_file = Path(temp_image)
        stem = original_file.stem # basename without suffix
        suffix = original_file.suffix
        timestamp = int(time.time())
        filename = f'{stem}_{timestamp}{suffix}'
        destination = Path(self.image_dir, filename)
        logger.info(f'destination file is: {destination}')
        if destination.exists():
            logger.error('A file with this name already exists! Cannot overwrite!')
            return
        logger.info(f'copying image {temp_image} to destination {destination}')
        shutil.copy2(temp_image, destination)
        logger.info(f'destination parts are: {destination.parts}')
        relative_dest = str(Path(*destination.parts[-1:]))
        self.image_ref = relative_dest
        logger.info(f'image_ref is: {self.image_ref}')

    def save_image(self, image_path, image: Image, old_image_path):
        original_file = Path(image_path)
        stem = original_file.stem # basename without suffix
        suffix = original_file.suffix
        timestamp = int(time.time())
        filename = f'{stem}_{timestamp}{suffix}'
        destination = Path(self.image_dir, filename)
        logger.info(f'destination file is: {destination}')
        if destination.exists():
            logger.error('A file with this name already exists! Cannot overwrite!')
            return
        logger.info(f'saving image {image_path} to destination {destination}')
        image.save(destination)
        logger.info(f'destination parts are: {destination.parts}')
        relative_dest = str(Path(*destination.parts[-1:]))
        self.image_ref = relative_dest
        logger.info(f'image_ref is: {self.image_ref}')
        if old_image_path:
            self.delete_old_image(old_image_path)

    def delete_old_image(self, old_image_path):
        # TODO replace with platformdirs image directory
        #full_path = Path(ModelRecipe.PROJECT_ROOT, old_image_path)
        full_path = ModelRecipe.image_dir / old_image_path
        try:
            os.remove(full_path)
            logger.info(f'deleted old image {full_path}, it has been replaced by a newer image')
        except FileNotFoundError:
            logger.error(f'could not find file to delete: {full_path}')
        except PermissionError:
            logger.error(f'Permission denied or file is in use: {full_path}')
        except Exception as e:
            logger.error(f'An error occured: {e}')


    @staticmethod
    def read_file(filepath: str):
        if filepath:
            filepath = str(filepath) # ensure filepath is a str and not a Path
        with open(filepath, 'r', encoding='utf-8') as json_file:
            json_object = json.load(json_file)
        logger.debug(f'Loaded json object from file: {json_object}')
        recipe_model = ModelRecipe(**json_object) # validate schema of the file
        ModelRecipe.recent_file_manager.add_file(filepath)
        return recipe_model.model_dump(by_alias=True)
    
    @staticmethod
    def read_json_str(recipe_json_str: str) -> (dict):
        match: re.Match = re.search(r"\{.*\}", recipe_json_str, re.DOTALL)
        if not match:
            logger.error('Error: input string did not contain a JSON object')
            logger.error(f'Input String: {recipe_json_str}')
            return None
        
        json_str = match.group(0)
        json_object = json.loads(json_str)
        ModelRecipe(**json_object) # validate schema of the json string
        return json_object


    
    @staticmethod
    def set_snapshot(json_content):
        ModelRecipe.snapshot = json_content

    @staticmethod
    def get_image(relative_img_path) -> Image:
        try:
            #file_path = Path(ModelRecipe.PROJECT_ROOT, relative_img_path)
            file_path = ModelRecipe.image_dir / relative_img_path
            return Image.open(file_path)
        except FileNotFoundError as e:
            logger.error(f' image file not found: {file_path}')
            return None
        except OSError as e:
            logger.error(f'Error reading file: {e}')
            return None

    @staticmethod
    def init_project_root():
        if getattr(sys, 'frozen', False):
            # running in a bundle
             ModelRecipe.PROJECT_ROOT = Path(sys._MEIPASS).resolve().parent
        else:
            # running script locally
            ModelRecipe.PROJECT_ROOT = Path(__file__).resolve().parent.parent
        
        # init images folder for models
        ModelRecipe.dirs = PlatformDirs(appname=constants.APP_NAME, appauthor=False)
       # ModelRecipe.image_dir = ModelRecipe.PROJECT_ROOT / 'images'
        ModelRecipe.image_dir = ModelRecipe.dirs.user_data_path / 'images'
        ModelRecipe.image_dir.mkdir(exist_ok=True)
        logger.info(f'PROJECT ROOT is: {ModelRecipe.PROJECT_ROOT}')
        logger.info(f'image directory is: {ModelRecipe.image_dir}')

ModelRecipe.init_project_root()



            

    