"""Make some requests to OpenAI's chatbot"""

import time
import os 
import sys
import logging
import flask

from flask import g
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('API_USER')
PASSWORD = os.getenv('API_PASSWORD')

file_handler = logging.FileHandler(filename='chats.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] %(message)s',
    handlers=[file_handler, stdout_handler]
)

APP = flask.Flask(__name__)
PLAY = sync_playwright().start()
PAGE = PLAY.chromium.launch_persistent_context(
    user_data_dir="/tmp/playwright",
    headless=True,
).new_page()


def get_input_box():
    """Get the child textarea of `PromptTextarea__TextareaWrapper`"""
    return PAGE.query_selector("form").query_selector("textarea")

def is_logged_in():
    return PAGE.get_by_text("Log out").count() > 0

def login():
    PAGE.goto("https://chat.openai.com/")
    if not is_logged_in():
        logging.info("Logging in...")
        PAGE.get_by_text("Log in", exact=True).click()
        PAGE.locator("#username").fill(USERNAME)
        PAGE.get_by_text("Continue", exact=True).click()
        PAGE.locator("#password").fill(PASSWORD)
        PAGE.get_by_text("Continue", exact=True).click()
    logging.info("Logged in")

def send_message(user, message):
    try:
        logging.info(f"{user} says: {message}")
        box = get_input_box()
        box.fill(message)
        box.press("Enter")
    except AttributeError:
        logging.error("There has been an error, logging in again")
        login()
        send_message(message)

def get_last_message():
    """Get the latest message"""
    page_elements = PAGE.query_selector_all("div[class*='request-']")
    last_element = page_elements[-1]
    return last_element.inner_text()

@APP.route("/reset", methods=["POST"])
def reset():
    login()

@APP.route("/chat", methods=["GET"])
def chat():
    message = flask.request.args.get("q")
    user = flask.request.args.get("u")
    send_message(user, message)

    while PAGE.query_selector(".result-streaming") is not None:
        time.sleep(0.1)

    response = get_last_message()
    logging.info(f"Response: {response}")
    return response

def start_api():
    PAGE.set_default_timeout(0)
    login()
    APP.run(port=5001, threaded=False)
        
if __name__ == "__main__":
    start_api()
