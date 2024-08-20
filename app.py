#Essential Imports
from flask import Flask, request , jsonify , send_file
from flask_cors import CORS
import requests
import json
import os
import fitz
import zipfile
import io
import chromadb
from chromadb.config import Settings

#LangChain Imports
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage 
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings


app = Flask(__name__)
CORS(app)

#LLM Initialization
llm = ChatOpenAI(
    model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    temperature=0.5, #Higher temp = more random and creative output , Lower temp = more predictable and safe output
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="lm-studio",
    base_url="http://localhost:1234/v1"
)
            
# Embeddings Initialization
embeddings = FastEmbedEmbeddings()

#Text Splitter Initialization
#Prepare the text for embedding by splitting it into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000 ,
    chunk_overlap=100 , 
    length_function=len , 
    is_separator_regex=False
    )

#PDF to text converter function
def pdf_to_text_converter(file_like_object):
    # Assuming file_like_object is a file-like object (e.g., from request.files in Flask)
    # Convert the file-like object to bytes
    file_bytes = file_like_object.read()
    
    # Open the PDF from bytes
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_content = ""
    for page in doc:
        text_content += page.get_text()
    doc.close()
    return text_content


#Generate response with LLM
def generate_response_with_llm(pdf_content, user_prompt):
    prompt_template = PromptTemplate.from_template(
    """Read through this document: <Start of Document> {pdf} <End of Document>.
       After reading and understanding the text thoroughly, 
    I want you to answer this {prompt} as accurately as possible based on the given text"""
)
    formatted_prompt = prompt_template.format(pdf=pdf_content, prompt = user_prompt)
    
    messages = [
    (
        "system",
        "You are a helpful, smart, kind, and efficient AI assistant. You always fulfill the user's requests to the best of your ability.",
    ),
    
    ("human", formatted_prompt),
]
    AI_Response = llm.invoke(messages)

    return AI_Response.content
    
    
    
#Database Initialization
folder_path = "./db"
client = chromadb.PersistentClient(path=folder_path, settings=Settings(allow_reset=True))


#Store chat history locally + prompt to be used in the retrieval chain
chat_history = [] #local memory
raw_prompt = PromptTemplate.from_template("""
    You are a technical assistant who is good at searching and analyzing documents. If you do not have an answer from the provided information then say so. 
    {input}
    Context: {context}
    Answer:                                     
""")


# Send POST request to /v1/chat/completions endpoint of local server on LMStudio
@app.route("/ask_llm" , methods=["POST"])
def aiPost():
    print("Post /ask_llm called")
    data = request.get_json()
    query = data.get("query")
 
    print(f"Query: {query}")

    # Define the URL of your local server
    url = "http://localhost:1234/v1/chat/completions"

    # Define the headers for the POST request
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer lm-studio",
    }
    
    # Ensure that the query is a string
    if not isinstance(query, str):
        query = str(query)
    
   
    # Define the data for the POST request
    data = {
        "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        "messages": [
            {"role": "system", "content": "You are a Helpful Assistant who is able to read documents and provide in-depth analysis."},
            {"role": "user", "content": query},
        ],
        "temperature": 0.5,
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data)) #Convert data dictionary to JSON string

    # Parse the response
    response_data = response.json()

    # The assistant's reply can be extracted from the response
    response_answer = response_data['choices'][0]['message']['content']

    return response_answer



@app.route("/upload_documents", methods=["POST"])
def uploadDocuments():
    files = request.files.getlist('file')  # Get list of files
    responses = []

    for file in files:
        file_extension = os.path.splitext(file.filename)[1].lower()
        filename = file.filename  # Initialize filename variable
        
        if file_extension == '.pdf':
            pdf_filename = file.filename
            # SAVE pdf TO static/pdf FOLDER
            pdf_path = os.path.join('static/pdf/uploads', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            file.save(pdf_path)
            
            path = 'static/pdf/uploads/' + pdf_filename

            loader = PyMuPDFLoader(path)
            docs = loader.load_and_split()
            print(f"docs len = {len(docs)}")

            chunks = text_splitter.split_documents(docs)
            print(f"chunks len = {len(chunks)}")
        
        elif file_extension == '.txt':
            txt_filename = file.filename
            # SAVE txt TO static/txt FOLDER
            txt_path = os.path.join('static/txt/uploads', txt_filename)
            os.makedirs(os.path.dirname(txt_path), exist_ok=True)
            file.save(txt_path)
            
            path = 'static/txt/uploads/' + txt_filename

            loader = TextLoader(path)
            docs = loader.load()
            print(f"docs len = {len(docs)}")

            chunks = text_splitter.split_documents(docs)
            print(f"chunks len = {len(chunks)}")

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            client = client
        )

        response = {"filename": filename, "doc_len": len(docs), "chunk_len": len(chunks)}
        responses.append(response)
        os.remove(path)
        

    return {"status": "Successfully Uploaded", "files": responses}

@app.route("/ask_documents", methods=["POST"])
def askDocuments():
    data = request.get_json()
    query = data.get("query")
    
    print(f"Query: {query}")
    
    print("Loading Vector Store")

    print(f"Query: {query}")
    
    print("Loading Vector Store")
    vector_store = Chroma(client=client, embedding_function=embeddings)
    
    print("Creating chain")
    retriever = vector_store.as_retriever(
        search_type = "similarity_score_threshold",
        search_kwargs = {
            "k": 10, #return up to 10 documents that match the query
            "score_threshold": 0.1 #minimum similarity score to return a document
        },
    )
    
    retriever_prompt = ChatPromptTemplate.from_messages(
        [
        MessagesPlaceholder(variable_name = "chat_history"),
        ("human","{input}"),
        ("human","Given the above conversation, generate a search query to lookup relevant documents in order to get information relevant to the conversation",),
        ]
                                                        )
    
    history_aware_retriever = create_history_aware_retriever(
        llm = llm,
        retriever = retriever,
        prompt = retriever_prompt
        )
    
    document_chain = create_stuff_documents_chain(llm, raw_prompt)
    #chain = create_retrieval_chain(retriever, document_chain)
    
    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        document_chain,
    )
    
    
    result = retrieval_chain.invoke({"input" : query})
    print(result["answer"])
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=result["answer"]))
    
    response_answer = {"answer" : result["answer"]}
    
    return response_answer




@app.route('/batch_file_query', methods=['POST'])
def batch_file_query():
    try:
        print("Post /batch_file_query called")
        if 'user_prompt' not in request.form or 'uploaded_files' not in request.files:
            return jsonify({'error': 'Missing form data'}), 400

        user_prompt = request.form['user_prompt']
        uploaded_files = request.files.getlist('uploaded_files')

        if not uploaded_files:
            return jsonify({'error': 'No selected files'}), 400

        # In-memory bytes buffer for the zip file
        in_memory_zip = io.BytesIO()

        # Create a zip file in memory
        with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in uploaded_files:
                PDF_filename = file.filename
                pdf_content = pdf_to_text_converter(file)  # Assuming this function can take a file-like object
                response = generate_response_with_llm(pdf_content, user_prompt)
                response_filename = os.path.splitext(PDF_filename)[0] + "_response.txt"
                # Write the response to the zip file
                zf.writestr(response_filename, response)

        # Important: Move the pointer to the start of the BytesIO buffer before sending
        in_memory_zip.seek(0)

        # Send the in-memory zip file to the client
        return send_file(in_memory_zip, download_name="BatchQueryResponses.zip", as_attachment=True)

    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route("/clear_db", methods=["POST"])
def clear_db():
    client.reset()  # resets the database
    return {"status": "Database Cleared"}
    
      
   
    
if __name__ == "__main__":
    app.run()
    
