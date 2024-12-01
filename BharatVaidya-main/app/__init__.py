from flask import Flask, session, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
app.config["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
app.secret_key = os.environ.get("SECRET_KEY", "bharatvaidya")  # Set a secret key for session management
 # Set a secret key for session management
CORS(app)

# Importing and registering blueprints after Flask app creation
# to avoid circular imports.
from app.routes import chat_gpt_routes, form_routes

app.register_blueprint(chat_gpt_routes.chatgpt_bp)
app.register_blueprint(form_routes.form_bp)

# Route to serve the chatbot HTML page
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')