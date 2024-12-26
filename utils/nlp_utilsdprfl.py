import json
import re
from pymongo import MongoClient      
from sentence_transformers import SentenceTransformer,util
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer,DistilBertTokenizer, BertForQuestionAnswering, BertTokenizer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
import logging
import faiss
import numpy as np
import torch
from transformers import (
    DPRContextEncoder, 
    DPRQuestionEncoder, 
    DPRContextEncoderTokenizer, 
    DPRQuestionEncoderTokenizer,
    
)

import json
import nltk
from sentence_transformers import SentenceTransformer, util
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Load models from local cache
sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
flan_t5_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base", local_files_only=True)
flan_t5_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base", local_files_only=True)


# DPR Models
context_encoder = DPRContextEncoder.from_pretrained('facebook/dpr-ctx_encoder-single-nq-base', local_files_only=True)
question_encoder = DPRQuestionEncoder.from_pretrained('facebook/dpr-question_encoder-single-nq-base', local_files_only=True)
context_tokenizer = DPRContextEncoderTokenizer.from_pretrained('facebook/dpr-ctx_encoder-single-nq-base', local_files_only=True)
question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained('facebook/dpr-question_encoder-single-nq-base', local_files_only=True)


# NLP setup
nltk.download('stopwords')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))





# Constants
TOP_K = 5
MAX_LENGTH = 200
NUM_BEAMS = 4
LENGTH_PENALTY = 2.0

def preprocess_text(text):
    # Convert text to lowercase and tokenize
    text = text.lower()
    tokens = word_tokenize(text)

    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words and token.isalpha()]

    # Return the cleaned text
    return ' '.join(tokens)


def preprocess_data(pdf_data, folder_data, web_data):
    structured_data = []

    logging.debug(f"Preprocessing PDF data: {len(pdf_data)} items")
    logging.debug(f"Preprocessing folder data: {len(folder_data)} items")
    logging.debug(f"Preprocessing web data: {bool(web_data)}")

    # Process PDF and folder data
    for item in pdf_data + folder_data:
        if isinstance(item, dict) and 'text' in item:
            sentences = nltk.sent_tokenize(item['text'])
            structured_data.extend([{'type': 'text', 'content': sent, 'source': 'pdf/folder'} for sent in sentences])

    # Process web data
    if web_data:
        logging.debug(f"Web data keys: {web_data.keys()}")
        if isinstance(web_data, list) and len(web_data) > 0:
            web_data = web_data[0]  # Take the first item if it's a list
        
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
                    structured_data.extend(preprocess_data([], [], [sub_page]))  # Recursive call for sub-pages

    logging.info(f"Preprocessed data: {len(structured_data)} items")
    logging.debug(f"First few preprocessed items: {structured_data[:5]}")
    return structured_data





def get_t5_relevance_score(question, text):
    input_text = f"question: {question} context: {text} relevant:"
    input_ids = flan_t5_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).input_ids
    with torch.no_grad():
        output = flan_t5_model.generate(input_ids, max_length=5)
    result = flan_t5_tokenizer.decode(output[0], skip_special_tokens=True)
    return float(result == "true")




import torch
import numpy as np
import faiss
import json
import logging
from transformers import AutoTokenizer, AutoModel
import re
import random

def encode_passages(passages, encoder, tokenizer, batch_size=8):
    encoded_passages = []
    for i in range(0, len(passages), batch_size):
        batch = passages[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = encoder(**inputs)
        encoded_passages.extend(outputs.pooler_output.cpu().numpy())
    return np.array(encoded_passages)



def generate_answer(question, relevant_info, max_length=150):
    # Encode passages for DPR
    passage_embeddings = encode_passages(relevant_info, context_encoder, context_tokenizer)
    
    # Create FAISS index
    index = faiss.IndexFlatIP(passage_embeddings.shape[1])
    index.add(passage_embeddings)
    
    # Encode the query using DPR Question Encoder
    query_inputs = question_tokenizer([question], return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        query_embedding = question_encoder(**query_inputs).pooler_output.cpu().numpy()
    
    # Retrieve the top-1 results for more context
    D, I = index.search(query_embedding, k=1)
    retrieved_passages = [relevant_info[i] for i in I[0]]
    
    # Combine retrieved passages with weights based on relevance scores
    combined_context = "\n".join([f"{score:.2f}: {passage}" 
                                for score, passage in zip(D[0], retrieved_passages)])
    
    
    
    print(f"relevant info : {combined_context}")
    prompt = f"Answer this question based on the given context. Question: {question} Context: {retrieved_passages}"
    inputs = flan_t5_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    
    with torch.no_grad():
        outputs = flan_t5_model.generate(
            inputs.input_ids,
            max_length=MAX_LENGTH,
            min_length=MIN_LENGTH,
            num_beams=3,
            early_stopping=True
        )
    
    return flan_t5_tokenizer.decode(outputs[0], skip_special_tokens=True)




    
MIN_LENGTH = 10 




def get_general_answer(data, question):
    try:
        # Process input data
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
            relevant_items = (question, inventory_data)
            inventory_summary = "\n".join([f"{item['name']}: ${item['price']:.2f}, {item['quantity']} in stock" for item in relevant_items])
            answer = generate_answer(question, inventory_summary)
            answer = post_process_answer(answer)
            final_answer += answer + " "

        return final_answer.strip()
    except Exception as e:
        logging.error(f"Error generating inventory answer: {str(e)}")
        return "I apologize, there seems to be an issue with processing your query."
