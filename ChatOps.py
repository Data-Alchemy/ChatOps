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
        self.prompt_manager = Prompt_Manager(self.init.model_name, self.args.objective_name, [], "", user_roles)

    def _add_arguments(self):
        self.parser.add_argument(
            "--project_name",
            type=str,
            default="bot",
            help="The name of your project will be used to store the output of the prompt (optional) defaults to bot"
        )
        self.parser.add_argument(
            "--objective_name",
            type=str,
            default="You are a helpful AI Assistant with extensive knowledge in programming, writing, and creative development.",
            help="Description: Your AI assistant's objective."
        )
        self.parser.add_argument(
            "--tasks_and_data",
            nargs='+',
            default=[],
            help="Pairs of task and data values. Example: "
                 "--tasks_and_data 'Task1' 'Data1' 'Task2' 'Data2'. "
                 "When a data file parameter is passed, all tasks will use the same data file. "
                 "For independent chains, you can pass data files here."
        )
        self.parser.add_argument(
            "--output_index",
            type=str,
            default=None,
            help="Index of the output to process. If not provided, processes the last output by default."
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
            "--no_testing",
            type=bool,
            default=False,
            help="If set to true, will output results from LLM without trying to execute the code."
        )
        self.parser.add_argument(
            "--output_override",
            nargs='+',
            default=[None, None],
            help="When passed, can override LLM file output rules and specify file name and application. "
                 "Both file name and application must be passed together. "
                 "Application is used for running code; passing 'python' will execute code as a Python script."
                 " Example: --output_override 'hello_world.py' 'python'"
        )
        self.args = self.parser.parse_args()

    def parse_output_override(self, output_override):
        if len(output_override) != 2:
            raise ValueError("Output override must contain both output file and app type.")
        
        output_file, output_app_type = output_override
        return output_file, output_app_type

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

            # Parse output_override and pass to process_output
            output_override = self.parse_output_override(self.args.output_override)
            self.process_output(
                output_index=self.args.output_index,
                output_override=output_override
            )

    def load_data_from_file(self, file_path):
        try:
            file_path = os.path.normpath(file_path)
            with open(file_path, 'r') as file:
                data = file.read()
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
                if len(data) <1 or data == None :
                    raise FileNotFoundError(f"{data_or_file} does not exist or is empty")
            else:
                data = data_or_file
            print('---------------------------------------------',data)
            self.prompt_manager.add_task(task_name, data)

    def process_output(self, output_index=None, output_override=None):
        outputs = list(self.prompt_manager.tmp.items())

        if str(output_index).lower() == "all":
            for _, output in outputs:
                self._process_output(output, output_override=output_override)
        elif output_index is not None:
            try:
                _, output = outputs[output_index]
            except IndexError:
                logging.error(f"Invalid output index {output_index}. Processing the last output by default.")
                _, output = outputs[-1]
            self._process_output(output, output_override=output_override)
        else:
            for _, output in outputs:
                self._process_output(output, output_override=output_override)

    def _process_output(self, output, output_override=None):
        processor = CodeProcessor(
            output_project=self.args.project_name,
            output_location=self.init.output_folder,
            overwrite_project=self.args.overwrite_project,
            no_test=self.args.no_testing
        )

        # Pass output_override to the execute_code_blocks method
        code_blocks = processor.parse_code_blocks(output)
        logging.info(code_blocks)
        print('---' , output_override[0],output_override[1])
        execution_results = processor.execute_code_blocks(code_blocks,output_file=output_override[0] ,output_app_type= output_override[1])
        logging.info(execution_results)

if __name__ == "__main__":
    cli = CLI()
    cli.main()
