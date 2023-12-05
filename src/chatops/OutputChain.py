import subprocess
import logging
import shutil
import json
import ast
import re
import os


class CodeProcessor:
    """
    Asynchronous class to process code responses and validate their format and content.
    """
    def __init__(self, output_location="output", output_project:str ="bot", overwrite_project = False, max_retries: int = 3, test:bool =True):
        """
        Initializes the CodeProcessor with a maximum number of retries and an output location.
        """

        self.test = test
        self.max_retries = max_retries
        self.output_location = output_location
        self.output_project = output_project
        self.overwrite_project = overwrite_project
        self.get_folder_instance = self.get_project_folder(overwrite_project)
        self.structured_list = []
        self.unstructured_list = []
        self.non_executables = [
            'yaml', 'json', 'xml', 'csv', 'toml', 'ini', 'conf',
            'html', 'md', 'rst',
            'css', 'scss', 'less',
            'txt', 'log', 'pdf', 'docx', 'xlsx', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'svg', 'mp3', 'mp4', 'avi', 'mov',
            'zip', 'tar', 'gz', 'markdown' , 'text', 'txt', 'tf', 'hcl' , 'terraform' , 'xml' , 'sql' ,'env'
        ]
        
        self.programming_languages = {
            'python'        : 'py',
            'javascript'    : 'js',
            'java'          : 'java',
            'yaml'          : 'yaml',
            'html'          : 'html',
            'css'           : 'css',
            'php'           : 'php',
            'typescript'    : 'ts',
            'c#'            : 'cs',
            'shell'         : 'sh',
            'ruby'          : 'rb',
            'go'            : 'go',
            'swift'         : 'swift',
            'kotlin'        : 'kt',
            'c++'           : 'cpp',
            'rust'          : 'rs',
            'scala'         : 'scala',
            'spark'         : 'py',
            'dart'          : 'dart',
            'lua'           : 'lua',
            'perl'          : 'pl',
            'r'             : 'r',
            'haskell'       : 'hs',
            'objective-c'   : 'm',
            'hcl'           : 'tf',
            'markdown'      : 'md',
            'docker'        : 'Dockerfile',
            'kubernetes'    : 'yaml',
            'powershell'    : 'ps1',
            'bash'          : 'sh',
            'makefile'      : 'mk',
            'sql'           : 'sql',
            'toml'          : 'toml',
            'conf'          : 'conf',
            'env'           : 'env',
            'csv'           : 'csv',
            'hcl'           : 'tf' , 
            'terraform'     : 'tf',
            'xml'           : 'xml',
            'json'          : 'json',
        }


    def extract_code_blocks(self, input_string):
        """
        Extract code blocks from the input string.
        """
        pattern = r'```(.*?)```'
        return re.findall(pattern, input_string, re.DOTALL)

    def extract_program_type(self, input_string):
        """
        Extract program types from the input string.
        """
        if isinstance(input_string, dict):
            return [value.get('app_type', '') for value in input_string.values()]
        elif isinstance(input_string, str):
            pattern = r'(\S+)\s*```[\s\S]*?```'
            return re.findall(pattern, input_string)

    def extract_path(self, input_string):
        """
        Extract paths from the input string.
        """
        if isinstance(input_string, dict):
            return [value.get('path', '') for value in input_string.values()]
        elif isinstance(input_string, str):
            pattern = r'#~(.*?)~'
            return re.findall(pattern, input_string)
        
    def object_handler(self,input)->bool:
        print(type(input))
        try:
            if isinstance(input,str):
                lit = dict(ast.literal_eval(input))
                self.structured_list.append(lit)
                return lit
            
            elif isinstance(input,dict):
                self.structured_list.append(input)

            elif isinstance(input,list):
                for i in input:
                    if isinstance(i,dict):
                        self.structured_list.append(input)
                    else:
                        self.unstructured_list.append(input)
            else:
                raise IOError ('unknown input format for object handler')


        except Exception as e:
            try:
                json = json.loads(input)
                self.structured_list.append(json)
                return json
            except:
                self.unstructured_list.append(input)
                return input



    def parse_code_blocks(self, input_data):
        if isinstance(input_data,str):
            pattern = r'({.+?}})'
            matches = re.findall(pattern, input_data, re.DOTALL)
            result = [self.object_handler(match) for match in matches]
            return result
            #return True
        else:
            result = self.object_handler(input_data)
            
            return result





    def get_project_folder(self, overwrite=False):
        """
        Get the project folder path based on the version.
        """
        latest_version = self.get_latest_version(overwrite)
        return f"{self.output_location}/{self.output_project}_v{latest_version}"

    def get_latest_version(self, overwrite=False):
        """
        Find the latest version number for the project.
        """
        version = 1
        while os.path.exists(f"{self.output_location}/{self.output_project}_v{version}"):
            version += 1

        # Subtract 1 from the version if overwrite is set to True
        if overwrite:
            version -= 1
        return version

    def handle_file_name(self,file_name):
        """
        Handle file name based on input data (either dictionary or string).
        """
        if isinstance(file_name, dict):

            file_name = re.sub(r'[^\w\s.-]', '_', file_name)
            file_name = next(iter(file_name))

        elif isinstance(file_name, str):
            file_name = re.sub(r'[^\w\s.-]', '_', file_name)
            pattern = re.compile(r'(\.\w+)+$')
            result = pattern.sub(r'\1', file_name)
            return result

    def save_code_to_file(self, key, app_type, code_content, file_path: str = ""):
        """
        Save code content to a file based on the key, app_type, and code_content.
        """
        output_folder = self.get_folder_instance

        if file_path and file_path != '.':
            output_folder = os.path.join(output_folder, file_path)

        file_extension = self.programming_languages.get(app_type.lower(), 'txt')
        file_name = os.path.join(output_folder, self.handle_file_name(f"{key}.{file_extension}"))

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(file_name, 'w') as file:
            file.write(code_content)



    def execute_code_blocks(self, code_dict, output_file:str = None, output_app_type:str = None, Structured:str = True):
        """
        Execute code blocks using subprocess and return the results.
        """
        if Structured == False or isinstance(code_dict, str):
            # save output unstructured folder #
            unstruct_key = 0 
            for i in code_dict:
                file_key =f'unstructured_file_{str(unstruct_key)}'
                self.save_code_to_file(file_key, 'text', i, file_path='unstructured')
                unstruct_key+=1

        if (output_file is None and output_app_type is not None) or (output_file is not None and output_app_type is None):
            raise ValueError("Both output_file and output_app_type must be provided together when passed")


        results = {}

        for key, value in code_dict.items():
            app_type = value['app_type']
            code_content = value['response']
            path = value['path']
            result = {'request': code_content, 'result': '', 'status': '', 'app_type': app_type, 'path': path}


            # Check if the app_type is in the list of languages to save directly
            if app_type.lower() in self.non_executables or self.test:
                # Save code directly without execution
                self.save_code_to_file(key, app_type, code_content,file_path=path)
                result['status'] = 'saved_directly'

            else:
                # Run the code using subprocess
                try:
                    process = subprocess.run([app_type, '-c', code_content], capture_output=True, text=True, check=True)
                    result['result'] = process.stdout.strip()
                    result['status'] = 'completed'
                    

                    # Save code to file if execution is successful
                    if result['status'] == 'completed':
                        
                        if output_file == None:
                            self.save_code_to_file(key, app_type, code_content,file_path=path)
                        else :
                            self.save_code_to_file(output_file, output_app_type, code_content,file_path=path)

                except subprocess.CalledProcessError as e:
                    result['status'] = 'failed'
                    result['result'] = f"Error executing code: {e.stderr.strip()}"

                except FileNotFoundError:
                    # Handle the case where the programming language is not installed
                    result['status'] = 'language_not_installed'
                    result['result'] = f"Error: {app_type} is not installed."

            results[key] = result

        return json.dumps(results, indent=4)
    
'''
# Sample Usage #

input_string = '''
{'requirements.txt': {'response': """
pyspark==3.1.2
""", 'status': 'pending_validation', 'result': '', 'app_type':'text' , 'path':'test2'}}
'''

processor = CodeProcessor()
code_dict_from_string = processor.parse_code_blocks(input_string)
for i in processor.structured_list:
    result_from_string = processor.execute_code_blocks(i,Structured=False)
    print(result_from_string)


'''