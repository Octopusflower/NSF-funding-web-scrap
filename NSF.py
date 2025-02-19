from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Automatically manage ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the NSF funding opportunities page
url = "https://www.nsf.gov/funding/opportunities"
driver.get(url)

# Wait for content to load
time.sleep(10)  # Ensure full page load

funding_data = []  # List to store all scraped data

while True:
    print("🔄 Scraping page...")

    # Extract funding opportunities
    opportunities = driver.find_elements(By.CSS_SELECTOR, "div.funding-search-teaser")

    if not opportunities:
        print("❌ No funding opportunities found on this page. Exiting loop.")
        break

    for opp in opportunities:
        try:
            # Extracting Program Title & Link
            title_element = opp.find_element(By.CSS_SELECTOR, "h3.teaser--title a") if opp.find_elements(By.CSS_SELECTOR, "h3.teaser--title a") else None
            title = title_element.text.strip() if title_element else ""
            program_link = title_element.get_attribute("href") if title_element else ""

            # Extracting Program Description
            description_element = opp.find_element(By.CSS_SELECTOR, "div.funding-search-teaser_text p") if opp.find_elements(By.CSS_SELECTOR, "div.funding-search-teaser_text p") else None
            description = description_element.text.strip() if description_element else ""

            # Extracting Award Type & Opportunity Type
            award_type_element = opp.find_element(By.CSS_SELECTOR, "div.funding-search-teaser__award-type") if opp.find_elements(By.CSS_SELECTOR, "div.funding-search-teaser__award-type") else None
            award_type = award_type_element.text.strip() if award_type_element else ""

            opportunity_type_element = opp.find_element(By.CSS_SELECTOR, "div.funding-search-teaser__opp-type") if opp.find_elements(By.CSS_SELECTOR, "div.funding-search-teaser__opp-type") else None
            opportunity_type = opportunity_type_element.text.strip() if opportunity_type_element else ""

            # Extracting Posted Date
            posted_date_element = opp.find_element(By.CSS_SELECTOR, "div.funding-search-teaser__posted div.field__inline span:nth-child(2)") if opp.find_elements(By.CSS_SELECTOR, "div.funding-search-teaser__posted div.field__inline span:nth-child(2)") else None
            posted_date = posted_date_element.text.strip() if posted_date_element else ""

            # Extracting Proposal Deadline
            deadline_element = opp.find_element(By.CSS_SELECTOR, "div.funding-search-teaser__req") if opp.find_elements(By.CSS_SELECTOR, "div.funding-search-teaser__req") else None
            proposal_deadline = deadline_element.text.strip() if deadline_element else ""

            # Append extracted data
            funding_data.append([
                award_type, opportunity_type, title, description, posted_date, proposal_deadline, program_link
            ])

        except Exception as e:
            print(f"⚠️ Skipping an entry due to error: {e}")

    # Try to find the "Next" button and go to the next page
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "li.pager__item.pager__item--next a")
        driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to the button
        time.sleep(2)
        next_button.click()  # Click the "Next" button
        time.sleep(5)  # Wait for the next page to load
    except Exception:
        print("✅ No more pages. Scraping complete.")
        break

# Close browser
driver.quit()

# Convert to DataFrame with the correct column structure
df = pd.DataFrame(funding_data, columns=[
    "Award Type", "Opportunity Type", "Program Title", "Program Description",
    "Posted Date", "Proposal Deadline", "Program Link"
])

# Check if data was extracted
if df.empty:
    print("❌ No data extracted! Try increasing the sleep time or modifying selectors.")

# Save to CSV
csv_filename = "nsf_funding_opportunities_cleaned.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8")

print(f"✅ Data saved to {csv_filename}")
