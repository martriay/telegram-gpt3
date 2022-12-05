"""Make some requests to OpenAI's chatbot"""

import time
import os 
import flask

from flask import g

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

APP = flask.Flask(__name__)
PLAY = sync_playwright().start()
BROWSER = PLAY.chromium.launch_persistent_context(
    user_data_dir="/tmp/playwright",
    headless=True,
)

PAGE = BROWSER.new_page()
USERNAME = os.getenv('API_USER')
PASSWORD = os.environ.get('API_PASSWORD')

def get_input_box():
    """Get the child textarea of `PromptTextarea__TextareaWrapper`"""
    return PAGE.query_selector("div[class*='PromptTextarea__TextareaWrapper']").query_selector("textarea")

def is_logged_in():
    try:
        # See if we have a textarea with data-id="root"
        return get_input_box() is not None
    except AttributeError:
        return False

def send_message(message):
    # Send the message
    box = get_input_box()
    box.click()
    box.fill(message)
    box.press("Enter")
    while PAGE.query_selector(".result-streaming") is not None:
        time.sleep(0.1)

def get_last_message():
    """Get the latest message"""
    page_elements = PAGE.query_selector_all("div[class*='ConversationItem__Message']")
    last_element = page_elements[-1]
    return last_element.inner_text()

@APP.route("/chat", methods=["GET"])
def chat():
    message = flask.request.args.get("q")
    print("Sending message: ", message)
    send_message(message)
    response = get_last_message()
    print("Response: ", response)
    return response

def start_browser():
    PAGE.goto("https://chat.openai.com/")
    if not is_logged_in():
        print("Please log in to OpenAI Chat")
        print("Press enter when you're done")
        PAGE.get_by_text("Log in", exact=True).click()
        PAGE.locator("#username").fill(USERNAME)
        PAGE.get_by_text("Continue", exact=True).click()
        PAGE.locator("#password").fill(PASSWORD)
        PAGE.get_by_text("Continue", exact=True).click()
    APP.run(port=5001, threaded=False)
        
if __name__ == "__main__":
    start_browser()
