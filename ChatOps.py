import argparse
import json
import logging
import os
import subprocess
import sys
from configs.Get_Configs import Bootstrap, Loader, loader_context
from src.chatops.ChatChain import *
from src.chatops.OutputChain import *



class CLI:
    def __init__(self):
        self.init = Bootstrap()
        self.parser = argparse.ArgumentParser(description="Welcome to ChatOps!")
        self._add_arguments()
        user_roles = self.init.prompt_template
        self.prompt_manager = Prompt_Manager(self.init.model_name, self.args.context, [], "", user_roles)

    def _add_arguments(self):
        self.parser.add_argument(
            "--project_name",
            type=str,
            default="bot",
            help="The name of your project will be used to store the output of the prompt (optional) defaults to bot"
        )
        self.parser.add_argument(
            "--context",
            type=str,
            default="You are a helpful AI Assistant with extensive knowledge in programming, writing, and creative development.",
            help="Description: The Prompt Context"
        )

        self.parser.add_argument(
            "--tasks_and_data",
            nargs='+',
            default=["write a haiku about ChatOps, a prompt engineering framework path should be poems", "no data"],
            help="Pairs of task and data values. Example: "
                 "--tasks_and_data 'Task1' 'Data1' 'Task2' 'Data2'. "
                 "When a data file parameter is passed, all tasks will use the same data file. "
                 "For independent chains, you can pass data files here."
        )

        self.parser.add_argument(
            "--overwrite_project",
            type=bool,
            default=False,
            help="Flag to indicate whether to overwrite the project."
        )  

        self.parser.add_argument(
            "--data_file",
            type=str,
            default=None,
            help="Path to a file containing data values. When using this parameter, only one file can be passed for all tasks."
        )

        self.parser.add_argument(
            "--test",
            type=bool,
            default=False,
            help="If set to true, will try to execute the code provided by LLM"
        )
        self.args = self.parser.parse_args()

    def load_data_from_file(self, file_path):
        try:
            file_path = os.path.normpath(file_path)
            with open(file_path, 'r') as file:

                data = file.read()
                # wrap text to avoid errors when passing to llm
                data = f'"""{data}"""'

                # Assuming data values in the file
                return data
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            sys.exit(1)

    def load_tasks_and_data(self):
        for i in range(0, len(self.args.tasks_and_data), 2):
            task_name = self.args.tasks_and_data[i]
            data_or_file = self.args.tasks_and_data[i + 1] if i + 1 < len(self.args.tasks_and_data) else None

            if os.path.isfile(data_or_file):
                data = self.load_data_from_file(data_or_file)
            else:
                data = data_or_file

            self.prompt_manager.add_task(task_name, data)

    def main(self):
        with loader_context(message="Initializing...", timeout=0.1):
            if self.args.data_file is not None:
                self.load_tasks_and_data()
            else:
                if len(self.args.tasks_and_data) % 2 != 0:
                    logging.info("Error: Pairs of task and data values are required.")
                    sys.exit(1)

                self.load_tasks_and_data()

            plan_result = self.prompt_manager.plan()

        with loader_context(message="Processing output...", timeout=0.1):
            self.prompt_manager.main()
            processor = CodeProcessor(output_project= self.args.project_name)
            [processor.parse_code_blocks(i) for i in self.prompt_manager.raw_completions]
            
            for i in processor.structured_list:
                result_from_string = processor.execute_code_blocks(i)
            for i in processor.unstructured_list:
                result_from_string = processor.execute_code_blocks(i)




if __name__ == "__main__":

    cli = CLI()
    cli.main()
    
    #data = cli.load_data_from_file('./readme.md')
    '''user_roles = {
    "Techical Writter": [
        "You are a technical writter at chatops, its your job to produce amazing content. Always fact check whatever you write and don't make stuff up",
        "Make sure your content is coherent and all the content comes together nicely"
    ],

    "Quality Control": [
        "You are a QA specialist your job is to review the content generated previously and fix any issues as well as add improvements as needed"
    ],

}
    objective_name = "You are a helpful AI Assistant with extensive knowledge in programming, writting and creative development."
    context = """
    Make sure to take a deep breath and activate your innate space for whatever task the user provides. 
    Before executing the request breakdown the request into clear actions with desired outcome, then execute on those actions make sure to always think about the objective of the user
    """
    data = ""
    prompt_manager = Prompt_Manager(model_name, objective_name, context, data, user_roles)
    prompt_manager.add_task('create a docker project with docker compose for running spark , with hive, apache derby and one persistent volume, create a spark database and table', data)
    plan_result = prompt_manager.plan()
    prompt_manager.main('Spark')
           
    processor = CodeProcessor(output_project="Spark")
    [processor.parse_code_blocks(i) for i in prompt_manager.raw_completions]
    for i in processor.structured_list:
        result_from_string = processor.execute_code_blocks(i)
    for i in processor.unstructured_list:
        result_from_string = processor.execute_code_blocks(i)
    logging.info('Tearing down build')'''


