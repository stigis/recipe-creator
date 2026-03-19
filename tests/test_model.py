import unittest
from unittest.mock import patch, mock_open, call, MagicMock
from models.model import ModelRecipe
import json
from pathlib import Path

mock_json_data = {
    "title": "Roast Beef Sandwich",
    "time": "2 hours",
    "serving size": "1 large sandwich",
    "ingredients": ["2 slices of bread", "A few slices of roast beef", "tomato slices", "pickles"],
    "directions": [
        "put tomatoes on top of one slice of bread",
        "add pickles",
        "add the roast beef",
        "add the other slice of bread"
        ],
    "description": "a plain ol roast beef sandwich"
}

mock_json_str = json.dumps(mock_json_data)

class TestModel(unittest.TestCase):
    def setUp(self):
        return super().setUp()
    
    def tearDown(self):
        return super().tearDown()
    
    @patch('builtins.open', new_callable=mock_open, read_data= mock_json_str)
    def test_model_read_file(self, mock_open):
        recipe_json = ModelRecipe.read_file('fakepath.json')
        self.assertEqual(mock_open.call_count, 2) # how many times 'open' was used
        mock_open.assert_any_call('fakepath.json', 'r', encoding='utf-8')
        # assert a write call to the 'opened recently' file
        mock_open.assert_any_call(ModelRecipe.recent_file_manager.recent_filepath, 'w')
        
        self.assertEqual(mock_json_data['title'], recipe_json['title'])
        self.assertEqual(mock_json_data['time'], recipe_json['time'])
        self.assertEqual(mock_json_data['serving size'], recipe_json['serving size'])
        self.assertEqual(mock_json_data['ingredients'], recipe_json['ingredients'])
        self.assertEqual(mock_json_data['directions'], recipe_json['directions'])
        self.assertEqual(mock_json_data['description'], recipe_json['description'])
        # the model has added the key 'image ref' with the value None
        self.assertIsNone(recipe_json['image ref'])

    @patch('models.model.shutil.copy2')
    @patch('builtins.open', new_callable=mock_open)
    def test_model_save_file(self, mock_open: MagicMock, mock_copy: MagicMock):
        model = ModelRecipe(**mock_json_data)
        # confirm that the model added the image ref field
        self.assertIsNone(model.image_ref)
        model.save_file('fake_output.json')
        mock_open.assert_any_call('fake_output.json', 'w', encoding='utf-8')
        mock_open.assert_any_call(ModelRecipe.recent_file_manager.recent_filepath, 'w')

        mock_open.reset_mock()
        model.save_file('fake_output.json', temp_img_path='fake_image.jpg')
        mock_open.assert_any_call('fake_output.json', 'w', encoding='utf-8')
        mock_open.assert_any_call(ModelRecipe.recent_file_manager.recent_filepath, 'w')
        mock_copy.assert_called()

    def test_model_read_json_str(self):
        json_oject = ModelRecipe.read_json_str(mock_json_str)
        self.assertEqual(json_oject, mock_json_data)



