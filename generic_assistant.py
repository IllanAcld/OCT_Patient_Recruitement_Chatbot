import os
import time
import openai
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["api_key"])

headers = {
    "authorization": st.secrets["api_key"],
    "content-type": "application/json"
}

thread = client.beta.threads.create()

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def pretty_print(messages):
    responses = []
    for m in messages:
        if m.role == "assistant":
            responses.append(m.content[0].text.value)
    return "\n".join(responses)


st.title("Patient Recruitment :mag:")

# Description for PDF Analyzer
st.markdown("""
    This assistant is your dedicated resource for ensuring compliance of patient recruitment materials with country-specific regulations. Here's what you can do:
    - :file_folder: **Analyze your file** to verify compliance with local regulations.
    - :globe_with_meridians: **Check country-specific translation needs** to ensure effective communication.
    - :clipboard: Receive a **detailed compliance report** for specified documents and countries, covering aspects like Branding/Logo Requirements, Photo Inclusion, Study Medication Name Requirements, and more.
    - :mag_right: **Explore various document scenarios** and prepare your recruitment materials to meet all necessary legal standards.

    Simply upload your document and specify the country below, and let the assistant provide you with a comprehensive compliance analysis.

""")

country_options = [
    "Argentina", "Australia", "Austria", "Belgium", "Brazil",
    "Canada", "China", "Czech Republic", "Denmark", "France",
    "Germany", "Greece", "Hungary", "India", "Israel",
    "Italy", "Japan", "Malaysia", "Mexico", "Netherlands",
    "New Zealand", "Poland", "Republic of Korea (South Korea)",
    "South Africa", "Spain", "Sweden", "Taiwan", "Turkey",
    "United Kingdom", "United States" ]


uploaded_file = st.file_uploader("Upload your file", type=["pdf", "docx", "xlsx", "csv"])
user_query = st.selectbox("Select the target country for regulation comparison", country_options)

if uploaded_file is not None and user_query:
    with st.spinner('Analyzing file...'):
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            file_response = client.files.create(
                file=open(temp_file_path, "rb"),
                purpose="assistants",
            )
            assistant = client.beta.assistants.update(
                'asst_VUjrHpXJmP7nxSyrrThQ9xVH',
                file_ids=[file_response.id],
            )
            thread = client.beta.threads.create()
            run = submit_message('asst_VUjrHpXJmP7nxSyrrThQ9xVH', thread, user_query)
            run = wait_on_run(run, thread)
            response_messages = get_response(thread)
            response = pretty_print(response_messages)
            st.text_area("Response:", value=response, height=300)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Footer
st.markdown("---")
st.markdown("Developed with 💙 by Acolad")
