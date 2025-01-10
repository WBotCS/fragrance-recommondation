from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, NoSuchElementException
import time

# Function to initialize the Chrome WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    # Set the path to the Chrome browser executable
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    # Add necessary Chrome options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    # Set the path to the ChromeDriver executable
    service = Service('/Users/wbot/Desktop/fragrance-recommondation 2/venv/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Test Case 1: Verify Floating Action Button Opens Pop-up Modal
def test_fab_opens_popup():
    driver = init_driver()
    driver.get("http://127.0.0.1:5000/")

    # Wait for the form page to be visible
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "formPage")))

    # Scroll to the form page
    driver.execute_script("document.getElementById('formPage').scrollIntoView({ behavior: 'smooth' });")

    try:
        # Wait for the FAB to be clickable
        fab = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "fab")))
        fab.click()

        # Wait for the popup to be visible
        popup = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "fabPopup")))
        assert popup.is_displayed(), "Pop-up modal should be displayed when FAB is clicked."

    except (ElementNotInteractableException, TimeoutException) as e:
        print(f"An error occurred: {e}")
        assert False, f"An exception occurred: {e}"

    finally:
        driver.quit()


# Test Case 2: Verify "Get Started" Button Functionality
def test_get_started_button():
    driver = init_driver()
    driver.get("http://127.0.0.1:5000/")  # Replace with your local server URL

    try:
        # Wait for the "Get Started" button to be clickable
        get_started_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "getStartedButton"))
        )

        # Click the "Get Started" button
        get_started_button.click()

        # Wait for the form page to be visible (indicating successful scroll)
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "formPage"))
        )

        # Assert that the form page is now the active element (or some other way to confirm scroll)
        form_page = driver.find_element(By.ID, "formPage")
        assert form_page.is_displayed(), "Form page should be visible after clicking 'Get Started'."

    except (ElementNotInteractableException, TimeoutException, NoSuchElementException) as e:
        print(f"An error occurred: {e}")
        assert False, f"An exception occurred: {e}"

    finally:
        driver.quit()


# Placeholder for other test cases
def test_placeholder():
    assert True