import unittest
from unittest.mock import MagicMock
from views.view import View
import time

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


class TestGui(unittest.TestCase):
    
    def setUp(self):
        self.mock_controller = MagicMock()
        self.main_view = View(controller=self.mock_controller)
        self.main_view.update()
        return super().setUp()
    
    def tearDown(self):
        self.main_view.destroy()
        return super().tearDown()
    
    def test_header_exists(self):
        header_frame = self.main_view.header_frame
        self.assertTrue(header_frame.winfo_exists())

        self.assertTrue(header_frame.title_entry.winfo_exists())
        self.assertTrue(header_frame.time_label.winfo_exists())
        self.assertTrue(header_frame.time_value.winfo_exists())
        self.assertTrue(header_frame.serve_label.winfo_exists())
        self.assertTrue(header_frame.serve_value.winfo_exists())
        self.assertTrue(header_frame.img_frame.winfo_exists())
        self.assertTrue(header_frame.image_button.winfo_exists())
        self.assertIsNone(header_frame.image_label)


        
        self.assertEqual(header_frame.time_label.cget('text'), 'Time:')
        self.assertEqual(header_frame.serve_label.cget('text'), 'Serves:')

    def test_autosize_entries(self):
        header_frame = self.main_view.header_frame
        time_entry = header_frame.time_value
        serve_entry = header_frame.serve_value
        self.main_view.update()
        def assert_entry_grows(entry):
            old_width = entry.winfo_width()
            for char in 'test entry autosize with a long string':
                #print(f'letter for keyrelease is: {char}')
                entry.focus_set() # the entry needs focus for the KeyRelease event to trigger the bound function
                entry.insert('end', char)
                entry._entry.event_generate('<KeyRelease>', keysym=char)
                entry.update()
            new_width = entry.winfo_width()
            self.assertGreater(new_width, old_width)
        
        assert_entry_grows(time_entry)
        assert_entry_grows(serve_entry)


    def test_remove_ingredients(self):
        # delete the 2nd ingredient, out of 3
        ingredients_frame = self.main_view.ingredients_frame
        to_delete = [(1, 2), (1, 1), (0, 1)] # (index to delete, size after)
        
        for index, expected_size in to_delete:
            ingredient = ingredients_frame.linked_list.get(index)['sub_frame']
            delete_button = ingredient.winfo_children()[2]
            delete_button.invoke()
            self.main_view.update()
            self.assertEqual(ingredients_frame.linked_list.size, expected_size)

    def test_remove_directions(self):
        directions_frame = self.main_view.directions_frame
        to_delete = [(1, 2), (1, 1), (0, 1)] # (index to delete, size after)

        for index, expected_size in to_delete:
            direction = directions_frame.direction_list[index]['sub_frame']
            delete_button = direction.winfo_children()[2]
            delete_button.invoke()
            self.main_view.update()
            self.assertEqual(len(directions_frame.direction_list), expected_size)

    def test_insert_ingredient(self):
        ingredients_frame = self.main_view.ingredients_frame
        ingredient = ingredients_frame.linked_list.get(1)['sub_frame']
        insert_button = ingredient.winfo_children()[3]
        insert_button.invoke()
        self.main_view.update()
        self.assertEqual(len(ingredients_frame.linked_list), 4)

        new_ingredient_entry = ingredients_frame.linked_list.get(2)['ingredient']
        new_ingredient_entry.insert('end','testing insert new ingredient')
        self.main_view.update()
        self.assertEqual(new_ingredient_entry.get(), 'Ingredienttesting insert new ingredient')

    def test_insert_direction(self):
        directions_frame = self.main_view.directions_frame
        direction = directions_frame.direction_list[1]['sub_frame']
        insert_button = direction.winfo_children()[3]
        insert_button.invoke()
        self.main_view.update()
        self.assertEqual(len(directions_frame.direction_list), 4)

        new_direction_text = directions_frame.direction_list[2]['direction']
        new_direction_text.insert('end', 'testing insert new direction step')
        third_direction_text = directions_frame.direction_list[2]['direction']
        self.main_view.update()
        self.assertEqual(third_direction_text.get('1.0', 'end-1c'), 'Steptesting insert new direction step')

    def test_load_json(self):
        self.main_view.menu_bar.file_menu.invoke('Open')
        self.mock_controller.open_file.assert_called_once()

        self.main_view.load_json(mock_json_data)
        header_frame = self.main_view.header_frame
        self.assertEqual(header_frame.get_title(), mock_json_data['title'])
        self.assertEqual(header_frame.get_serving(), mock_json_data['serving size'])
        self.assertEqual(header_frame.get_time(), mock_json_data['time'])
        self.assertEqual(self.main_view.description_frame.get_description(), mock_json_data['description'])

        self.assertEqual(self.main_view.ingredients_frame.get_ingredients(), mock_json_data['ingredients'])
        self.assertEqual(self.main_view.directions_frame.get_directions(), mock_json_data['directions'])



        



        




        
        