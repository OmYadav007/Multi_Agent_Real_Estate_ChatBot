import os
from openai import AzureOpenAI
import base64
import constants
from agents import tenancy_faq,issue_detection  
import utility

def agent_router(user_input):
    try:
        system_prompt=""
        client, model = utility.get_client()
        classify_agent_prompt=constants.agent_classification_prompt
        gpt_message=[{"role":"system","content":classify_agent_prompt},
                    {"role":"user","content":f"Classify This use input and call appropriate function {user_input}"}]

        function_call_response = client.chat.completions.create(
                    model=model,
                    messages=gpt_message,
                    functions=constants.functions
                )
       
        choice = function_call_response.choices[0]                 
        message = choice.message                     
        function_arguments = message.function_call.arguments
        call_function_name=message.function_call.name


        print("this is the agent to call",function_arguments,call_function_name)
        if(call_function_name=="tenancy_faq_agent"):
            system_prompt=tenancy_faq.tenancy_faq_agent()
       
        elif(call_function_name=="issue_detection_agent"):
            system_prompt=issue_detection.issue_detection_agent()
           
        else:
            system_prompt=constants.default_sys_prompt

        return system_prompt
    except Exception as e:
        print("eXCEPTION agent called",e)

        return constants.default_sys_prompt