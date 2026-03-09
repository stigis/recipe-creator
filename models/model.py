'''
Docstring for img_recipe_extractor.gui.v3.model

JSON model for recipes
'''
from pydantic  import BaseModel, Field
from typing import List, Optional, ClassVar
import json
import re
from models.model_recent_files import RecentFileManager
import logging
logger = logging.getLogger(__name__)

# Define the JSON schema using Pydantic
class ModelRecipe(BaseModel):
    recent_file_manager: ClassVar[RecentFileManager] = RecentFileManager()
    snapshot: ClassVar[dict] = None

    title: str = Field(description="The title of the recipe")
    time: Optional[str] = Field(description="The amount of time the recipe takes, if it is present")
    serving_size: Optional[str] = Field(alias="serving size", description="The serving size or number of servings, if present")
    ingredients: List[str] = Field(description="An array containing all the ingredients for the recipe")
    directions: List[str] = Field(description="An array containing the step-by-step directions for the recipe")
    description: Optional[str] = Field(description="Any longer description that is provided in the recipe")

    def save_file(self, filepath: str):
        logger.info(f'saving to {filepath}')
        json_string: str = self.model_dump_json(by_alias=True, indent=4)
        with open(filepath, 'w', encoding='utf-8') as json_file:
            json_file.write(json_string)

        ModelRecipe.recent_file_manager.add_file(filepath)
        logger.info(f'saved file {filepath}')

    @staticmethod
    def read_file(filepath: str):
        with open(filepath, 'r', encoding='utf-8') as json_file:
            json_object = json.load(json_file)
        logger.debug(f'Loaded json object from file: {json_object}')
        ModelRecipe(**json_object) # validate schema of the file
        ModelRecipe.recent_file_manager.add_file(filepath)
        return json_object
    
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


            

    