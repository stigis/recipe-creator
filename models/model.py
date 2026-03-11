'''
Docstring for img_recipe_extractor.gui.v3.model

JSON model for recipes
'''
from pydantic  import BaseModel, Field
from typing import List, Optional, ClassVar
import json
import re
from pathlib import Path
import time
import shutil
from PIL import Image
from models.model_recent_files import RecentFileManager
import logging
logger = logging.getLogger(__name__)

# Define the JSON schema using Pydantic
class ModelRecipe(BaseModel):
    recent_file_manager: ClassVar[RecentFileManager] = RecentFileManager()
    snapshot: ClassVar[dict] = None
    PROJECT_ROOT: ClassVar[Path] = Path(__file__).resolve().parent.parent #recipe_builder
    image_dir: ClassVar[Path] = PROJECT_ROOT / 'images' # recipe_builder/images
    image_dir.mkdir(exist_ok=True)


    title: str = Field(description="The title of the recipe")
    time: Optional[str] = Field(description="The amount of time the recipe takes, if it is present")
    serving_size: Optional[str] = Field(alias="serving size", description="The serving size or number of servings, if present")
    ingredients: List[str] = Field(description="An array containing all the ingredients for the recipe")
    directions: List[str] = Field(description="An array containing the step-by-step directions for the recipe")
    description: Optional[str] = Field(description="Any longer description that is provided in the recipe")
    image_ref: Optional[str] = Field(default=None, alias="image ref", description="Optional link to an image of the dish")

    def save_file(self, filepath: str, temp_img_path: str = None):
        if temp_img_path:
            self.copy_image(temp_img_path)
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
        relative_dest = str(Path(*destination.parts[-2:]))
        self.image_ref = relative_dest
        logger.info(f'image_ref is: {relative_dest}')





    @staticmethod
    def read_file(filepath: str):
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
    def get_image(relative_img_path):
        try:
            file_path = Path(ModelRecipe.PROJECT_ROOT, relative_img_path)
            return Image.open(file_path)
        except FileNotFoundError as e:
            logger.error(f' image file not found: {file_path}')
            return None
        except OSError as e:
            logger.error(f'Error reading file: {e}')
            return None



            

    