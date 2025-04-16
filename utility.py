import os
from openai import AzureOpenAI
import base64
import constants
from agents import tenancy_faq,issue_detection  
from dotenv import load_dotenv
from typing import List, Dict

def remove_system_prompts(messages: List[Dict[str, str]]) -> None:
    """
    Remove all dictionaries with role 'system' from the messages list, in place.

    Args:
        messages: List of message dicts, each expected to have a 'role' key.
    """
    messages[:] = [m for m in messages if m.get("role") != "system"]


def get_client():
    """
    Initialize and return an AzureOpenAI client configured for GPT-4o-Mini.

    Returns:
        tuple: (AzureOpenAI client instance, model_name str)

    Raises:
        RuntimeError: If the client cannot be initialized.
    """
    try:
        load_dotenv()  
        endpoint = "https://gptdeployment9200789913.openai.azure.com/"
        model_name = "gpt-4o-mini"
        api_version = "2024-12-01-preview"
        subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
        if not subscription_key:
            raise RuntimeError("AZURE_SUBSCRIPTION_KEY not set")

        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=subscription_key,
        )
        return client, model_name
    except Exception as e:
        raise RuntimeError(f"Failed to initialize AzureOpenAI client: {e}")

def encode_image(image_bytes):
    """
    Encode raw image bytes into a base64 string.

    Args:
        image_bytes (bytes): Raw image data.

    Returns:
        str or None: Base64-encoded string, or None if encoding fails.
    """
    try:
        return base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error encoding image bytes: {e}")
    return None

def decode_image(base64_string):
  """
  Decodes a base64 encoded string back into image bytes.

  Args:
    base64_string: The base64 encoded string representing the image.

  Returns:
    bytes: The original image bytes.s
  """
  try:
    image_bytes = base64.b64decode(base64_string)
    return image_bytes
  except Exception as e:
    print(f"Error decoding base64 string: {e}")
    return None




def call_agent(user_input):
    """
    Classify the user's input via GPT-4o-Mini and dispatch to the appropriate agent function.

    Args:
        user_input (str): The raw input text from the user.

    Returns:
        str: The response from the selected agent.

    Raises:
        RuntimeError: If the OpenAI call fails or no valid function call is returned.
        ValueError: If the function name returned is unrecognized.
    """
    try:
        client, model = get_client()
        messages = [
            {"role": "system", "content": constants.agent_classification_prompt},
            {"role": "user", "content": f"Classify this user input and call the appropriate function: {user_input}"}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            functions=constants.functions
        )
    except Exception as e:
        raise RuntimeError(f"Error during OpenAI function call: {e}")

    choice = response.choices[0].message
    func_call = getattr(choice, "function_call", None)
    if not func_call:
        raise RuntimeError("No function_call returned from classification model")

    func_name = func_call["name"]
    args = func_call.get("arguments", {})
    try:
        if func_name == "tenancy_faq_agent":
            return tenancy_faq.tenancy_faq_agent(args["query"])
        elif func_name == "issue_detection_agent":
            return issue_detection.issue_detection_agent(args["query"])
        else:
            raise ValueError(f"Unrecognized function name: {func_name}")
    except KeyError as e:
        raise RuntimeError(f"Missing required argument in function call: {e}")
