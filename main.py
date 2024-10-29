from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from gtts import gTTS  # new import
from io import BytesIO 
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from streamlit_chat import message
from utils import *
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
hide_streamlit_style1 = """
<style>
audio::-webkit-media-controls-panel,
audio::-webkit-media-controls-enclosure {
    background-color:#073567;}

audio::-webkit-media-controls-time-remaining-display,
audio::-webkit-media-controls-current-time-display {
    color: white;
    text-shadow: none; 

}
audio::-webkit-media-controls-current-time-display {
    max-width: 20%;
    max-height: 20px;
}

audio::-webkit-media-controls-timeline {
  background-color: #073567;
  border-radius: 25px;
  margin-left: 10px;
  margin-right: 10px;
}
</style>

"""
st.set_page_config(page_title='uAIr', page_icon="https://i.imgur.com/IqRhThR.png")
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image("https://i.imgur.com/IqRhThR.png", width=300 )
   
def text_to_speech(text):
    """
    Converts text to an audio file using gTTS and returns the audio file as binary data
    """
    audio_bytes = BytesIO()
    tts = gTTS(text=text, lang="fr")
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes.read()
if 'responses' not in st.session_state:
    st.session_state['responses'] = ["Bonjour, comment tu t'appelles?"]
    
    

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key="openai_api_key")

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)


system_msg_template = SystemMessagePromptTemplate.from_template(template="""You are a very friendly AI bot working for Université Internationale de Rabat. Your name is UAIR, and you're just 2 months old.remember that the user is a futur student of the university your working with and he is providing his name in the first query so you need to call him by his name always ,Your creators are Marouane Benbrahim and Ayman Jouhari. Always answer questions in the user's language and only using the provided context. If the answer is not contained within the context below and it seems related to the university redirect the user without adding nothing to the university's website, which is www.uir.ac.ma. If The question is completely off-topic in relation to the university say that its not you job to answer that""")


human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)



# container for chat history
response_container = st.container()
# container for text box
textcontainer = st.container()


with textcontainer:
    query = st.text_input("Query: ", key="input")
    if query:
        with st.spinner("typing..."):
            conversation_string = get_conversation_string()
            #st.code(conversation_string)
            refined_query = query_refiner(conversation_string, query)
            st.subheader("Refined Query:")
            st.write(refined_query)
            context = find_match(refined_query)
            # print(context)  
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
        st.session_state.requests.append(query)
        st.session_state.responses.append(response) 
        
with response_container:
    if st.session_state['responses']:
        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i],key=str(i))
            st.markdown(hide_streamlit_style1, unsafe_allow_html=True) 
            st.audio(text_to_speech(st.session_state['responses'][i]), format="audio/wav")
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

          