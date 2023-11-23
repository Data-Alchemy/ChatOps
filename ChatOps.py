import os
import sys
import argparse
from dotenv import load_dotenv
from src.chatops.ChatChain import *
from src.chatops.OutputChain import *
from configs.Get_Configs import Bootstrap

class CLI:
    def __init__(self):
        self.init = Bootstrap()
        self.parser = argparse.ArgumentParser(description="Your script description")
        self.parser.add_argument("--objective_name", default="You are a helpful AI Assistant with extensive knowledge in programming, writing, and creative development.")
        self.parser.add_argument("--tasks_and_data", nargs='+', default=[], help="Pairs of task and data values. Example: --tasks_and_data 'Task1' 'Data1' 'Task2' 'Data2'")
        self.parser.add_argument("--output_index", type=int, help="Index of the output to process. If not provided, processes the last output by default.")
        self.parser.add_argument("--overwrite_project", type=bool, default=False, help="Flag to indicate whether to overwrite the project.")

        self.args = self.parser.parse_args()


    def process_output(self, prompt_manager, output_index=None):
        if output_index is None:
            _, output = list(prompt_manager.tmp.items())[-1]
        else:
            try:
                _, output = list(prompt_manager.tmp.items())[output_index]
            except IndexError:
                logging.error(f"Invalid output index {output_index}. Processing the last output by default.")
                _, output = list(prompt_manager.tmp.items())[-1]

        processor = CodeProcessor(output_location=self.init.output_folder, overwrite_project=self.args.overwrite_project)
        code_blocks = processor.parse_code_blocks(output)
        logging.info(code_blocks)
        execution_results = processor.execute_code_blocks(code_blocks)
        logging.info(execution_results)

    def main(self):
        #logging.info(self.init.cli_logo)
        user_roles = self.init.prompt_template
        if len(self.args.tasks_and_data) % 2 != 0:
            logging.info("Error: Pairs of task and data values are required.")
            sys.exit(1)

        prompt_manager = Prompt_Manager(self.init.model_name, self.args.objective_name, [], "", user_roles)

        for i in range(0, len(self.args.tasks_and_data), 2):
            task_name = self.args.tasks_and_data[i]
            data = self.args.tasks_and_data[i + 1] if i + 1 < len(self.args.tasks_and_data) else None
            prompt_manager.add_task(task_name, data)

        plan_result = prompt_manager.plan()
        prompt_manager.main()

        self.process_output(prompt_manager, output_index=self.args.output_index)

if __name__ == "__main__":
    cli = CLI()
    cli.main()
