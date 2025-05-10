import json
from aws_cdk import (
    Stack,
    Tags,
)
from constructs import Construct

class DeployModelStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load tags from configuration.json
        with open("resource_configuration.json", "r") as config_file:
            config = json.load(config_file)
            tags = config.get("tags", {})

        # Apply tags to the stack
        for key, value in tags.items():
            Tags.of(self).add(key, value)