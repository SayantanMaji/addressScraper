import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import pandas as pd

AddDict = {}

def scrape_address_data(postal_code):
    global AddDict

    print(postal_code)

    driver = webdriver.Chrome()
    driver.get("https://prizereactor.co.uk/index.php/register/50poundfriday")

    try:
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[3]/div/button"))).click()
        except:
            pass

        post_code_input = driver.find_element(By.NAME, "postcode")
        post_code_input.send_keys(postal_code)

        find_address_button = driver.find_element(By.XPATH, "//*[@id=\"register_find_address_button\"]")
        find_address_button.click()

        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        city_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "register_address_city")))
        city = city_element.get_attribute("value") if city_element else None

        country_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "register_address_county")))
        country = country_element.get_attribute("value") if country_element else None

        address_options = [option.text for option in soup.select("#register_address_line_1 option")]
        address_options.remove("Please select")


        # Extract details from the UK postcode
        area, district, sector, unit = extract_details_from_uk_postcode(postal_code)
        if area and district and sector and unit:
            if area not in AddDict:
                AddDict[area] = {}

            if district not in AddDict[area]:
                AddDict[area][district] = {}

            if sector not in AddDict[area][district]:
                AddDict[area][district][sector] = {}

            if unit not in AddDict[area][district][sector]:
                AddDict[area][district][sector][unit] = {
                    'City': city,
                    'Suburb': country,
                    'Address Options': address_options
                }


        else:
            print("Invalid UK postcode format.")

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()

        # Save the global dictionary to a file after each run
        with open("global_dict.pkl", "wb") as file:
            pickle.dump(AddDict, file)

    return [
        {
            'Postal Code': postal_code,
            'Suburb': city,
            'City': country,
            'Address Options': address_options
        }
    ]



def extract_details_from_uk_postcode(postcode):
    postcode_regex = r'^([A-Z]{1,2})(\d{1,2}[A-Z]?)(\d)([A-Z]{2})$'
    match = re.match(postcode_regex, postcode.upper().replace(" ", ""))

    if match:
        area = match.group(1)
        district = match.group(2)
        sector = match.group(3)
        unit = match.group(4)
        return area, district, sector, unit
    else:
        return None, None, None, None


if __name__ == "__main__":
    file_path = r'C:\Users\91967\Downloads\sample_data.xlsx'
    df = pd.read_excel(file_path)

    # Convert the postal codes to strings to preserve any leading zeros
    df['postcode'] = df['postcode'].astype(str)

    # Extract data from the 'postcode' column
    postal_codes = df['postcode'].tolist()

    # Add a space before the last three characters of each postal code if it doesn't exist
    postal_codes_with_space = [code[:-3] + (' ' if len(code) > 3 and not code[-4].isspace() else '') + code[-3:] for
                               code in postal_codes]

    # Create an empty list to store the results
    results = []

    # Call the function with each postal code and store the results in the list
    for postal_code in postal_codes_with_space:
        result = scrape_address_data(postal_code)
        results.extend(result)  # Extend the list instead of appending

    # Create a DataFrame from the results list
    df_output = pd.DataFrame(results, columns=['Postal Code', 'Suburb', 'City', 'Address Options'])

    # Save the DataFrame to a new Excel file
    output_file_path = r'C:\Users\91967\Downloads\output_data.xlsx'
    df_output.to_excel(output_file_path, index=False)

    print("Output data has been saved to 'output_data.xlsx'.")

    print("AddDict:", AddDict)
    print("Output data has been saved to 'output_data.xlsx'.")



