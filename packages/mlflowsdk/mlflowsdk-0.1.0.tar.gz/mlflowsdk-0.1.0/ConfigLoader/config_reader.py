import yaml
import os
from utils.logger import logger

class ConfigFileReader():

    """
    A class for reading and loading YAML configuration files.

    This class provides functionality to read a configuration file (config.yml)
    from the current working directory and parse it as YAML data.

    Attributes:
    config_file_path (str): The absolute path to the configuration file.
    """

    def __init__(self):
        self.config_file_path = os.path.join(os.getcwd(), 'config.yml')

    def read_config(self):

        """
        Read and parse the YAML configuration file.

        Returns:
            dict: The parsed configuration data from the YAML file.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            yaml.YAMLError: If there's an error parsing the YAML content.
        """
        try:
            # Read the YAML configuration file
            with open(self.config_file_path, 'r') as file:
                config_data = yaml.safe_load(file)
                logger.info("Successfully loaded the configurations for the mlflowsdk")
                return config_data
        except Exception as e:
            logger.error("Error reading configuration file: {}".format(e))
