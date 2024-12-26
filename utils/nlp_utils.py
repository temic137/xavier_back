import cohere
import json
import logging
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import json
import re
from pymongo import MongoClient      
import torch
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
import logging
import faiss
import numpy as np
import torch
from huggingface_hub import InferenceClient

nltk.download('stopwords')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

import os
from dotenv import load_dotenv

load_dotenv()

huggingface_token = os.getenv('HUGGINGFACE_API_TOKEN')

cohere_token =  os.getenv('COHERE_CLIENT')

# Initialize Cohere client (you'll replace this with your actual API key)
cohere_client = cohere.Client(api_key=cohere_token)


# Replace the Cohere client initialization
huggingface_client = InferenceClient(api_key=huggingface_token)

def preprocess_text(text):
    # The existing preprocessing remains the same
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [token for token in tokens if token.isalpha()]
    return ' '.join(tokens)

def preprocess_data(pdf_data, folder_data, web_data):
    # Maintain the existing preprocess_data function structure
    structured_data = []

    logging.debug(f"Preprocessing PDF data: {len(pdf_data)} items")
    logging.debug(f"Preprocessing folder data: {len(folder_data)} items")
    logging.debug(f"Preprocessing web data: {bool(web_data)}")

    # Process PDF and folder data
    for item in pdf_data + folder_data:
        if isinstance(item, dict) and 'text' in item:
            sentences = nltk.sent_tokenize(item['text'])
            structured_data.extend([{'type': 'text', 'content': sent, 'source': 'pdf/folder'} for sent in sentences])

    # Process web data (existing logic remains the same)
    if web_data:
        logging.debug(f"Web data keys: {web_data.keys()}")
        if isinstance(web_data, list) and len(web_data) > 0:
            web_data = web_data[0]
        
        if isinstance(web_data, dict):
            if 'title' in web_data:
                structured_data.append({'type': 'title', 'content': web_data['title'], 'source': 'web'})
            
            if 'sections' in web_data:
                for section in web_data['sections']:
                    if isinstance(section, dict):
                        if 'heading' in section:
                            structured_data.append({'type': 'heading', 'content': section['heading'], 'source': 'web'})
                        if 'content' in section:
                            structured_data.extend([{'type': 'web_content', 'content': item, 'source': 'web'} for item in section['content']])
            
            if 'sub_pages' in web_data:
                for sub_page in web_data['sub_pages']:
                    structured_data.extend(preprocess_data([], [], [sub_page]))

    logging.info(f"Preprocessed data: {len(structured_data)} items")
    return structured_data


# def generate_answer(question, relevant_info, max_length=150):
#     # Combine all relevant information into a single context
#     context = " ".join(relevant_info)
    
#     try:
#         # Use Cohere's chat generation with web search
#         response = cohere_client.chat(
#             model='command-r-plus',
#             message=f"Context: {context}\n\nQuestion: {question}",
#             temperature=0.3,
#             connectors=[{"id": "web-search"}]
#         )
        
#         return response.text
#     except Exception as e:
#         logging.error(f"Error generating answer: {str(e)}")
#         return "I apologize, but I encountered an issue while processing your question."




# def generate_answer(question, relevant_info, max_length=150):
#     # Combine all relevant information into a single context
#     context = " ".join(relevant_info)
    
#     try:
#         # Prepare messages for the chat model
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context but you are concise and helpful and answer questions in a friendly manner."},
#             {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
#         ]
        
#         # Use Hugging Face's chat completion
#         response = huggingface_client.chat.completions.create(
#             model="HuggingFaceH4/zephyr-7b-beta",  # You can change this to another chat model
#             messages=messages,
#             temperature=0.1,
#             max_tokens=75  # Adjust as needed
#         )
        
#         # Extract the text from the response
#         return response.choices[0].message.content
    
#     except Exception as e:
#         logging.error(f"Error generating answer: {str(e)}")
#         return "I apologize, but I encountered an issue while processing your question."

from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict
import logging
from nltk.tokenize import word_tokenize
import nltk

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
except:
    pass

def prepare_bm25_index(documents: List[str]) -> BM25Okapi:
    """
    Prepare BM25 index from a list of documents.
    """
    # Tokenize documents
    tokenized_documents = [word_tokenize(doc.lower()) for doc in documents]
    # Create BM25 index
    return BM25Okapi(tokenized_documents)

def get_relevant_passages(question: str, documents: List[str], bm25: BM25Okapi, top_k: int = 3) -> List[str]:
    """
    Retrieve the most relevant passages using BM25 scoring.
    """
    # Tokenize the question
    tokenized_question = word_tokenize(question.lower())
    
    # Get BM25 scores for all documents
    scores = bm25.get_scores(tokenized_question)
    
    # Get top-k document indices
    top_indices = np.argsort(scores)[-top_k:][::-1]
    
    # Return the top-k documents
    return [documents[i] for i in top_indices]

def generate_answer(question: str, documents: List[str], max_length: int = 150) -> str:
    """
    Generate an answer using BM25 ranking and language model.
    """
    try:
        # Create BM25 index
        bm25 = prepare_bm25_index(documents)
        
        # Get relevant passages
        relevant_info = get_relevant_passages(question, documents, bm25)
        
        # Combine relevant information into context
        context = " ".join(relevant_info)
        
        # Prepare messages for the chat model
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on the given context but you are concise and helpful and answer questions in a friendly manner."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}"
            }
        ]
        
        # Use Hugging Face's chat completion
        response = huggingface_client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=messages,
            temperature=0.1,
            max_tokens=250
        )
        
        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"Error generating answer: {str(e)}")
        return "I apologize, but I encountered an issue while processing your question."


def get_general_answer(data, question):
    try:
        # Process input data (existing logic remains the same)
        chatbot_data = json.loads(data) if isinstance(data, str) else data
        if isinstance(chatbot_data, list) and chatbot_data:
            chatbot_data = chatbot_data[-1]
        
        if not isinstance(chatbot_data, dict):
            raise ValueError("Invalid data format.")
        
        # Extract data from different sources
        pdf_data = chatbot_data.get('pdf_data', [])
        folder_data = chatbot_data.get('folder_data', [])
        web_data = chatbot_data.get('web_data', {})
        
        # Preprocess and structure the data
        structured_data = preprocess_data(pdf_data, folder_data, web_data)
        text_data = [item['content'] for item in structured_data if 'content' in item]
        
        # Generate and enhance the answer
        answer = generate_answer(question, text_data)
        
        return answer
        
    except Exception as e:
        logging.error(f"Error processing question: {str(e)}")
        return "I apologize, but I ran into an issue while processing your question. Could you try rephrasing it?"

# Keep other existing functions like split_complex_query and post_process_answer unchanged

def preprocess_text(text):
    # Convert text to lowercase and tokenize
    text = text.lower()
    tokens = word_tokenize(text)

    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words and token.isalpha()]

    # Return the cleaned text
    return ' '.join(tokens)


def split_complex_query(query):
    sentences = sent_tokenize(query)
    questions = [s for s in sentences if s.strip().endswith('?')]
    return questions if questions else [query]


def post_process_answer(answer, question):
    if not any(keyword in answer.lower() for keyword in question.lower().split()):
        answer = f"To answer your question about {question.lower()}: {answer}"
    
    if any(keyword in answer.lower() for keyword in ['might', 'maybe', 'possibly', 'not sure']):
        answer += " Please note that this answer is based on the available information and may not be completely certain."
    
    return answer


def get_inventory_rag_answer(data, query):
    try:
        chatbot_data = json.loads(data) if isinstance(data, str) else data
        inventory_data = chatbot_data.get('db_data', [{}])[0].get('text', [])
        inventory_data = json.loads(inventory_data) if isinstance(inventory_data, str) else inventory_data

        questions = split_complex_query(query)
        final_answer = ""

        for question in questions:
            inventory_summary = "\n".join([f"{item['name']}: ${item['price']:.2f}, {item['quantity']} in stock" for item in inventory_data])
            answer = generate_answer(question, [inventory_summary])
            answer = post_process_answer(answer, question)
            final_answer += answer + " "

        return final_answer.strip()
    except Exception as e:
        logging.error(f"Error generating inventory answer: {str(e)}")
        return "I apologize, there seems to be an issue with processing your query."