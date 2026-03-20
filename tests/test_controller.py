import unittest
from controllers.controller import Controller
from unittest.mock import patch, MagicMock

@patch('controllers.controller.View')
@patch('controllers.controller.ModelRecipe')
class TestController(unittest.TestCase):
    def test_controller_open_file(self, mock_model: MagicMock, mock_view: MagicMock):
        controller = Controller()
        mock_model.read_file.return_value = {"a": 1}
        #print(mock_model)
        #print(mock_view)
        controller.open_file(file_path='fake_file.json')

        mock_model.read_file.assert_called_once_with('fake_file.json')
        # use mock_view.return_value to get the view instance created by the controller
        mock_view.return_value.load_json.assert_called_once()

    def test_save(self):
        # TODO test save function
        pass