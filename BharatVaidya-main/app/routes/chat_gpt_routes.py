from typing import Optional, Dict, Any, Tuple, List
from flask import Blueprint, request, jsonify, Response, session
import sqlite3
import logging
from app.services import chat_gpt_service
from app.utils.util import get_context
import re

logging.basicConfig(level=logging.DEBUG)

chatgpt_bp = Blueprint("chatgpt_routes", __name__)

DATABASE = 'products.db'


def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        logging.debug("Database connection established.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Failed to connect to the database: {e}")
        raise


@chatgpt_bp.route("/api/chat_gpt/chat/", methods=["POST"])
def chat_with_gpt() -> Tuple[Response, int]:
    data: Optional[Dict[str, Any]] = request.json
    if data is None:
        logging.warning("Received empty JSON payload.")
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    message_content: Optional[str] = data.get("message_content")
    model: str = data.get("model", "gpt-4o")

    if message_content is None:
        logging.warning("Missing 'message_content' in the payload.")
        return jsonify({"error": "Missing field: message_content"}), 400

    logging.info(f"Processing message: {message_content}")

    milvus_context = get_context(message_content)
    logging.debug(f"Context from Milvus: {milvus_context}")

    conversation = [{"role": "user", "content": message_content}]
    if milvus_context and "CURE NOT FOUND IN DATABASE" not in milvus_context:
        logging.info("Cure found in Milvus, asking ChatGPT to simplify the response without modifying treatment.")
        conversation.append({
            "role": "system",
            "content": (
                """You are an assistant that helps explain Ayurvedic treatments in simple terms. 
                Your task is to simplify the following Ayurvedic text for a common person to understand. 
                Strictly ensure that you do not modify any treatment details or suggest any changes, even if the treatments appear incorrect. 
                Only simplify the names of herbs and concepts in plain language.\n\n"""
                f"Original text:\n{milvus_context}"
            )
        })
    else:
        logging.info("Cure not found in Milvus, proceeding with normal ChatGPT conversation.")
        conversation.append({
            "role": "system",
            "content": milvus_context or "No specific context found in Milvus. Proceeding with default conversation."
        })

    response = chat_gpt_service.chat_with_gpt(conversation, model)
    chat_response = response['message']
    logging.debug(f"Response from ChatGPT: {chat_response}")

    ingredients = extract_ingredients_from_response(chat_response)
    logging.info(f"Extracted ingredients: {ingredients}")

    session['ingredients'] = ingredients
    logging.debug(f"Ingredients stored in session: {session['ingredients']}")

    return jsonify({"message": chat_response, "ingredients": ingredients}), 200


@chatgpt_bp.route("/api/search_products", methods=["POST"])
def search_products() -> Tuple[Response, int]:
    data: Optional[Dict[str, Any]] = request.json
    ingredients = data.get('ingredients') if data else None

    if not ingredients:
        ingredients = session.get('ingredients', [])
        logging.debug(f"Ingredients retrieved from session: {ingredients}")
        if not ingredients:
            logging.warning("No ingredients provided for search and none found in session.")
            return jsonify({"error": "Invalid or missing ingredients data"}), 400

    logging.info(f"Searching products with ingredients: {ingredients}")

    results = search_products_by_ingredients(ingredients)

    logging.debug(f"Search results: {results}")
    return jsonify({"results": results}), 200


def extract_ingredients_from_response(response: str) -> List[str]:
    possible_ingredients = [
        'Mahanila Taila', 'bibhitaka', 'amalaka', 'triphala', 'neem', 'honey', 'lemon', 'cinnamon',
        'dmalaka juice', 'pippali', 'candana', 'utpala', 'lotus pollens', 'madhuka', 'ghee', 'rock salt',
        'triphala water', 'bhallataka', 'guktamla', 'sesamum', 'iron powder', 'rice', 'cyavanapraga',
        'trivrt', 'haritaki', 'danti'
    ]

    ingredient_pattern = re.compile(
        r'\b(?:' + '|'.join(re.escape(ingredient) for ingredient in possible_ingredients) + r')\b', re.IGNORECASE)
    found_ingredients = ingredient_pattern.findall(response)

    unique_ingredients = list(set(found_ingredients))
    logging.debug(f"Ingredients extracted: {unique_ingredients}")
    return unique_ingredients


def search_products_by_ingredients(ingredients: List[str]) -> List[Dict[str, Any]]:
    if not ingredients:
        logging.info("No ingredients provided for search.")
        return []

    ingredients = [ingredient.lower().strip() for ingredient in ingredients]
    logging.debug(f"Normalized ingredients for search: {ingredients}")

    query = "SELECT product_category, product_name, price, link, ingredients FROM products WHERE"
    conditions = [" LOWER(ingredients) LIKE ?" for _ in ingredients]
    query += " OR ".join(conditions)

    params = [f"%{ingredient}%" for ingredient in ingredients]
    logging.debug(f"SQL query: {query}")
    logging.debug(f"Query parameters: {params}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        logging.debug(f"Number of rows fetched: {len(rows)}")
        if len(rows) == 0:
            logging.info("No products found for the given ingredients.")

        results = [dict(row) for row in rows]
        logging.debug(f"Products found: {results}")
        return results

    except sqlite3.Error as e:
        logging.error(f"An error occurred while searching products: {e}")
        return []


# Helper function to print all products for debugging purposes
def print_all_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()

        products = [dict(row) for row in rows]
        logging.debug(f"All products in the database: {products}")
    except sqlite3.Error as e:
        logging.error(f"An error occurred while fetching all products: {e}")


# Call this function to debug and check the products
print_all_products()
