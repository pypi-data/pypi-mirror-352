from typing import Annotated, List
import os
import json
from jinja2 import Environment, FileSystemLoader
from litellm import AllMessageValues, completion
from pydantic import BaseModel, Field, conlist

from .util.messages import system_message


class MemoryFilter:
    def __init__(self, completion_model: str):
        self.completion_model = completion_model
        # Set up Jinja environment
        template_dir = os.path.join(os.path.dirname(__file__), "prompts")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))


    def filter_relevant_memories(self,messages: List[AllMessageValues], memories: List[str]) -> List[bool]:
        """
        Filters memories based on their relevance to the request.

        Args:
            request (ChatCompletionRequest): The request containing the query.
            memories (List[str]): A list of memory strings to filter.

        Returns:
            List[int]: Indices of relevant memories.
        """

        class RelevanceResponse(BaseModel):
            relevance_list: Annotated[list[bool], conlist(item_type=bool, min_length=len(memories), max_length=len(memories))]
            reasoning: str



                # Load and render the template
        template = self.jinja_env.get_template("memory_relevance.jinja")
        prompt = template.render(messages=messages, memories=memories)

        # Call the completion API
        resp = completion(
            model=self.completion_model,
            messages=[system_message(prompt)] + messages,
            response_format=RelevanceResponse
        )

        # Parse the response
        response_content: str = resp.choices[0].message.content # type: ignore
        parsed_response = RelevanceResponse.model_validate(json.loads(response_content))

        return parsed_response.relevance_list




