import logging
from controllers.controller import Controller

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # clear the log file at the start
    with open('recipe_viewer_app.log', mode= 'w') as f:
        pass
    
    file_handler = logging.FileHandler('recipe_viewer_app.log', mode = 'a')
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])
    logger.info('Starting Application...')
    controller = Controller()
    controller.main()
    logger.info('Finished running Controller. Ending Application...')