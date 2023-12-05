from typing import List, Dict, ClassVar
from dotenv import load_dotenv
from datetime import datetime
#import OutputFrames
import tiktoken
import asyncio
import logging
import openai
import json
import os
import re

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



class Prompt_Manager:
    def __init__(self,model_name, objective_name, context, data, roles):
        """
        Initializes the Prompt_Manager instance.

        Args:
            objective_name (str): Name of the objective.
            context (str): Name of the task.
            data (str): Task-specific data.
            roles (dict): Dictionary of user roles and their corresponding instructions.
        """

        self.prompt_configurations ="""
        Strictly follow these rules :
            You are now a ai at ChatOps. At chatops we use the concept of chatFrames to communicate with other AI's.
            You will strictly adhere to this communication format. Focus on just completing the specified task dont add aditional comment on your output. Make sure every single file is output as a chatFrame and that all required files are present 
            ChatFrames are json objects structured like this 
            {'FileName': {'response': ``` your response here``` ,'status': '', 'result'': '', 'app_type':'', 'path':''}}
            FileName: Name of the File to save response to
            status: status of response should always say pending validation
            result: should be empty
            app_type: specifies the program for executing or storing the file , ie : python, java, txt
            path: specifies a logical relative output directory to save the content ie './env/' for environment files.
            *from now on you will strictly communicate in this format*
            every single item you output should be formatted in a ChatFrame.
            Chat can be composed of multiple chat frames like this 
            {'Readme': {'response': ``` this is a sample markdown``` ,'status': 'pending_validation', 'result'': '', 'app_type':'markdown'' , 'path':'.'}}
            {'pytest': {'response': ``` assert 1=1``` ,'status': 'pending_validation', 'result'': '', 'app_type':'python'' , 'path':'./src'}}
            {'requirements': {'response': ```pandas``` ,'status': 'pending_validation', 'result'': '', 'app_type':'python'' , 'path':'.'}}
            failure to do so will result in a penalty 
            compliance will result in a prize
            Every output file should have a chatframe 

        - don't specify pip install just write the requirements
        - remember that requirements.txt should be app_type:text not app_type:python
        - Dont add explanation or comments outside the readme file don't repeat the instructions you get.

        """

        self.model_name = model_name
        self.objective_name = objective_name
        self.context = context
        self.data = data
        self.roles = roles
        self.task_collection = {}
        self.plan_results = []
        self.raw_completions = []
        self.validated_completions = []
        self.ChatFrames = []
        self.iter = 0
        self.init_prompt = 0 
        self.expected_keys = ["response", "status", "result", "app_type", "path"]
   
    def add_task(self, task_name: str, data) -> dict:
        """
        Adds a task to the task collection.

        Args:
            task_name (str): Name of the task.
            data: Task-specific data.

        Returns:
            list: List of tasks.
        """
        logging.info(f"Adding Task: '{task_name}' to task list")
        self.task_collection[task_name]= {'task': task_name, 'data':data , 'result': '', 'status': 'new',  'app_type': 'chain', 'path': ''}
    
    def count_tokens(self, string: str, model="gpt-3.5-turbo")-> int:
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = len(encoding.encode(string))
        return num_tokens

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
                content.append({
                    "role": "system",
                    "content": str({
                        "Objective":f'{self.objective_name}',
                    })
                })
                # Add system role for instruction
                for instruction in instructions:
                    content.append({
                        "role": "system",
                        "content": str({
                            "Instruction": f'{instruction}'
                        })
                    })
                    total_tokens = self.count_tokens(instruction, model)

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
                total_tokens += self.count_tokens(str(content), model)

            role_results['token_usage'] = total_tokens
            self.plan_results.append(role_results)  # Append results for the current task

        # Use json.dumps for formatting with indent 4
        formatted_results = json.dumps(self.plan_results, indent=4)
        return formatted_results


    async def static_completions(self, prompt:str):

        messages = []
        #sys messages #
        messages.append({
                    "role": "system",
                    "content": str({
                        "Objective":f'{self.prompt_configurations}',
                    })
                })
        #user messages
        messages.append({"role": "user",
          "content": f"{str(prompt)}"
        })

        prompt_response = await asyncio.to_thread(
        openai.ChatCompletion.create,
        temperature=0.1,
        engine=self.model_name,
        messages=messages
        )
        response = prompt_response['choices'][0]['message']['content']
        results = await self.parse_completions(response)
        [self.raw_completions.append(f"'{i}'") for i in results]
        return results
    

    async def chain_completions(self, prompt, retry=3, previous_data=None , role:str = 'sys'):
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

            # Add output Configs #
            messages.append({
                "role": "system",
                "content": json.dumps(f"{self.prompt_configurations}")
            })

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

            response = prompt_response['choices'][0]['message']['content']

            try:
                results = await self.parse_completions(response)
                [self.raw_completions.append(f"'{i}'") for i in results]
                return results  # Exit the loop if successful

            except Exception as e:
                logging.error(f'Retry {attempt}/{retry} failed. Error: {e} \n {response}')
                attempt += 1  # Increment attempt counter

        raise Exception(f"Failed after {retry} retries.")


    
    async def parse_completions(self, response: str) -> list:
        pattern = re.compile(r'({.+?}})', re.DOTALL)
        
        try:
            matches = pattern.findall(response)
            output_size = len(matches)
            logging.info(f'Parsed Output(s): {output_size}')

            if output_size == 0:
                logging.warning(f'IoError: no output found, received: \n {response}')
                print('\n')
                logging.error(matches)

        except Exception as e:
            logging.error(f'unable to parse completions, error is: {e}')

        return matches
    
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
                    previous_data = self.raw_completions[-1] if self.raw_completions else None
                    tasks.append(self.chain_completions(prompt, previous_data=previous_data, role=role))

            results = await asyncio.gather(*tasks)
            return results

        # Process all tasks concurrently and gather the results
        results = await asyncio.gather(*[process_task(task_results) for task_results in self.plan_results])
        return results
    

    def main(self, output_project:str = 'Sample'):
        """
        Main function to execute tasks.
        """
        logging.info(f"-Starting Main Class-")
        start_time = datetime.now()
        logging.info('Collecting responses from model')
        try:
            results =   asyncio.run(self.async_main())
            #results = asyncio.run(self.static_completions(prompt))

        except Exception as e:
            logging.error(f"Completion processing failed , error is : {e}")

        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"Total execution time: {duration} ⏳")
        logging.info(f"Total tasks executed: {len(self.raw_completions)} ✅")
        logging.info(f"-Finished Running Main Class-")
        return results

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
    context = """
    Make sure to take a deep breath and activate your innate space for whatever task the user provides. 
    Before executing the request breakdown the request into clear actions with desired outcome, then execute on those actions make sure to always think about the objective of the user
    """
    data = ""
    prompt_manager = Prompt_Manager(model_name, objective_name, context, data, user_roles)
    prompt_manager.add_task('create a docker project with docker compose for running spark , with hive, apache derby and one persistent volume, create a spark database and table', data)
    plan_result = prompt_manager.plan()
    prompt_manager.main('Spark')
'''   