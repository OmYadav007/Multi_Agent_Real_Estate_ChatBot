import constants

def tenancy_faq_agent( ):
    system_prompt=constants.tenancy_faq_agent_prompt
    message_obj={"role":"system","content":system_prompt}
    
    return message_obj
