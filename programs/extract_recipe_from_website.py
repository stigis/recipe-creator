from google import genai
from dotenv import load_dotenv

import sys
import os
import requests
from requests import Response
from bs4 import BeautifulSoup
import json
import re

load_dotenv()
if len(sys.argv) == 1:
    print("Usage: python pull_recipe.py <recipe_sub_url>")
    print("Example: python pull_recipe.py biscuit-recipe")
    sys.exit(1)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output", "website")
SITE_CONTENT_OUTPUT = os.path.join(OUTPUT_DIR, "site_content.txt")
JSON_OUTPUT = os.path.join(OUTPUT_DIR, "gemma_output.json")

recipe_url = sys.argv[1]
headers = {
    'User-Agent': 'Chrome/58.0.3029.110'
}

print('url is: ', recipe_url)
#sys.exit(1)
print('sending http request')
http_response: Response = requests.get(recipe_url, headers=headers)
print('received http response')
status_code = http_response.status_code
print(f'http status code is {status_code}')
if status_code != 200:
    print(f'expected status code 200, but was {status_code}')
    print('Response is...')
    print(http_response.text)
    sys.exit(1)

soup: BeautifulSoup = BeautifulSoup(http_response.text, 'html.parser')
visible_text = soup.get_text(separator=" ", strip=True)

# force data to be utf-8 encoding
print('encoding results...')
encoded_bytes = visible_text.encode(encoding = 'utf-8')
encoded_text = encoded_bytes.decode(encoding = 'utf-8')
print('finished encoding text...')
#print(encoded_text)

# write the site content to a file, ensure utf-8 encoding
with open(SITE_CONTENT_OUTPUT, 'w', encoding='utf-8') as file:
    print('writing site content to file')
    file.write(encoded_text)
    print('finished writing site content file')


#sys.exit(1)
#input_file = "C:\\Users\\stigi\\Documents\\python testing\\site_content.txt"
#with open(input_file, 'r', encoding='utf-8') as file:
#    recipe = file.read()
recipe = encoded_text
prompt = """
    The text below contains a Recipe. Please extract the recipe and output it in JSON format. USe the following fields:
        "title": the name of the recipe,
        "time": The amount of time the recipe takes, as a string (optional, can be null if nothing is found),
        "serving size": The serving information for the recipe (optional, can be null if nothing is found)
        "ingredients": an array containing all the ingredients needed for the recipe,
        "directions": an array containing all the directions needed to make the recipe, in order,
        "description": a description of the recipe (optional, can be null if nothing is found)
    """

whole_prompt = f"{prompt} \n\n {recipe}"
#whole_prompt = "What encoding do you use to read text?"

client = genai.Client()
print('sending prompt to ai...')
response = client.models.generate_content(
    model="gemma-3-27b-it",
    contents=[whole_prompt],
)
print('Response received from AI model')
match: re.Match = re.search(r'\{.*\}', response.text, re.DOTALL) # dotall matches newlines to .
if not match:
    print('Error: could not extract JSON object from AI Model Response')
    print('writing AI response to error file')
    with open('bad_response.txt', 'w', encoding='utf-8') as file:
        file.write(response.text)
        print('wrote error file. Exiting ...')
        sys.exit(1)

json_str = match.group(0)
json_object = json.loads(json_str)


print(response.text)
print('writing json output from the model')
with open(JSON_OUTPUT, 'w', encoding='utf-8') as json_file:
    json.dump(json_object, json_file, indent=4)
print('finished writing model output')

