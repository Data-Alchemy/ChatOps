import os
import json
import openai
import logging
from dotenv import load_dotenv


class Bootstrap:


    def __init__(self, prompt_template_file: str = 'prompt_roles.json', output_folder:str = 'outputs'):
        """
        A class for initializing ChatOps configurations and setting up credentials.

        Parameters:
        takes 2 input parameter
        - prompt_template_file (str): File path to the JSON file containing prompt templates (default is 'prompt_roles.json'). | 
        you can store as many templates as you want just call them by file name
        - output_folder (str): Folder location where to output code to
        
        - reads from 4 files :
            - ./env/azure.env (used to configure connectivity to azure cli)
            - ./env/llm.env   (used to configure connectivity to azure open ai)
            - ./env/git.env   (used to configure connectivity to git repo expects private_key.rsa)
            - ./cli.txt ( has chatops logo for cli)

        Attributes:
        - azure_openai_key (str): Azure OpenAI API key.
        - azure_openai_endpoint (str): Azure OpenAI API endpoint.
        - azure_openai_api_version (str): Azure OpenAI API version.
        - azure_openai_api_type (str): Azure OpenAI API type.
        - support_email (str): Support email address.
        - model_name (str): OpenAI model name.
        - prompt_template (dict): Loaded prompt templates.
        - output_folder (str): output_folder for code files

        Methods:
        - assert_not_empty(value): Asserts that the provided value is not empty and returns it.
        - load_config(file_path): Loads JSON configuration from the specified file path.

        Example usage:
        ```
        bootstrap_instance = Bootstrap()
        print(bootstrap_instance.azure_openai_key)
        print(bootstrap_instance.prompt_template)
        ```
        """
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'env', 'llm.env'))
        prompt_template = os.path.abspath(os.path.join(os.path.dirname(__file__), prompt_template_file))
        logo= os.path.abspath(os.path.join(os.path.dirname(__file__), 'cli.txt'))
        logo = open(logo,'r').read()
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')
        print('')
        print(logo)
        logging.info('Initializing Application')
        logging.info(' - Loading Configurations')
        
        # Load environment variables from .env file

        load_dotenv(env_path)
        self.output_folder = output_folder

        # Get credentials
        self.azure_openai_key = self.assert_not_empty(os.getenv("azure_openai_key"))
        self.azure_openai_endpoint = self.assert_not_empty(os.getenv("azure_openai_endpoint"))
        self.azure_openai_api_version = self.assert_not_empty(os.getenv("azure_openai_api_version"))
        self.azure_openai_api_type = self.assert_not_empty(os.getenv("azure_openai_api_type"))
        self.support_email = self.assert_not_empty(os.getenv("support_email"))
        self.model_name = self.assert_not_empty(os.getenv("model_name"))
        self.cli_logo = logo
        # Configure OpenAI credentials
        openai.api_base = self.azure_openai_endpoint
        openai.api_key = self.azure_openai_key
        openai.api_version = self.azure_openai_api_version
        openai.api_type = self.azure_openai_api_type

        # Load additional configurations
        self.prompt_template = self.load_config(prompt_template)
        logging.info(' - Finished Loading Configurations')

    def assert_not_empty(self, value):
        """
        Asserts that the provided value is not empty.

        Args:
        - value: Value to be checked.

        Returns:
        - value: The non-empty value.

        Raises:
        - AssertionError: If the value is empty.
        """
        assert value is not None and value.strip() != '', f"Environment variable cannot be empty: {value}"
        return value

    @staticmethod
    def load_config(file_path):
        """
        Loads JSON configuration from the specified file path.

        Args:
        - file_path (str): Path to the JSON file.

        Returns:
        - config (dict): Loaded JSON configuration.
        """
        with open(file_path, 'rb') as file:
            config = json.load(file)
        return config
