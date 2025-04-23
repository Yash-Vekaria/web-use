from browser_use import Agent, Browser
from langchain_openai import ChatOpenAI
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
from browser_use import BrowserConfig
import pandas as pd
import asyncio
import sys
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
def generate_extended_message(record):
    first_name = record['FirstName']
    last_name = record['LastName']
    race = record['Race']
    gender = record['Gender']
    income = record['Income']
    dob = record['DOB']
    age = record['Age']
    address = record['Address']
    street = record['Street']
    city = record['City']
    state = record['State']
    zip_code = record['Zip']
    phone = record['Phone']
    email = record['Email']

    extend_system_message = f"""
You are an expert form filling AI assistant. Your goal is to help me fill forms on lead generation websites. 
REMEMBER the following details to be filled in a form wherever relevant:
- First Name: {first_name}
- Middle Initial: A.
- Last Name: {last_name}
- DOB: {dob}
- Age: {age}
- Gender: {gender}
- Height: 5'8"
- Weight: 150 lbs
- U.S. Citizen: Yes
- Email: {email}
- Phone: {phone}
- Address: {address}, USA
- Street Address: {street}
- City: {city}
- State: {state}
- Zip: {zip_code}
- Desired Insurance Coverage Amount: $500,000
- Desired Benefits: Create a safe and secure future for my family, provide for family's needs, pay off debts, cover funeral expenses, save money, and leave a legacy.
- Term Length: 30 years
- Insurance Type: Life
- Expected life insurance start date: Immediately
- Annual Income: {income}
- Total Debt: $50,000
- Homeowner: Yes
- Household Size: 2
- Marital Status: Married
- Beneficiares to add: Yes
- Spouse: Yes
- Spouse Age: 30
- Spouse DOB: 01/01/1993
- Spouse Name: Jane {last_name}
- Self and Spouse Employment Status: Employed
- Will or estate plan: No
- Recent engagement with extreme sports: Yes
- Recent Alcohol Consumption: Yes
- Alcolol Consumption Frequency: 2-3 drinks a week
- Recent Tobacco or Nicotine Product Use: No
- Recent Drug Use: No
- Recent Hospitalization: No
- Recent Surgery: No
- Recent Prescription Medication: No
- Receiving Oxygen or Dialysis: No
- Alcohol Absure: No
- Motor Vehicle Accidents in past 7 years: No
- Motor Vehicle Violations in past 10 years: Yes
- Numbers of Motor Vehicle Violations: 1
- DUI in past 10 years: No
- Criminal Convictions or Arrest: No
- Require Assistance with Activities of Daily Living: No
- Military Service: No
- Parents: Yes
- Children: No
- Pets: No
- Disability: No
- Current Health Status: Good
- Employment Status: Employed
- Any Ailments or Conditions: Heart Attack
- First Occurrence of Heart Attack: 12/21/2024
- Most Recent Occurrence of Heart Attack: 12/21/2024
- Current Medications Details: Aspirin 81 mg
- Current Medications Frequency: Once a day
- Current Medications Purpose: Prevent heart attack
- Current Medications Start Date: 12/24/2024
- Current Medications End Date: 05/24/2025
- Family History of Ailments: Yes, Father had a Heart Disease since he was 58 years old
- Family Death from Ailments: No
- Health or Medical Insurance: Yes
- Dental Insurance: No
- Vision Insurance: No
- Medicare: No
- Medicaid: Yes
- Health Insurance Type: Public
- Health Insurance Provider: Aetna
- Health Insurance Start Date: 01/01/2022
- Health Insurance End Date: 12/31/2025
- Ever filed for bankruptcy: No
- Ever requested or received workers' compensation, Social Security, or disability income payment: No
- Ever ver had an application for life insurance modified, rated, declined, postponed, canceled, or restricted in any way: No
- Ever subject to backup withholding from the IRS for failing to report interest or dividends: No
- Ever traveled to Afghanistan, Iraq, or any other country on the U.S. Department of State's list of countries with travel warnings: No
- Traveled outside the U.S. in the last 24 months: No
- Planning to travel outside the U.S. in the next 24 months: No

IMPORTANT: 
- Always WAIT 1 minute AFTER the last page of the form is submitted to view the displayed quotes.
- Select "I'm not a robot" checkbox if available and complete the captcha, if needed.
- Always checkmark the "I agree to the terms and conditions" or equivalent checkbox if available.
- The form usually starts by entering zip code. If you detect "95616" as pre-entered in the zip code field, replace it with the zip code from the profile above.
- If form field already has a pre-filled value that matches the corresponding input value from the profile above, do not change or re-enter it.
- If at any point you do not know what to input in the form, make an educated guess based on the profile provided above.
"""
    return extend_system_message


def load_csv_to_dict(csv_filename):
    df = pd.read_csv(csv_filename)
    records = df.to_dict(orient='index')
    return records


def save_screenshots(screenshots, website_index, website):
    domain = website.split("//")[-1].split("/")[0].replace("www.", "")
    ss_folder = f"/Users/yvekaria/Documents/Research/Leads-Tech-Policy/web-use/output/screenshots/{website_index}-{domain}"
    os.makedirs(ss_folder, exist_ok=True)
    for i, screenshot in enumerate(screenshots):
        screenshot_path = os.path.join(ss_folder, f"screenshot_{i}.png")
        with open(screenshot_path, 'wb') as f:
            # If screenshot is a string, encode it to bytes
            if isinstance(screenshot, str):
                f.write(screenshot.encode('utf-8'))
            else:
                f.write(screenshot)
    print(f"Saved screenshots to {ss_folder}")


# Defining an asynchronous function
async def main(website_index=None, website=None, system_message=None):
    custom_prompts = {
        "https://purchase.allstate.com/onlineshopping/welcome": "Select the product 'Term Life' once so that the selection turns green and then enter zip code and submit to start the process."
    }
    custom_instructions = f"\n\n{custom_prompts[website]}" if website in custom_prompts else ""
    agent = Agent(
        task=f"Visit {website} and fill the form as an individual looking for the life insurance quotes (for self + spouse) offered by the website.{custom_instructions}",
        llm=ChatOpenAI(model="gpt-4o"),
        browser=browser,  # Browser instance will be reused
        context=context,
        save_conversation_path="./logs/conversation",
        extend_system_message=system_message
    )

    result = await agent.run()
    screenshots = result.screenshots()
    save_screenshots(screenshots, website_index, website)

    # Manually close the browser
    await browser.close()

if __name__ == "__main__":
    # python3.12 run.py 
    csv_filename = "./browser_use/websites/demographics-experiments.csv"
    records_dict = load_csv_to_dict(csv_filename)
    for index, record in records_dict.items():
        # if int(index) < 1:
        #     continue
        extend_system_message = generate_extended_message(record) # Generate the extended system message for each record
        website = record['Website']
        website_index = record['Index']
        asyncio.run(main(website_index, website, extend_system_message)) # Run the main async function with the website and extended message
        print(f"Processed {website}")
        exit()