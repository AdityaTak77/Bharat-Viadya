"""
Module to define routes for Ayurvedic diagnostic chatbot handling.

This module sets up a Flask Blueprint for handling routes related to an Ayurvedic
diagnostic tool. It includes routes for rendering the chatbot interface.
"""

from flask import Blueprint, render_template, Response

form_bp = Blueprint("form_bp", __name__)

@form_bp.route("/")
def home() -> Response:
    """
    Redirect to the chatbot interface.

    Returns:
        Response: Renders the chatbot HTML page.
    """
    return render_template("chatbot.html")