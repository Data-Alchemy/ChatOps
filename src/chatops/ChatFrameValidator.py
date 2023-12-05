
from datetime import datetime
from pydantic import BaseModel, ValidationError
from typing import List, Dict, ClassVar


class ChainValidator:
    class ChatFrameValidator(BaseModel):
        response: str
        status: str
        result: str
        app_type: str
        path: str

        expected_structure: ClassVar[Dict[str, str]] = {key: '' for key in __annotations__}

        Errors: ClassVar[bool] = False
        ErrorsList: ClassVar[List[Dict]] = []

        class Config:
            extra = 'forbid'  # Disallow extra keys

        @classmethod
        def __init_subclass__(cls, **kwargs):
            cls.expected_structure = {key: '' for key in cls.__annotations__}

        @classmethod
        def validate_dict_keys(cls, value, expected_keys:list =["response", "status", "result", "app_type", "path"]):
            if not isinstance(value, dict):
                cls.Errors = True
                cls.ErrorsList.append({"message": f"Responses must be structured as ChatFrames. ie: {cls.expected_structure}."})
                return {"message": f"Responses must be structured as ChatFrames. ie: {cls.expected_structure}."}

            try:
                # Pydantic will validate the dictionary keys and types
                model = cls(**value)
                return None  # No errors
            except ValidationError as e:
                # Extract error messages and format them
                error_messages = []
                unexpected_keys = cls.get_unexpected_keys(value)

                # Check for unexpected keys
                for key in unexpected_keys:
                    message = f"Output Error: Unexpected key: '{key}' is not a valid key. It must be removed."
                    error_messages.append(message)

                # Check for incorrect keys and suggest correct fields
                if expected_keys:
                    received_keys = list(value.keys())
                    incorrect_order = []
                    for expected_key, received_key in zip(expected_keys, received_keys):
                        if expected_key != received_key:
                            incorrect_order.append((expected_key, received_key))

                    for expected_key, received_key in incorrect_order:
                        message = f"Output Error: Incorrect key: '{received_key}' is not the correct field for this section. Did you mean '{expected_key}'?"
                        error_messages.append(message)

                cls.Errors = True
                cls.ErrorsList.append({
                    **value, 'status': 'structure_invalid', 'result': 'invalid', 'errors': error_messages
                })

                return {
                    **value, 'status': 'structure_invalid', 'result': 'invalid', 'errors': error_messages
                }

        @classmethod
        def get_unexpected_keys(cls, values):
            return set(values) - set(cls.__annotations__)

        @classmethod
        def get_errors(cls):
            return cls.ErrorsList

    class InstanceManager:
        def __init__(self, validator_class):
            self.validator_class = validator_class

        def process_instances(self, instances, expected_keys=None):
            results = []
            if isinstance(instances, dict):
                instances = [instances]  # Convert single dict to a list of dicts

            for instance in instances:
                instance_key = list(instance.keys())[0]
                instance_value = instance[instance_key]

                # Validate each instance and store the result
                error_response = self.validator_class.validate_dict_keys(instance_value, expected_keys)

                if not error_response:
                    # Update the status field for success
                    instance_value['status'] = 'structure_valid'
                    instance_value['result'] = 'in_progress'
                    results.append({instance_key: instance_value})

            return results

    def __init__(self, validator_class):
        self.validator_class = validator_class
        self.instance_manager = self.InstanceManager(validator_class)

    def process_instances(self, instances, expected_keys=None):
        self.ChatFrameValidator.Errors = False
        self.ChatFrameValidator.ErrorsList = []

        if not (isinstance(instances, dict) or isinstance(instances, list)):
            self.ChatFrameValidator.Errors = True
            self.ChatFrameValidator.ErrorsList.append({"message": f"Input must be a ChatFrame. ie: {{'FileName': {{'response': '', 'status': '', 'result': '', 'app_type': ''}}}} received output: {instances}"})
            return []

        results = self.instance_manager.process_instances(instances, expected_keys)

        return results