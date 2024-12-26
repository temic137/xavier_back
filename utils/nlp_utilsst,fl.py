import json
import logging
from typing import List, Dict, Any
import torch
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load models from local cache
sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
flan_t5_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base", local_files_only=True)
flan_t5_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base", local_files_only=True)

# NLP setup
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Constants
TOP_K = 5
MAX_LENGTH = 50
MIN_LENGTH = 10

def preprocess_text(text: str) -> str:
    """Preprocess text by converting to lowercase, removing stopwords, and lemmatizing."""
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words and token.isalpha()]
    return ' '.join(tokens)

def preprocess_data(pdf_data: List[Dict], folder_data: List[Dict], web_data: Dict) -> List[Dict]:
    """Preprocess different types of input data."""
    structured_data = []

    # Process PDF and folder data
    for item in pdf_data + folder_data:
        if isinstance(item, dict) and 'text' in item:
            sentences = sent_tokenize(item['text'])
            structured_data.extend([{'type': 'text', 'content': sent, 'source': 'pdf/folder'} for sent in sentences])

    # Process web data
    if web_data:
        if isinstance(web_data, list) and web_data:
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

    logging.info(f"Preprocessed {len(structured_data)} items")
    return structured_data

def get_relevance_score(question: str, text: str) -> float:
    """Get FLAN-T5 relevance score for question-text pair."""
    input_text = f"Rate the relevance of this text to answer the question on a scale of 0 to 1. Question: {question} Text: {text}"
    inputs = flan_t5_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    
    with torch.no_grad():
        outputs = flan_t5_model.generate(
            inputs.input_ids,
            max_length=5,
            num_beams=2,
            early_stopping=True
        )
    
    result = flan_t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
    try:
        return float(result)
    except ValueError:
        return 0.0

def get_relevant_items(question: str, inventory_data: List[Dict], top_k: int = 5) -> List[Dict]:
    """Get relevant inventory items for a given question using SentenceTransformer."""
    try:
        if not inventory_data:
            return []
            
        inventory_texts = [
            f"{item['name']} {item['category']} ${item['price']} {item['quantity']} in stock"
            for item in inventory_data
        ]
        
        # Get embeddings
        question_embedding = sentence_transformer.encode(preprocess_text(question), convert_to_tensor=True)
        inventory_embeddings = sentence_transformer.encode(inventory_texts, convert_to_tensor=True)

        # Calculate similarities
        similarities = util.pytorch_cos_sim(question_embedding, inventory_embeddings)[0]
        top_k_indices = similarities.argsort(descending=True)[:top_k].cpu().numpy()

        return [inventory_data[i] for i in top_k_indices]
    except Exception as e:
        logging.error(f"Error in get_relevant_items: {str(e)}")
        return []

def generate_answer(question: str, relevant_info: str) -> str:
    """Generate an answer using FLAN-T5."""
    if not relevant_info:
        return "No relevant information found."

    try:
        print(f"relevant info : {relevant_info}")
        prompt = f"Answer this question based on the given context. Question: {question} Context: {relevant_info}"
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
    except Exception as e:
        logging.error(f"Error generating answer: {str(e)}")
        return "Error generating answer."



def find_relevant_info(question: str, structured_data: List[Dict], top_k: int = 5) -> List[Dict]:
    """Find relevant information using SentenceTransformer embeddings."""
    try:
        question_embedding = sentence_transformer.encode(question, convert_to_tensor=True)
        results = []
        
        for item in structured_data:
            content = item['content']
            content_embedding = sentence_transformer.encode(content, convert_to_tensor=True)
            
            # Calculate semantic similarity
            similarity = util.pytorch_cos_sim(question_embedding, content_embedding)[0][0].item()
            
            # Get relevance score from FLAN-T5
            relevance_score = get_relevance_score(question, content)
            
            # Combine scores
            combined_score =  0.7 * similarity
            #  0.7 * similarity + 0.3 * relevance_score
            results.append({
                "content": content,
                "score": combined_score,
                "source": item.get('source', 'unknown')
            })

        print(results)
        return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
    except Exception as e:
        logging.error(f"Error in find_relevant_info: {str(e)}")
        return []




def get_general_answer(data: Any, question: str) -> str:
    """Get answer for general questions."""
    try:
        chatbot_data = json.loads(data) if isinstance(data, str) else data
        if isinstance(chatbot_data, list) and chatbot_data:
            chatbot_data = chatbot_data[-1]
        
        if not isinstance(chatbot_data, dict):
            raise ValueError("Invalid data format.")
        
        pdf_data = chatbot_data.get('pdf_data', [])
        folder_data = chatbot_data.get('folder_data', [])
        web_data = chatbot_data.get('web_data', {})
        
        structured_data = preprocess_data(pdf_data, folder_data, web_data)
        relevant_info = find_relevant_info(question, structured_data)
        
        if not relevant_info:
            return "No relevant information found."
            
        context = " ".join([item['content'] for item in relevant_info[:2]])
        return generate_answer(question, context)
    
    except Exception as e:
        logging.error(f"Error processing question: {str(e)}")
        return "An error occurred while processing your request."

def get_inventory_rag_answer(data: Any, query: str) -> str:
    """Get answer for inventory-related queries."""
    try:
        # Parse input data
        chatbot_data = json.loads(data) if isinstance(data, str) else data
        inventory_data = chatbot_data.get('db_data', [{}])[0].get('text', [])
        inventory_data = json.loads(inventory_data) if isinstance(inventory_data, str) else inventory_data

        if not inventory_data:
            return "No inventory data available."

        # Split complex queries
        questions = sent_tokenize(query)
        questions = [q for q in questions if q.strip().endswith('?')] or [query]
        
        final_answer = []
        for question in questions:
            relevant_items = get_relevant_items(question, inventory_data)
            if relevant_items:
                inventory_summary = "\n".join([
                    f"{item['name']}: ${item['price']:.2f}, {item['quantity']} in stock"
                    for item in relevant_items
                ])
                answer = generate_answer(question, inventory_summary)
                final_answer.append(answer)

        return " ".join(final_answer) if final_answer else "I couldn't find relevant information to answer your query."

    except Exception as e:
        logging.error(f"Error generating inventory answer: {str(e)}")
        return "I apologize, there seems to be an issue with processing your query."