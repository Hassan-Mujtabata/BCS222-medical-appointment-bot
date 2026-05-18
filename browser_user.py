import asyncio
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from browser_use import Agent, BrowserConfig
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContextConfig

# Load environment variables
load_dotenv()

# Load Gemini API Key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
	raise ValueError('GEMINI_API_KEY is not set')

llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key))

# Load user data from .env
FIRST_NAME = os.getenv("FIRST_NAME")
LAST_NAME = os.getenv("LAST_NAME")
EMAIL = os.getenv("EMAIL")
DOB = os.getenv("DOB")
GENDER = os.getenv("GENDER")
PHONE = os.getenv("PHONE")
HAS_EMIRATES_ID = os.getenv("HAS_EMIRATES_ID")
EMIRATES_ID = os.getenv("EMIRATES_ID")
FIRST_TIME_VISIT = os.getenv("FIRST_TIME_VISIT")
SPECIALTY = os.getenv("SPECIALTY")
PAYMENT_METHOD = os.getenv("PAYMENT_METHOD")

# Define browser
browser = Browser(
	config=BrowserConfig(
		new_context_config=BrowserContextConfig(
			viewport_expansion=0,
		)
	)
)

async def run_search():
	task = f'''
		1. Go to 'https://www.clevelandclinicabudhabi.ae/en/forms/request-appointment-callback' scroll down for next step to look for the required field
		2. Find the First Name field and type {FIRST_NAME}.scroll down or up for next step to look for the required field
		3. Find the Last Name field and type {LAST_NAME}.scroll down or up for next step to look for the required field
		4. Find the Date of Birth field and type {DOB}.scroll down or up for next step to look for the required field
		5. Find the Gender field and select {GENDER}.scroll down or up for next step to look for the required field
		6. Find the Email field and type {EMAIL}.scroll down or up for next step to look for the required field
		7. Find the Phone field and type {PHONE}.scroll down or up for next step to look for the required field
		8. Check if user has Emirates ID: {HAS_EMIRATES_ID}, if yes then type {EMIRATES_ID}.scroll down or up for next step to look for the required field
		9. Indicate if this is their first visit: {FIRST_TIME_VISIT}.scroll down or up for next step to look for the required field
		10. Select specialty as {SPECIALTY}.scroll down or up for next step to look for the required field
		11. Choose payment method as {PAYMENT_METHOD}.scroll down or up for next step to look for the required field
		12. Submit the form.
	''',
	agent = Agent(
		task=task,
		llm=llm,
		max_actions_per_step=4,
		browser=browser,
	)

	await agent.run(max_steps=25)

if __name__ == '__main__':
	asyncio.run(run_search())
