"""
Takes in an image of a recipe as input
Uses Gemini to output a JSON file containing the recipe
"""

import sys
import os
from pathlib import Path
import json
import argparse
import tkinter as tk
from tkinter import filedialog

from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from PIL import Image
from dotenv import load_dotenv

# Constants
TEMP_OUTPUT_FILE = "output_filename.txt"
DEBUG = False
DEBUG_DUMMY_OUTPUT = {
    "title": "Roast Beef Sandwich",
    "time": None,
    "serving size": None,
    "ingredients": ["thing 1", "thing 2", "thing 3", "thing 4"],
    "directions": ["step 1", "step 2"],
    "description": "A very good meaty sandwich"
}

# Load variables from the .env file into the system environment
load_dotenv()

# Start Functions

# Provides a GUI for a user to select an image file
def get_img_path():
    # Initialize tkinter and hide the main root window
    root = tk.Tk()
    root.withdraw()

    # Open the file selection window
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )

    # Close the hidden root window completely
    root.destroy()
    print(f"filepath is {file_path}")
    return file_path

# Define the JSON schema using Pydantic
class RecipeSchema(BaseModel):
    title: str = Field(description="The title of the recipe")
    time: Optional[str] = Field(description="The amount of time the recipe takes, if it is present")
    serving_size: Optional[str] = Field(alias="serving size", description="The serving size or number of servings, if present")
    ingredients: List[str] = Field(description="An array containing all the ingredients for the recipe")
    directions: List[str] = Field(description="An array containing the step-by-step directions for the recipe")
    description: Optional[str] = Field(description="Any longer description that is provided in the recipe")

# If the Gemini API does not return the expected response, prints out error informtaion
def validate_response(response):
    if response.parsed is None:
        print("--- DEBUGGING INFO ---")
        print(f"prompt feedback is: {response.prompt_feedback}")

        # 1. Check the raw text (if any was generated)
        try:
            print(f"Raw Model Output: {response.text}")
        except ValueError:
            print("Raw Output: [No Text Returned]")

        # 2. Check the finish reason
        if response.candidates:
            candidate = response.candidates[0]
            print(f"Finish Reason: {candidate.finish_reason}")

            # 3. Check for safety blocks
            if candidate.finish_reason == "SAFETY":
                print("Safety Ratings:")
                for rating in candidate.safety_ratings:
                    print(f" - {rating.category}: {rating.probability}")
        else:
            print("No candidates returned from the model.")

# Sends a prompt to the Gemini API, using the provided image as input
# Outputs Json data containing the extracted recipe
def extract_recipe_to_json(image_path: str):
    # Load image for processing
    img = Image.open(image_path)
    prompt = """
    Extract the recipe information from this image or images. 
    Format the output as a JSON object with the following fields: 
    title, time, serving size, ingredients, directions, and description.
    Ensure all ingredients and directions are separated into lists.
    """
    current_temp = 1.0
    for attempt in range(2):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[img, prompt],
            config={
                "response_mime_type": "application/json",
                "response_schema": RecipeSchema,
                "temperature": current_temp
            },
        )

        if response.candidates and response.candidates[0].finish_reason == 4: # recitation
            print('prompt failed due to recitation')
            current_temp += 0.2
            prompt = f'{prompt} \n\n Please summarize or rephrase the output to avoid direct quotes.'
            continue

            
        # The SDK automatically parses the response into the Pydantic model
        #print(response.text)
        validate_response(response)
        return response.parsed

# End Functions
# Start script
parser = argparse.ArgumentParser(description='Send an image of a recipe to an AI model, output the recipe in a JSON file')
parser.add_argument('-d', '--debug', action='store_true', help='supply dummy data instead of using an AI model')
parser.add_argument('-i', '--input', help='input image file. If none is supplied you will choose a file')
parser.add_argument('-o', '--output', help='output file directory. If none is provided, will use a default location')
args = parser.parse_args()

print()
DEBUG = bool(args.debug)
OUTPUT_DIR = args.output
if DEBUG:
    print('debug mode enabled')
if not OUTPUT_DIR:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(ROOT_DIR, 'ai_output')
if args.input:
    print('input provided: ', args.input)
    img_path = args.input
else:
    img_path = get_img_path()

# Validate that the image file exists
p = Path(img_path)
if not p.is_file():
    print("The input img file was not found")
    sys.exit()

# The client gets the API key from the environment variable `GEMINI_API_KEY`
client = genai.Client()

"""
for m in client.models.list():
    for action in m.supported_actions:
        if action == "generateContent":
            print(m.name)

print("gemma info")
model_info = client.models.get(model="gemma-3-12b-it")
print(model_info)
"""

#recipe = None #extract_recipe_to_json(img_path)
# output json in a JSON file
print()
if not DEBUG:
    print("starting ai prompt")
    recipe = extract_recipe_to_json(img_path)
    print("finished ai prompt")

    output = recipe.model_dump(by_alias=True)
else:
    output = DEBUG_DUMMY_OUTPUT
title = output["title"]
title_normalized = title.replace(" ", "_").lower()
filepath = os.path.join(OUTPUT_DIR, f'{title_normalized}.json')  #f"ai_json_output{os.sep}{title_normalized}.json"
print("writing output to File")
with open(filepath, "w") as json_file:
    json.dump(output, json_file, indent=4)
print("finished writing output to file")

# write temp file containing the name of the output file. For use by the batch script
temp_file_full_path = os.path.join(OUTPUT_DIR, TEMP_OUTPUT_FILE)
with open(temp_file_full_path, "w") as temp_file:
    temp_file.write(filepath)
