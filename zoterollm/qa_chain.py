from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from zoterollm.llm import LLModel
from zoterollm.create_vector_store import VectorStoreFAISS, VectorStoreChromab
import time
from langchain.chains import LLMChain
def create_prompt_template():
    # prepare the template we will use when prompting the AI
    template = """Use the provided context to answer the user's question.
    If you don't know the answer, respond with "I do not know".

    Context: {context}
    Question: {question}
    Answer:
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question'])
    return prompt

def create_prompt_template2():
    # prepare the template we will use when prompting the AI
    template = """Respond with "I am {name} and I will help you with your question using the information i have in these context." 
    Use the provided context to answer the user's question. 
    If you don't know the answer, respond with "I do not know".
    Previous conversation: {past}
    Context: {context}
    Question: {question}
    My answer is:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question', 'name', 'past'])
    return prompt

def create_qa_chain(db, model):
    prompt = create_prompt_template()

    # create the qa_chain
    retriever = db.as_retriever(
        search_kwargs={'k': 2}
                                )
    qa_chain = RetrievalQA.from_chain_type(llm=model,
                                        chain_type='stuff',
                                        retriever=retriever,
                                        # return_source_documents=True,
                                        chain_type_kwargs={'prompt': prompt}
    )

    return qa_chain


def generate_response(query, qa_chain):
    return qa_chain({'query':query})['result'], qa_chain({'query':query})['source_documents']


if __name__ == "__main__":

    # test the code with a sample question
    query = "What is LLama 2 ?"
    llmodel = LLModel()
    # model = llmodel.load_llm(model_id='meta-llama/Llama-2-7b-chat-hf', hf_auth=None, device='cuda:0')
    model = llmodel.load_llm_4bit(model_id='/data/llm/Llama-2-7b-chat-hf/', hf_auth=None, device='cuda:0')
    # model = llmodel.load_ctransformer()
    vectordb = VectorStoreFAISS(output_dir="../vectordb/faiss")
    # vectordb = VectorStoreChromab(output_dir="../vectordb/chromab")
    db = vectordb.load_vector_store()

    qa_chain = create_qa_chain(db,model)


    # use basic prompt
    start = time.time()
    # response, source = generate_response(query=query, qa_chain=qa_chain)
    # # print(source)
    # print("Time taken: ", time.time()-start)

    # result = qa_chain.run(query)
    # print(result)

    docs = db.similarity_search(query, k=5)
    print(f"Query: {query}")
    print(f"Retrieved documents: {len(docs)}")
    for doc in docs:
        doc_details = doc.to_json()['kwargs']
        print("Source: ", doc_details['metadata']['source'])
        # print("Text: ", doc_details['page_content'], "\n")
    end = time.time()
    print("Time taken: ", end-start)

    # use prompt with name
    prompt_template = create_prompt_template2()
    # prompt = prompt_template.partial(name="Super chatbot")
    # qa_chain = RetrievalQA.from_chain_type(llm=model,
    #                                        chain_type='stuff',
    #                                        retriever=db.as_retriever(search_kwargs={'k': 5}),
    #                                        # return_source_documents=True,
    #                                        chain_type_kwargs={'prompt': prompt}
    #                                        )
    # qa_chain({'query': query})['result']

    # chain = prompt_template | model
    llm_chain = LLMChain(prompt=prompt_template, llm=model)
    context = [doc.to_json()['kwargs']['page_content'] for doc in docs]
    context = "\n".join(context)
    # response = chain.invoke({"question": query,
    #               "context": context,
    #               "name": "Super chatbot",
    #               'past': ""})


    response = llm_chain.run(question=query,
    						 context=context,
                             name="Super chatbot",
                             past="")
    print("Time taken: ", time.time() - start)
    #
    past = f"Question: {query}\nAnswer: {response}\n"

    query = "Can you give me some example of it?"

    # response = chain.invoke({"question": query,
    #                          "context": context,
    #                          "name": "Super chatbot",
    #                          'past': ''})
    response = llm_chain.run(question=query,
                                context=context,
                                name="Super chatbot",
                                past=past)


