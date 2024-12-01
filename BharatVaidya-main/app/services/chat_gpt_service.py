import os
import requests
import json

def chat_with_gpt(conversation_history: list, model: str = "gpt-4o") -> dict:
    """
    Sends a request to OpenAI's GPT model to generate a chat response
    for a multi-turn conversation.

    Args:
        conversation_history (list): The conversation history to send to the GPT model.
        model (str, optional): The identifier of the GPT model to use.
            Defaults to 'gpt-4o-mini'.

    Returns:
        dict: A dictionary containing the formatted response from the GPT model.
    """
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    # Pre-prompt to instruct ChatGPT to act as an Ayurvedic assistant
    pre_prompt = {
        "role": "system",
        "content": "You are an expert Ayurvedic assistant. Your goal is to provide diagnostic and treatment suggestions based on Ayurvedic principles. Please provide answers using simple, easy-to-understand language."
    }

    # Insert the pre-prompt at the beginning of the conversation history
    conversation_with_pre_prompt = [pre_prompt] + conversation_history

    data = {
        "model": model,
        "messages": conversation_with_pre_prompt,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(data), verify=False, timeout=15
        )
        response.raise_for_status()
        response_data = response.json()

        # Extract the message content
        assistant_message = response_data["choices"][0]["message"]["content"]

        # Format response to HTML
        formatted_message = format_response_to_html(assistant_message)

        return {"message": formatted_message}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while contacting the OpenAI API: {e}")
        return {"message": "There was an error processing your request. Please try again later."}


def format_response_to_html(response: str) -> str:
    """
    Format the GPT response into HTML for better readability.

    Args:
        response (str): The raw response text from the GPT model.

    Returns:
        str: A string formatted with HTML.
    """
    # Convert specific markers to HTML tags for better formatting
    response = response.replace("\n", "<br>")
    response = response.replace("**", "<strong>").replace("**", "</strong>")
    # Further processing can be done here to parse lists, headers, etc.

    return response
