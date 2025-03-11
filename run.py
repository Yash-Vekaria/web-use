from browser_use import Agent, Browser
from langchain_openai import ChatOpenAI
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
from browser_use import BrowserConfig
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/yvekaria/.config/gcloud/application_default_credentials.json"

# Basic configuration
browser_config = BrowserConfig(
    headless=False,
    disable_security=True
)

context_config = BrowserContextConfig(
    wait_for_network_idle_page_load_time=3.0,
    browser_window_size={'width': 1280, 'height': 1100},
    locale='en-US',
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    highlight_elements=True,
    viewport_expansion=500,
)

browser = Browser(config=browser_config)
context = BrowserContext(browser=browser, config=context_config)

# Add your custom instructions
extend_system_message = """
You are an expert form filling AI assistant. Your goal is to help me fill forms on lead generation websites. 
REMEMBER the following details to be filled in a form wherever relevant:
- First Name: Honey
- Last Name: Funny
- DOB: 10/10/1990
- Age: 34
- Gender: Male
- Email: honey.money.funny@gmail.com
- Phone: 484-743-8377
- Address: 1440, Wake Forest Drive, Davis, CA, 95616, USA
- Street Address: 1440, Wake Forest Drive
- City: Davis
- State: CA
- Zip: 95616
- Country: USA
IMPORTANT: If at any point you do not know what to input in the form, make an educated guess based on the profile provided above.
"""


# Defining an asynchronous function
async def main():
    agent = Agent(
        task="Visit netquote.com and fill the form as an individual looking for the services offered by the website.",
        llm=ChatOpenAI(model="gpt-4o"),
        browser=browser,  # Browser instance will be reused
        context=context,
        save_conversation_path="./logs/conversation",
        extend_system_message=extend_system_message
    )

    await agent.run()

    # Manually close the browser
    await browser.close()

# Run the main async function
import asyncio
asyncio.run(main())