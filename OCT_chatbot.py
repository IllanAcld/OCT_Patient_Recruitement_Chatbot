import streamlit as st
import logging
import openai
from openai import OpenAI

client = OpenAI(api_key=st.secrets["api_key"])

headers = {
    "authorization": st.secrets["api_key"],
    "content-type": "application/json"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Upload an .xlsx file with an "assistants" purpose
file = client.files.create(
    file=open("C:\\Users\\knafoui\\Downloads\\Local Translation Requirements Data_231219.pdf", "rb"),
    purpose='assistants'
)

assistant = client.beta.assistants.create(
    instructions="You help users by analyzing specific requirements from your Excel file knowledge detailing country-specific translation needs for patient recruitment materials. It focuses on checking compliance with local regulations based on the columns such as Branding/Logo Requirements, Photo Inclusion, Study Medication Name Requirements, and more. When a document and a country are specified, it provides a detailed report on whether the document is compliant with local regulations, covering all aspects listed in the Excel columns.",
    model="gpt-4-turbo",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id]
)

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="I can not find in the PDF manual how the country you are referring to.",
  file_ids=[file.id]
)
def get_response(user_query):
    thread = openai.Thread.create(assistant_id=assistant.id)
    message = openai.ThreadMessage.create(
        thread_id=thread.id,
        role="user",
        content=user_query
    )
    # Assuming the assistant might use the file to retrieve information
    return message.choices[0].message['content']

def main():
    st.title('AI Assistant with Document Understanding')
    query = st.text_input("Ask something:")
    if st.button('Ask'):
        response = get_response(query)
        st.text(response)

if __name__ == "__main__":
    main()
