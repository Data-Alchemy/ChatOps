import asyncio
import concurrent.futures
import logging
import json
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict
import tiktoken
import openai
from dotenv import load_dotenv


# Get the absolute path to the .env file using the current script's directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'env', 'llm.env'))

# Load Environment file
load_dotenv(env_path)



azure_openai_key = os.getenv("azure_openai_key")
azure_openai_endpoint = os.getenv("azure_openai_endpoint")
azure_openai_api_version = os.getenv("azure_openai_api_version")
azure_openai_api_type = os.getenv("azure_openai_api_type")
support_email = os.getenv("support_email")
model_name = os.getenv("model_name")
openai.api_base = azure_openai_endpoint
openai.api_key = azure_openai_key
openai.api_version = azure_openai_api_version
openai.api_type = azure_openai_api_type

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')


class Item(BaseModel):
    name: str


class Task(BaseModel):
    name: str
    items: List[Item]
    metadata: dict


class Objective(BaseModel):
    name: str
    objective: str  # High-level objective
    tasks: Dict[str, List[str]]  # Change tasks to a dictionary
    data: str  # Add a data attribute for the task-specific data


class RoleTask(BaseModel):
    role: str
    instructions: List[str]


class Prompt_Manager:
    def __init__(self,model_name, objective_name, task_name, data, roles):
        """
        Initializes the Prompt_Manager instance.

        Args:
            objective_name (str): Name of the objective.
            task_name (str): Name of the task.
            data (str): Task-specific data.
            roles (dict): Dictionary of user roles and their corresponding instructions.
        """

        self.prompt_configurations ="""
        Strictly follow these rules :
        - Always generate a folder structure comment on line one of your output in this format #~Folder_Name:Microsoft/Compute~ where the first section is the Program and the second is the usage
        - Always generate a file name as a comment at the top of your output based on what the request was using this format #~File_Name:Hello_World~
        - *The #~Folder_Name:~ and #~File_Name~ should be placed before each initial ``` and should be added for every code section that needs to be saved to a file
        - *Always wrap your code output with ``` ```
        - Always specify the programming language right after ``` for example: ```python
        - *when writting markdown files put everything inside ``` ``` code wrapper for example ```markdown ```. Don't add any other ``` for sections inside the markdown instead use ` `
        - Dont specify file extensions
        - don't specify pip install just write the requirements
        - remember that requirements.txt should be ```text not ```python
        - Dont add explanation or comments outside the readme file don't repeat the instructions you get.

        """
        self.model_name = model_name
        self.objective_name = objective_name
        self.task_name = task_name
        self.data = data
        self.roles = roles
        self.task_collection = {}
        self.plan_results = []
        self.completions = []
        self.tmp = {}
        self.iter = 0
        self.init_prompt = 0 

    def add_task(self, task_name: str, data) -> list:
        """
        Adds a task to the task collection.

        Args:
            task_name (str): Name of the task.
            data: Task-specific data.

        Returns:
            list: List of tasks.
        """
        logging.info(f"Adding Task: '{task_name}' to task list")
        self.task_collection[task_name] = data

    def num_tokens_from_string(self, string: str, encoding) -> int:
        """
        Calculates the number of tokens in a given string.

        Args:
            string (str): Input string.
            encoding: Encoding method.

        Returns:
            int: Number of tokens.
        """
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def count_tokens(self, text, encoding):
        """
        Counts the number of tokens in the given text.

        Args:
            text: Input text.
            encoding: Encoding method.

        Returns:
            int: Number of tokens.
        """
        return self.num_tokens_from_string(text, encoding)

    def plan(self, model="gpt-3.5-turbo"):
        """
        Plans the execution of tasks.

        Args:
            model (str): OpenAI model to use.

        Returns:
            str: Formatted results.
        """
        # List to store results for each task
        for task, data in self.task_collection.items():
            logging.info(f"Objective: {self.objective_name}")
            logging.info(f" -Executing Task: {task}")
            role_results = {}
            total_tokens = 0
            for role, instructions in self.roles.items():
                content = []
                logging.info(f"  - Executing Task as Role: {role}")
                # Add system role for instruction
                for instruction in instructions:
                    content.append({
                        "role": "system",
                        "content": str({
                            "Instruction": f'{instruction}'
                        })
                    })
                    total_tokens = self.count_tokens(str(instruction), tiktoken.encoding_for_model(model))

                # Add user role for task
                content.append({
                    "role": "user",
                    "content": str({
                        "Task": task,
                        "Data": data,  # Use the data parameter here
                        "Role": role
                    })
                })

                role_results[role] = content
                total_tokens += self.count_tokens(str(content), tiktoken.encoding_for_model(model))

            # Add system role for objective
            role_results["system"] = [{
                "role": "system",
                "content": str({
                    "Objective": self.objective_name
                })
            }]
            total_tokens += self.count_tokens(str(self.objective_name), tiktoken.encoding_for_model(model))
            role_results['token_usage'] = total_tokens

            self.plan_results.append(role_results)  # Append results for the current task

        # Use json.dumps for formatting with indent 4
        formatted_results = json.dumps(self.plan_results, indent=4)
        return formatted_results

    async def chain_completions(self, prompt, retry=3, previous_data=None):
        """
        Chains completions asynchronously.

        Args:
            prompt: Input prompt.
            retry (int): Number of retries.
            previous_data: Previous completion data.

        Raises:
            Exception: Raised after reaching the maximum number of retries.
        """
        attempt = 0
        while attempt <= retry:
            messages = prompt

            
            #if attempt == 0 and self.init_prompt == 0:
            # Add output Configs #
            messages.append({
                "role": "system",
                "content": json.dumps(f"{self.prompt_configurations}")
            })


            self.init_prompt +=1

            if previous_data:
                messages.append({
                    "role": "system",
                    "content": json.dumps(f"Use the output from the previous completion: {previous_data} as your starting point for completing your task. Make changes in place ")
                })

            prompt_response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                temperature=0.1,
                engine=self.model_name,
                messages=messages
            )

            try:
                output = prompt_response['choices'][0]['message']['content']
                self.completions.append(output)

                task_name = self.iter
                self.tmp[task_name] = output
                self.iter +=1
                print(output)
                return output
            except Exception as e:
                logging.error(f'Retry {attempt}/{retry} failed. Error: {e}')
                attempt += 1

        raise Exception(f"Failed after {retry} retries.")

    async def async_main(self):
        """
        Asynchronous main function to process tasks concurrently.
        """
        async def process_task(task_results):
            tasks = []
            for role, content in task_results.items():
                if role != 'token_usage':
                    self.init_prompt = 0
                    prompt = content
                    previous_data = self.completions[-1] if self.completions else None

                    # Append the coroutine to the list, not the result of the coroutine
                    tasks.append(self.chain_completions(prompt, previous_data=previous_data))

            # Await all tasks concurrently and gather the results
            results = await asyncio.gather(*tasks)
            return results

        # Process all tasks concurrently and gather the results
        results = await asyncio.gather(*[process_task(task_results) for task_results in self.plan_results])
        return results

    def main(self):
        """
        Main function to execute tasks.
        """
        logging.info(f"-Starting Main Class-")
        start_time = datetime.now()
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self.async_main())
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"Total execution time: {duration} ⏳")
        logging.info(f"Total tasks executed: {len(self.tmp)} ✅")
        logging.info(f"-Finished Running Main Class-")

'''
# Example usage:
if __name__ == "__main__":
    user_roles = {
    "Techical Writter": [
        "You are a technical writter at chatops, its your job to produce amazing content. Always fact check whatever you write and don't make stuff up",
        "Make sure your content is coherent and all the content comes together nicely"
    ],

    "Quality Control": [
        "You are a QA specialist your job is to review the content generated previously and fix any issues as well as add improvements as needed"
    ],

}


    objective_name = "You are a helpful AI Assistant with extensive knowledge in programming, writting and creative development."
    task_name = """
    Make sure to take a deep breath and activate your innate space for whatever task the user provides. 
    Before executing the request breakdown the request into clear actions with desired outcome, then execute on those actions make sure to always think about the objective of the user
    """
    data = ""

    prompt_manager = Prompt_Manager(model_name, objective_name, task_name, data, user_roles)
    data = """

    """
    prompt_manager.add_task('write a markdown document for snowflake usage', data)
    # prompt_manager.add_task('create a vnet', '')

    # Example calls
    """result = prompt_manager.main()
    print("Execution Results:")
    for role_results in result:
        print(role_results)"""

    plan_result = prompt_manager.plan()
    # [print(i['Programmer']) for i in prompt_manager.plan_results]
    #print(plan_result)
    prompt_manager.main()
    [print(i) for k,i in prompt_manager.tmp.items()]
'''