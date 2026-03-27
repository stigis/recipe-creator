'''
    Reads and writes a list of recently used files. This is stored as a json array of absolute filepaths
'''
import json
import os
from pathlib import Path
import re
from platformdirs import PlatformDirs
import constants
import logging
logger = logging.getLogger(__name__)

class RecentFileManager():
    MAX = 10

    def __init__(self):
        self.app_base = os.getenv('APPDATA')
        #self.app_directory = os.path.join(self.app_base, 'RecipeViewer')
        self.app_dirs = PlatformDirs(appname=constants.APP_NAME, appauthor=False, ensure_exists=True)
        self.data_dir = self.app_dirs.user_data_dir

        #logger.info(f'app dir for data is: {self.app_dirs.dat}')

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.recent_filepath = os.path.join(self.data_dir, 'opened_recently.json')
        self.recent_files = self.load_recents()

    def load_recents(self):
        if not os.path.exists(self.recent_filepath):
            logger.info('no recents file to load')
            return []
        try:
            with open(self.recent_filepath, 'r') as recents_file:
                recently_used = json.load(recents_file)
                return recently_used
        except json.JSONDecodeError:
            logger.error('error doing json decode on recents file')
            return []

    def add_file(self, filename):
        if filename:
            filename = str(filename) # ensure filepath is a str and not a Path
        if filename in self.recent_files:
            self.recent_files.remove(filename)

        self.recent_files.insert(0, filename) # add to the begining

        if len(self.recent_files) > RecentFileManager.MAX:
            self.recent_files.pop() # remove the least recently used file

        with open(self.recent_filepath, 'w') as file:
            json.dump(self.recent_files, file, indent=4)


