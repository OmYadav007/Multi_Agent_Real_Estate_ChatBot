import constants


def issue_detection_agent():
    
    system_prompt=constants.issue_detection_agent_prompt
    message_obj={"role":"system","content":system_prompt}

    return message_obj
