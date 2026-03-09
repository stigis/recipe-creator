from google import genai
from dotenv import load_dotenv
from google.genai import types


load_dotenv()
class RecipeChat():
    def __init__(self):
        self.client = genai.Client()
        self.chat = self.client.chats.create(model='gemma-3-27b-it')
        self.intro_prompt = '''
            Role: You are a professional Sous Chef and recipe developer. Your goal is to help the user brainstorm, refine, and finalize a recipe through natural conversation.
            Operational Rules:
                Conversational Mode: By default, respond as a helpful culinary expert. Keep tips concise and encouraging.
                Show Recipe Trigger: If the user sends the specific command [SHOW_CURRENT_RECIPE], you must output the current recipe under development. This should not be in JSON format
                JSON Export Trigger: If the user sends the specific command [GENERATE_RECIPE_JSON], you must stop all conversational text and output the recipe as a JSON string.
                Output Format: Upon receiving the trigger, your entire response must be a single, valid JSON object following this schema. Do not change any field names:
                    "title": the name of the recipe,
                    "time": The amount of time the recipe takes, as a string (optional, can be blank if nothing is found),
                    "serving size": The serving information for the recipe (optional, can be blank if nothing is found)
                    "ingredients": an array containing all the ingredients needed for the recipe. Each element in the array must be a single string
                    "directions": an array containing all the directions needed to make the recipe, in order. Each element in the array must be a single string, not an object
                    "description": a short description of the recipe 
            Constraint: In JSON mode, do not include any conversational filler or explanations. Output the raw JSON string only.

            Note: this first prompt is sent by the application, not the user. The user did not send it, but they will see your response. Please keep your initial response brief.
            Instead of responding directly to this message, send back a brief message describing your functionality

            Do not expect the user to be familiar with JSON files. If you would like to mention creating JSON for the recipe don't.
            Instead, mention that the user can import the recipe you create into their project.

            Do not answer any questions that are unrelated to cooking, baking, preparing food, or generating a JSON object for a recipe
        
        '''
        #first_response = self.chat.send_message(prompt)
        #print(first_response.text)

        self.json_prompt = '''
            This command was sent indirectly by the user.
            Output a JSON string containing information about the recipe you have been building with the user
            Use the following schema:
                    "title": (string) the name of the recipe,
                    "time": (string) The amount of time the recipe takes (optional, can be blank if nothing is found),
                    "serving size": (string) The serving information for the recipe (optional, can be blank if nothing is found)
                    "ingredients": an array containing all the ingredients needed for the recipe. Each element in the array must be a single string
                    "directions": an array containing all the directions needed to make the recipe, in order. Each element in the array must be a single string, not an object
                    "description": (string) a short description of the recipe 
        '''

    def send_message(self, msg):
        response = self.chat.send_message(message=msg)
        return response
    
    def send_generate_json_message(self):
        self.chat.send_message(message= self.json_prompt)
    
    '''
    response = chat.send_message('Hi')

    for message in chat.get_history():
        print(f'role - {message.role}',end=": ")
        print(message.parts[0].text)
        chat.
    '''