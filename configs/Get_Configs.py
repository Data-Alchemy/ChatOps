import os
import sys
import json
import curses
import openai
import logging
from queue import Queue
from itertools import cycle
from time import sleep, time
from dotenv import load_dotenv
from contextlib import contextmanager
from threading import Thread, Event





class Bootstrap:


    def __init__(self, prompt_template_file: str = 'prompt_roles.json', output_folder: str = 'outputs', disable_logging: bool = False):
        """
        A class for initializing ChatOps configurations and setting up credentials.

        Parameters:
        takes 3 input parameters
        - prompt_template_file (str): File path to the JSON file containing prompt templates (default is 'prompt_roles.json'). | 
        you can store as many templates as you want just call them by file name
        - output_folder (str): Folder location where to output code to
        - disable_logging (Bool): If specified will not display info logs
        
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
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')

        if disable_logging:
            logging.disable(logging.CRITICAL)
        
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'env', 'llm.env'))
        prompt_template = os.path.abspath(os.path.join(os.path.dirname(__file__), prompt_template_file))
        logo = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cli.txt')),'r')
        logo = logo.read()
        # Configure logging

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


class LoaderContext:
    def __enter__(self):
        if not hasattr(LoaderContext, 'stdscr'):
            curses.initscr()
            curses.curs_set(0)  # Hide the cursor
            curses.start_color()

            for i in range(1, 9):
                curses.init_pair(i, curses.COLOR_BLUE, curses.COLOR_BLACK)

            LoaderContext.stdscr = curses.initscr()

        return LoaderContext.stdscr

    def __exit__(self, exc_type, exc_value, tb):
        curses.endwin()

@contextmanager
def loader_context(message="Loading...", timeout=0.1):
    with LoaderContext() as stdscr:
        loader = Loader(stdscr, message, timeout)
        with loader:
            yield loader

        end_time = time()
        duration = end_time - loader.start_time
        loader.print_summary(duration)


class Loader:
    line_number = 1  # Class-level variable to track line number for each instance

    def __init__(self, stdscr, desc="Loading...", timeout=0.1):

        self.stdscr = stdscr
        self.desc = desc
        self.timeout = timeout
        self._thread = None
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.colors = [curses.COLOR_BLUE] * len(self.steps)
        self.done_event = Event()
        self.instance_line_number = Loader.line_number  # Instance-specific line number
        Loader.line_number += 2  # Increment class-level line number for the next instance
        self.last_iteration = False  # Flag to track if this is the last iteration
        self.duration = None  # Track the total duration
        self.done_displayed = False  # Flag to track if "Done!" has been displayed
        self.logo = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cli.txt')),'r').read()
        self.context_started = False

    def start(self):
        # Only start the context if it hasn't been started yet
        if not self.context_started:
            self._thread = Thread(target=self._animate, daemon=True)
            self._thread.start()
            self.context_started = True  # Set the flag to indicate the context has been started
        return self

    def _animate(self):
        # Display initial static text only once at the beginning
        if not getattr(self, 'initial_text_displayed', False):
            initial_static_text = self.logo
            self.stdscr.addstr(0, 0, initial_static_text, curses.A_BOLD)
            self.stdscr.refresh()
            self.initial_text_displayed = True

        # Print the static ASCII art
        self.stdscr.addstr(0, 0, initial_static_text, curses.A_BOLD)

        for i, c in enumerate(cycle(self.steps)):
            if self.done_event.is_set():
                break

            color_pair = (i % len(self.colors)) + 1

            # Get the length of the loader animation
            loader_length = len(f"{self.desc} {c}")

            # Clear only the loader animation portion of the line
            self.stdscr.addstr(self.instance_line_number + 7, 0, " " * loader_length)

            # Print the animated character for the current step
            self.stdscr.addstr(self.instance_line_number + 7, 0, f"{self.desc} {c}", curses.color_pair(color_pair))

            self.stdscr.refresh()
            sleep(self.timeout)

            # Restore the static ASCII art
            self.stdscr.addstr(0, 0, initial_static_text, curses.A_BOLD)

            # Check if done_event is set and break the loop
            if self.done_event.is_set():
                break

            # Check if this is the last iteration
            if i == len(self.steps) - 1:
                self.last_iteration = True

        # Ensure "Done!" is printed only once
        if self.last_iteration and not self.done_displayed:
            duration = time() - self.start_time
            self.print_summary(duration)
            self.done_displayed = True  # Set the flag to indicate that "Done!" has been displayed

    def stop(self):
        # Clear the animation line
        self.stdscr.addstr(self.instance_line_number, 0, " " * curses.COLS)
        self.stdscr.refresh()
        self.done_event.set()

    def __enter__(self):
        self.start_time = time()  # Record the start time
        return self.start()

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()

    def print_summary(self, duration=None):
        if duration is not None:
            # Clear the animation line
            self.stdscr.addstr(self.instance_line_number + 7, 0, " " * curses.COLS)

            # Prefix the original message with "Done" and print the duration in blue
            message_with_duration = f"{self.desc} Done in {duration:.2f} seconds"
            color_pair = 1  # You can adjust the color pair as needed
            self.stdscr.addstr(self.instance_line_number + 7, 0, message_with_duration, curses.color_pair(color_pair))
            self.stdscr.refresh()

