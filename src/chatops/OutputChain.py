
import subprocess
import logging
import shutil
import json
import re
import os


class CodeProcessor:
    """
    Asynchronous class to process code responses and validate their format and content.
    """
    def __init__(self, output_location="output", output_project:str ="bot", overwrite_project = False, max_retries: int = 3):
        """
        Initializes the CodeProcessor with a maximum number of retries and an output location.
        """
        self.setup_logging()
        self.max_retries = max_retries
        self.output_location = output_location
        self.output_project = output_project
        self.overwrite_project = overwrite_project
        self.get_folder_instance = self.get_project_folder(overwrite_project)
        self.non_executables = [
            'yaml', 'json', 'xml', 'csv', 'toml', 'ini', 'conf',
            'html', 'md', 'rst',
            'css', 'scss', 'less',
            'txt', 'log', 'pdf', 'docx', 'xlsx', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'svg', 'mp3', 'mp4', 'avi', 'mov',
            'zip', 'tar', 'gz', 'markdown' , 'text', 'txt', 'tf', 'hcl' , 'terraform' , 'xml' , 'sql'

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
            'xml'           : 'xml'
        }

    def setup_logging(self):
        """
        Placeholder for logging setup. You should implement this method based on your logging needs.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        pattern = r'(\S+)\s*```[\s\S]*?```'
        return re.findall(pattern, input_string)

    def extract_path(self, input_string):
        """
        Extract paths from the input string.
        """
        pattern = r'#~(.*?)~'
        return re.findall(pattern, input_string)

    def parse_code_blocks(self, input_string):
        """
        Parse code blocks from the input string and return them as a dictionary.
        The dictionary has the key from the 'File_Name' and a dictionary with 'app_type' and 'code_content'.
        """
        code_dict = {}
        code_pattern = r'```(\S+)\s*([\s\S]*?)```'
        file_name_pattern = r'~File_Name:(.*?)~'

        # Find all File_Name matches in the input_string
        file_name_matches = re.findall(file_name_pattern, input_string)

        # Find all code matches in the input_string
        code_matches = re.findall(code_pattern, input_string, re.DOTALL)

        for file_name, (app_type, code_content) in zip(file_name_matches, code_matches):
            code_dict[file_name] = {'app_type': app_type, 'code_content': code_content.strip()}

        return code_dict



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

    def save_code_to_file(self, key, app_type, code_content):
        """
        Save code content to a file based on the key, app_type, and code_content.
        """
        output_folder = self.get_folder_instance
        file_extension = self.programming_languages.get(app_type.lower(), 'txt')
        file_name = f"{output_folder}/{key}.{file_extension}"

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        with open(file_name, 'w') as file:
            file.write(code_content)


    def execute_code_blocks(self, code_dict):
        """
        Execute code blocks using subprocess and return the results.
        """
        results = {}

        for key, value in code_dict.items():
            app_type = value['app_type']
            code_content = value['code_content']
            result = {'code_executed': code_content, 'status': '', 'result': '', 'app_type': app_type}

            # Check if the app_type is in the list of languages to save directly
            if app_type.lower() in self.non_executables:
                # Save code directly without execution
                self.save_code_to_file(key, app_type, code_content)
                result['status'] = 'saved_directly'

            else:
                # Run the code using subprocess
                try:
                    process = subprocess.run([app_type, '-c', code_content], capture_output=True, text=True, check=True)
                    result['result'] = process.stdout.strip()
                    result['status'] = 'completed'

                    # Save code to file if execution is successful
                    if result['status'] == 'completed':
                        self.save_code_to_file(key, app_type, code_content)

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
input_string = """
Here is some text before the code block.
~File_Name:Hello_World~
```toml
console.log("Hello, World!");
```
~File_Name:Math2~
```powershell
(Invoke-WebRequest -Uri "https://www.google.com").Links.Href
```
```
~File_Name:Wikipedia~
```powershell
(Invoke-WebRequest -Uri "https://simple.wikipedia.org/wiki/Main_Page").Links.Href
```
~File_Name:javascript~
```shell
print(1+a)
```

"""

processor = CodeProcessor(output_location="output")
code_blocks = processor.parse_code_blocks(input_string)
print(code_blocks)
execution_results = processor.execute_code_blocks(code_blocks)
print(execution_results)'''
