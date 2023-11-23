```
 ______     __  __     ______     ______   ______     ______   ______    
/\  ___\   /\ \_\ \   /\  __ \   /\__  _\ /\  __ \   /\  == \ /\  ___\   
\ \ \____  \ \  __ \  \ \  __ \  \/_/\ \/ \ \ \/\ \  \ \  _-/ \ \___  \  
 \ \_____\  \ \_\ \_\  \ \_\ \_\    \ \_\  \ \_____\  \ \_\    \/\_____\ 
  \/_____/   \/_/\/_/   \/_/\/_/     \/_/   \/_____/   \/_/     \/_____/ 
```                                                                        

# ChatOps: LLM Automation Framework

The ChatOps LLM Automation Framework is designed to operationalize the usage of Large Language Models (LLMs) by seamlessly integrating build, test, and deploy processes into a collaborative chat environment. This framework aims to streamline the development lifecycle, providing an efficient and automated workflow for planning, coding, testing, and deploying code using LLMs. ChatOps runs and tests your code before generating it to make sure it is functional.

## Advantages of ChatOps

1. **Operational Efficiency:**
   - Enhances the overall development lifecycle with an automated workflow for planning, coding, testing, and deploying code using LLMs.
   - By default any code generated for a specific ChatOps project will be stored in a versioned folder, everytime you re run your project it will generate a new version *( can be changed to overite = True for git managed versioning)*

2. **Simplified LLM Usage:**
   - Abstracts and simplifies complex processes in prompt engineering.
   - Features the innovative **Chain Planning**, enabling the simulation of chat messages without actual LLM dispatch and providing insightful token usage estimates.

3. **Lazy Evaluation for Enhanced Workflow:**
   - Implements lazy evaluation on tasks, allowing users to accumulate and visualize tasks concurrently.
   - Tasks are processed concurrently and asynchronously, optimizing the execution pipeline for increased efficiency.

4. **Contextual Task Execution with Prompt Roles:**
   - Utilizes **prompt roles** as contextual windows for tasks.
   - Allows execution of a single task by multiple contexts (programmer, QA, manager, etc.), fostering collaboration.
   - Iteratively works on specified tasks within a context, referred to as a **chain** by ChatOps, sharing output between phases.
## Table of Contents

- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [Plan Function](#plan-function)
- [Sample Usage](#sample-usage)
- [Enhancements](#enhancements)
- [Links](#links)

## Setup

To set up the ChatOps framework, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Data-Alchemy/ChatOps.git
   ```
2. Navigate to the project directory:
    ```bash
    cd chatops
    ```
3. Install Dependencies
    ```bash
    poetry install
    ```
4. Set up environment variables

    To configure the ChatOps credentials create a `llm.env` file in the project env folder and add the necessary environment variables. These variables are essential for connecting to the Azure OpenAI API and defining other configurations.

    ```dotenv
    # llm.env
    ```

    | Variable                    | Value                     | Explanation                          |
    |-----------------------------|--------------------------|---------------------------------------|
    | AZURE_OPENAI_KEY            | your_openai_key          | OpenAI API key for authentication.    |
    | AZURE_OPENAI_ENDPOINT       | your_openai_endpoint     | Endpoint URL for the OpenAI API.      |
    | AZURE_OPENAI_API_VERSION    | your_openai_api_version  | API version of the OpenAI service.    |
    | AZURE_OPENAI_API_TYPE       | your_openai_api_type     | Type of the OpenAI API being used.    |
    | SUPPORT_EMAIL               | support@example.com      | Email address for support.            |
    | MODEL_NAME                  | your_model_name          | Name of the specific model to use.    |


# Usage

## Key Terms in ChatOps

| Term                | Description                                    |
|---------------------|------------------------------------------------------|
| Chat Chains         | Sequential exchanges of messages in a conversational context, forming a chain of communication between participants. |
| Prompt Roles        | Assigned roles with specific responsibilities in a collaborative content generation framework, guiding individuals in their contribution tasks. |
| Chat Chain Planning | The strategic and organized process of planning and structuring conversational interactions within a chat system, often to achieve specific communication goals. |
| Shared Context Windows | Common reference points or informational frames that are accessible to multiple participants in a conversation, ensuring a consistent understanding of the context. |


Run the ChatOps framework using the main script ` poetry run ChatOps.py`. Here are the available command-line options:

- `--objective_name`: Set the name of the objective (default: "You are a helpful AI Assistant...").
- `--tasks_and_data`: Provide pairs of task and data values. tasks are assigned to prompt roles to complete. You can add several tasks at a time to a chain
- `--output_index`: Specify the index of the output to process. If not provided, processes the last output by default.
- `--overwrite_project`: Flag to indicate whether to overwrite the project (default: False).

# Contributing

Contributions are welcome! To contribute to the ChatOps framework, follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push the changes to your fork.
5. Create a pull request to the main repository.

# Up

Contributions are welcome! To contribute to the ChatOps framework, follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push the changes to your fork.
5. Create a pull request to the main repository.


# Upcoming Features

| Feature                              | Description                                                                                                                                                 |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Run inside Docker**                | Ensures better security by allowing the ChatOps Large Language Model (LLM) Automation Framework to run inside Docker containers.                                 |
| **Streamlit Front End**              | Introduces a streamlined user interface using Streamlit, a Python library to enhance the overall user experience.   |
| **API Mode for Task Management**     | - **Overview:** Introduce API-based triggering for tasks, providing a programmatic way to interact with and control the ChatOps framework.                              - **Key Benefits:** Enables automation, flexibility in task management, and seamless integration with other tools and systems.                                - **Implementation:** Integrates APIs, documents endpoints, implements security measures, and ensures scalability for future expansions.|


## Conclusion

These upcoming features are designed to elevate the ChatOps LLM Automation Framework, providing enhanced security, a more user-friendly interface through Streamlit, and advanced automation capabilities with the introduction of API mode. Stay tuned for these exciting developments that will further empower your experience with ChatOps.
