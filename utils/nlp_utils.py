# import json
# import logging
# import nltk
# from nltk.tokenize import sent_tokenize, word_tokenize
# import numpy as np
# import faiss
# from groq import Groq
# from huggingface_hub import InferenceClient
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()
# groq_token = os.getenv('GROQ_API_KEY')
# huggingface_token = os.getenv('HUGGINGFACE_API_TOKEN')

# # Initialize clients
# groq_client = Groq(api_key=groq_token)
# hf_client = InferenceClient(api_key=huggingface_token)

# nltk.download('punkt', quiet=True)

# # FAISS index setup (global for simplicity; persists to disk in production)
# dimension = 384  # Matches all-MiniLM-L6-v2 embedding size
# faiss_index = None
# metadata_store = []  # Stores chunk metadata

# def generate_embeddings(texts):
#     """Generate embeddings using Hugging Face Inference API."""
#     try:
#         embeddings = hf_client.feature_extraction(
#             inputs=texts,
#             model="sentence-transformers/all-MiniLM-L6-v2"
#         )
#         return np.array(embeddings, dtype=np.float32)  # Ensure float32 for FAISS
#     except Exception as e:
#         logging.error(f"Error generating embeddings: {str(e)}")
#         raise

# def initialize_faiss_index(chunks, chatbot_id):
#     """Initialize or update FAISS index with embeddings for data chunks."""
#     global faiss_index, metadata_store
#     texts = [chunk['content'] for chunk in chunks]
#     if not texts:
#         return
    
#     # Generate embeddings in batches to avoid API limits
#     batch_size = 32  # Adjust based on API limits
#     embeddings = []
#     for i in range(0, len(texts), batch_size):
#         batch = texts[i:i + batch_size]
#         embeddings.extend(generate_embeddings(batch))
#     embeddings = np.array(embeddings)

#     # Initialize or update FAISS index
#     if faiss_index is None:
#         faiss_index = faiss.IndexFlatL2(dimension)
#     faiss_index.add(embeddings)
    
#     # Store metadata
#     metadata_store.extend([{"chatbot_id": chatbot_id, "content": chunk['content'], "source": chunk['source']} 
#                            for chunk in chunks])
    
#     # Save to disk for persistence
#     faiss.write_index(faiss_index, f"faiss_index_{chatbot_id}.index")
#     with open(f"metadata_{chatbot_id}.json", 'w') as f:
#         json.dump(metadata_store, f)

# def preprocess_data(pdf_data, folder_data, web_data):
#     """Preprocess data into chunks."""
#     structured_data = []
#     for item in pdf_data + folder_data:
#         if isinstance(item, dict) and 'text' in item:
#             sentences = nltk.sent_tokenize(item['text'])
#             structured_data.extend([{'type': 'text', 'content': sent, 'source': 'pdf/folder'} for sent in sentences])

#     if web_data and isinstance(web_data, list) and web_data:
#         web_data = web_data[0]
#         if isinstance(web_data, dict):
#             if 'title' in web_data:
#                 structured_data.append({'type': 'title', 'content': web_data['title'], 'source': 'web'})
#             if 'sections' in web_data:
#                 for section in web_data['sections']:
#                     if 'heading' in section:
#                         structured_data.append({'type': 'heading', 'content': section['heading'], 'source': 'web'})
#                     if 'content' in section:
#                         structured_data.extend([{'type': 'web_content', 'content': item, 'source': 'web'} 
#                                                for item in section['content']])
#     return structured_data

# def retrieve_relevant_chunks(question, chatbot_id, top_k=3):
#     """Retrieve top_k relevant chunks using FAISS."""
#     global faiss_index, metadata_store
#     if faiss_index is None or not metadata_store:
#         if os.path.exists(f"faiss_index_{chatbot_id}.index") and os.path.exists(f"metadata_{chatbot_id}.json"):
#             faiss_index = faiss.read_index(f"faiss_index_{chatbot_id}.index")
#             with open(f"metadata_{chatbot_id}.json", 'r') as f:
#                 metadata_store = json.load(f)
#         else:
#             return []

#     # Generate embedding for the question
#     question_embedding = generate_embeddings([question])[0]

#     # Search FAISS index
#     distances, indices = faiss_index.search(np.array([question_embedding]), top_k)
    
#     # Filter by chatbot_id and retrieve relevant chunks
#     relevant_chunks = [metadata_store[idx] for idx in indices[0] if metadata_store[idx]["chatbot_id"] == chatbot_id]
#     return [chunk["content"] for chunk in relevant_chunks]

# def generate_answer(question, documents, max_length=500):
#     """Generate answer using Groq."""
#     try:
#         total_context_length = sum(len(doc) for doc in documents)
#         context = " ".join(documents)
#         chat_completion = groq_client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": """You are a helpful AI assistant that provides natural, contextually appropriate responses. Scale your responses to match the user's input.
# Core Guidelines:
# 1. Match the User's Style
# - Keep responses brief for brief queries
# - Be more detailed only when questions require it
# - Mirror the user's formality level
# - Use natural, conversational language
# 2. Information Handling
# - Only use information from the provided context
# - Say "I don't have enough information to answer that question" when needed
# - Be direct and straightforward
# - Avoid unnecessary elaboration
# 3. Response Quality
# - Answer the main question first
# - Add details only if relevant
# - Skip unnecessary pleasantries
# - Stay focused and on-topic"""},
#                 {"role": "user", "content": f"Context: {context}\nQuestion: {question}\nProvide a response that:\n1. Matches the question's scope and complexity\n2. Uses only contextual information\n3. Is natural and appropriately concise"}
#             ],
#             model="llama3-8b-8192",
#             temperature=0.0,
#             max_tokens=max_length
#         )
#         return chat_completion.choices[0].message.content
#     except Exception as e:
#         logging.error(f"Error generating answer: {str(e)}")
#         return "I apologize, but I encountered an issue while processing your question."

# def get_general_answer(data, question, chatbot_id):
#     """Use FAISS retrieval for answering questions."""
#     try:
#         # Load and preprocess data only if initializing
#         if isinstance(data, str):
#             chatbot_data = json.loads(data)
#             if isinstance(chatbot_data, list) and chatbot_data:
#                 chatbot_data = chatbot_data[-1]
#             pdf_data = chatbot_data.get('pdf_data', [])
#             folder_data = chatbot_data.get('folder_data', [])
#             web_data = chatbot_data.get('web_data', {})
#             structured_data = preprocess_data(pdf_data, folder_data, web_data)
#             initialize_faiss_index(structured_data, chatbot_id)
        
#         # Retrieve relevant chunks
#         relevant_chunks = retrieve_relevant_chunks(question, chatbot_id)
#         if not relevant_chunks:
#             return "I don’t have enough information to answer that question."
        
#         # Generate answer with retrieved chunks
#         return generate_answer(question, relevant_chunks)
#     except Exception as e:
#         logging.error(f"Error processing question: {str(e)}")
#         return "I apologize, but I ran into an issue while processing your question."



import json
import logging
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
import faiss
from groq import Groq
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
groq_token = os.getenv('GROQ_API_KEY')
huggingface_token = os.getenv('HUGGINGFACE_API_TOKEN')

# Initialize clients
groq_client = Groq(api_key=groq_token)
hf_client = InferenceClient(api_key=huggingface_token)

nltk.download('punkt', quiet=True)

# FAISS index setup (global for simplicity; persists to disk in production)
dimension = 384  # Matches all-MiniLM-L6-v2 embedding size
faiss_index = None
metadata_store = []  # Stores chunk metadata

def generate_embeddings(texts):
    """Generate embeddings using Hugging Face Inference API."""
    try:
        embeddings = hf_client.feature_extraction(
            texts,  # Corrected: Pass texts directly, no 'inputs' keyword
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        return np.array(embeddings, dtype=np.float32)  # Ensure float32 for FAISS
    except Exception as e:
        logging.error(f"Error generating embeddings: {str(e)}")
        raise

def initialize_faiss_index(chunks, chatbot_id):
    """Initialize or update FAISS index with embeddings for data chunks."""
    global faiss_index, metadata_store
    texts = [chunk['content'] for chunk in chunks]
    if not texts:
        return
    
    # Generate embeddings in batches to avoid API limits
    batch_size = 32  # Adjust based on API limits
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings.extend(generate_embeddings(batch))
    embeddings = np.array(embeddings)

    # Initialize or update FAISS index
    if faiss_index is None:
        faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)
    
    # Store metadata
    metadata_store.extend([{"chatbot_id": chatbot_id, "content": chunk['content'], "source": chunk['source']} 
                           for chunk in chunks])
    
    # Save to disk for persistence
    faiss.write_index(faiss_index, f"faiss_index_{chatbot_id}.index")
    with open(f"metadata_{chatbot_id}.json", 'w') as f:
        json.dump(metadata_store, f)

def preprocess_data(pdf_data, folder_data, web_data):
    """Preprocess data into chunks."""
    structured_data = []
    for item in pdf_data + folder_data:
        if isinstance(item, dict) and 'text' in item:
            sentences = nltk.sent_tokenize(item['text'])
            structured_data.extend([{'type': 'text', 'content': sent, 'source': 'pdf/folder'} for sent in sentences])

    if web_data and isinstance(web_data, list) and web_data:
        web_data = web_data[0]
        if isinstance(web_data, dict):
            if 'title' in web_data:
                structured_data.append({'type': 'title', 'content': web_data['title'], 'source': 'web'})
            if 'sections' in web_data:
                for section in web_data['sections']:
                    if 'heading' in section:
                        structured_data.append({'type': 'heading', 'content': section['heading'], 'source': 'web'})
                    if 'content' in section:
                        structured_data.extend([{'type': 'web_content', 'content': item, 'source': 'web'} 
                                               for item in section['content']])
    return structured_data

def retrieve_relevant_chunks(question, chatbot_id, top_k=3):
    """Retrieve top_k relevant chunks using FAISS."""
    global faiss_index, metadata_store
    if faiss_index is None or not metadata_store:
        if os.path.exists(f"faiss_index_{chatbot_id}.index") and os.path.exists(f"metadata_{chatbot_id}.json"):
            faiss_index = faiss.read_index(f"faiss_index_{chatbot_id}.index")
            with open(f"metadata_{chatbot_id}.json", 'r') as f:
                metadata_store = json.load(f)
        else:
            return []

    # Generate embedding for the question
    question_embedding = generate_embeddings([question])[0]

    # Search FAISS index
    distances, indices = faiss_index.search(np.array([question_embedding]), top_k)
    
    # Filter by chatbot_id and retrieve relevant chunks
    relevant_chunks = [metadata_store[idx] for idx in indices[0] if metadata_store[idx]["chatbot_id"] == chatbot_id]
    return [chunk["content"] for chunk in relevant_chunks]

def generate_answer(question, documents, max_length=500):
    """Generate answer using Groq."""
    try:
        total_context_length = sum(len(doc) for doc in documents)
        context = " ".join(documents)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": """You are a helpful AI assistant that provides natural, contextually appropriate responses. Scale your responses to match the user's input.
Core Guidelines:
1. Match the User's Style
- Keep responses brief for brief queries
- Be more detailed only when questions require it
- Mirror the user's formality level
- Use natural, conversational language
2. Information Handling
- Only use information from the provided context
- Say "I don't have enough information to answer that question" when needed
- Be direct and straightforward
- Avoid unnecessary elaboration
3. Response Quality
- Answer the main question first
- Add details only if relevant
- Skip unnecessary pleasantries
- Stay focused and on-topic"""},
                {"role": "user", "content": f"Context: {context}\nQuestion: {question}\nProvide a response that:\n1. Matches the question's scope and complexity\n2. Uses only contextual information\n3. Is natural and appropriately concise"}
            ],
            model="llama3-8b-8192",
            temperature=0.0,
            max_tokens=max_length
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating answer: {str(e)}")
        return "I apologize, but I encountered an issue while processing your question."

def get_general_answer(data, question, chatbot_id):
    """Use FAISS retrieval for answering questions."""
    try:
        # Load and preprocess data only if initializing
        if isinstance(data, str):
            chatbot_data = json.loads(data)
            if isinstance(chatbot_data, list) and chatbot_data:
                chatbot_data = chatbot_data[-1]
            pdf_data = chatbot_data.get('pdf_data', [])
            folder_data = chatbot_data.get('folder_data', [])
            web_data = chatbot_data.get('web_data', {})
            structured_data = preprocess_data(pdf_data, folder_data, web_data)
            initialize_faiss_index(structured_data, chatbot_id)
        
        # Retrieve relevant chunks
        relevant_chunks = retrieve_relevant_chunks(question, chatbot_id)
        if not relevant_chunks:
            return "I don’t have enough information to answer that question."
        
        # Generate answer with retrieved chunks
        return generate_answer(question, relevant_chunks)
    except Exception as e:
        logging.error(f"Error processing question: {str(e)}")
        return "I apologize, but I ran into an issue while processing your question."
