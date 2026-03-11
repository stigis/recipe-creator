import logging
logger = logging.getLogger(__name__)

class APIKeyController:

    def __init__(self):
        self.view = None

    # open a view window for setting and testing the API key
    # called from the menu
    def open_view(self):
        print('user asked to set/test api keys')
    
    def get_help(self):
        print('user asked for help with api keys')

    # separated from the constructor so it can be called after the view has been created
    def set_view(self, view):
        self.view = view