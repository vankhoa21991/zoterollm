import dotenv
dotenv.load_dotenv()
import os
import streamlit as st
from langchain import PromptTemplate
from streamlit_chat import message
from langchain.chains import RetrievalQA, LLMChain
from zoterollm.llm import LLModel
from zoterollm.create_vector_store import VectorStoreFAISS, VectorStoreChromab
from zoterollm.qa_chain import generate_response
st.set_page_config(page_title='Zotero chatbot')
st.header('Custom LLM Chatbot :robot_face:')

@st.cache_resource()
def load_llm():
    llmodel = LLModel()
    model = llmodel.load_llm_4bit(model_id='Llama-2-7b-chat-hf/', 
                                  hf_auth=None, 
                                  device='cuda:0')
    # model = llmodel.load_ctransformer()
    return model

@st.cache_resource()
def load_vector_store():
    vector_store = VectorStoreFAISS(output_dir=f"{os.environ['working_dir']}/vectordb/faiss")
    db = vector_store.load_vector_store()
    return db

def create_prompt_template():
    # prepare the template we will use when prompting the AI
    template = """Respond with "I will help you with your question using the information i have in my database." 
    Use the provided context to answer the user's question. If you don't know the answer, respond with "I do not know".
    Previous conversation: {past}
    Context: {context}
    Question: {question}
    My answer is:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question', 'past'])
    return prompt

def create_qa_chain():
    # load the llm, vector store, and the prompt
    llm = load_llm()
    db = load_vector_store()
    prompt = create_prompt_template()

    # create the qa_chain
    # retriever = db.as_retriever(search_kwargs={'k': 5})
    # qa_chain = RetrievalQA.from_chain_type(llm=llm,
    #                                        chain_type='stuff',
    #                                        retriever=retriever,
    #                                        return_source_documents=True,
    #                                        chain_type_kwargs={'prompt': prompt})
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return llm_chain, db

def get_user_input():
    input_text = st.text_input('Ask me anything you want to know!', "", key='input')
    return input_text

llm_chain, db = create_qa_chain()


# create empty lists for user queries and responses
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'source' not in st.session_state:
    st.session_state['source'] = []

# get the user query
user_input = get_user_input()
# print(user_input)

def search_context(query):
    docs = db.similarity_search(query, k=5)
    print(f"Query: {query}")
    print(f"Retrieved documents: {len(docs)}")
    for doc in docs:
        doc_details = doc.to_json()['kwargs']
        print("Source: ", doc_details['metadata']['source'])
        # print("Text: ", doc_details['page_content'], "\n")

    context = [doc.to_json()['kwargs']['page_content'] for doc in docs]
    context = "\n".join(context)
    source = set([doc.to_json()['kwargs']['metadata']['source'] for doc in docs])
    source = "\n".join(source)
    return context, source

past = ""
if user_input:
    # generate response to the user input
    context, source = search_context(user_input)
    response = llm_chain.run(question=user_input,
                             context=context,
                             past=past)

    # add the input and response to session state
    past = past + f"Question: {user_input}\nAnswer: {response}\n"
    st.session_state.past.append(user_input)
    st.session_state.source.append(source)
    st.session_state.generated.append(response)


# display conversaion history (if there is one)
if st.session_state['generated']:
    for i in range(len(st.session_state['generated']) -1, -1, -1):
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['source'][i], key=str(i)+'_source')
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
