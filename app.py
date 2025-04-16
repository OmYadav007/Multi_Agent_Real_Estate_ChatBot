import streamlit as st
import utility
import constants
st.title("Multi-Agent Real Estate Assistant Chatbot")
import router_manager


if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role":"assistant","content":"Hi I am a Real Estate Assistant Chatbot, How can i help you"})

for msg in st.session_state.messages:
    if msg["role"].lower()=="system":
        pass
    else:
        with st.chat_message(msg["role"]):
            try:
                if isinstance(msg["content"], list):
                    for item in msg["content"]:
                        if item["type"] == "text":
                            st.markdown(item["text"])
                        elif item["type"] == "image_url":
                            
                            encoded_image_data = item["image_url"]["url"]
                            encoded_image_data_cleaned = encoded_image_data.split(",")[1]
                            decoded_image = utility.decode_image(encoded_image_data_cleaned)
                            st.image(decoded_image, use_column_width=True)
                else:
                    
                    st.markdown(msg["content"])
            except Exception as e:
                st.markdown("Error rendering message.")


uploaded_files = st.file_uploader("Upload property images (optional)",
                                  type=["png","jpg","jpeg"],
                                  accept_multiple_files=True)
user_input = st.chat_input("Ask me something about this property…")


if user_input:
    content_obj = []

    if user_input.strip():
        content_obj.append({"type": "text", "text": user_input})

    if uploaded_files:
        for uploaded_file in uploaded_files:
            image_bytes = uploaded_file.read()
            encoded_image = utility.encode_image(image_bytes)
            content_obj.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })


    entry = {"role": "user", "content": content_obj if content_obj else user_input}

    st.session_state.messages.append(entry)

    with st.chat_message("user"):
        if isinstance(entry["content"], list):
            for item in entry["content"]:
                if item["type"] == "text":
                    st.markdown(item["text"])
                elif item["type"] == "image_url":
                    image_data_cleaned = item["image_url"]["url"].split(",")[1]
                    decoded_image = utility.decode_image(image_data_cleaned)
                    st.image(decoded_image, use_column_width=True)
        else:
           
            st.markdown(entry["content"])

    
    agent_based_prompt=router_manager.agent_router(user_input)
    
    utility.remove_system_prompts(st.session_state.messages)
    print("removed existing system prompts and appended new one on agent change")
    
    st.session_state.messages.append(agent_based_prompt)


    # 5) Call GPT-like model
    with st.chat_message("assistant"):
        client, model = utility.get_client()
        payload = st.session_state.messages
        print(payload)
        # GPT call with streaming
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=payload,
                stream=True,
            )
            assistant_reply = st.write_stream(stream)
        except Exception as e:
            assistant_reply=st.markdown("YOU HAVE EXCEEDED THE API CALL LIMIT FOR FREE TIER , PLEASE WAIT FOR 60 SECONDS AND RETRY WITH SMALLER MESSAGE OR IMAGE")

    # 6) Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_reply
    })




