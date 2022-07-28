# from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import sys
from telegram import send_message, send_photo
from creds import username, password, url_id, appointment_url_id


def run_visa_scraper(base_url, no_appointment_text):
    def has_website_changed():
        '''Checks for changes in the site. Returns True if a change was found.'''
        # Getting the website to check
        url = base_url + '/{url_id}'
        driver.get(url)

        # Checking if website is still logged
        if driver.current_url == 'https://ais.usvisa-info.com/' + country_code + '/niv/users/sign_in':
            print('Logging in.')
            # Clicking the first prompt, if there is one
            try:
                driver.find_element(by=By.XPATH, value='/html/body/div[6]/div[3]/div/button').click()
            except:
                pass
            # Filling the user and password
            user_box = driver.find_element(by=By.NAME, value='user[email]')
            user_box.send_keys(username)
            password_box = driver.find_element(by=By.NAME, value='user[password]')
            password_box.send_keys(password)
            # Clicking the checkbox
            driver.find_element(by=By.XPATH, value='//*[@id="new_user"]/div[3]/label/div').click()
            # Clicking 'Sign in'
            driver.find_element(by=By.XPATH, value='//*[@id="new_user"]/p[1]/input').click()
            
            # Waiting for the page to load.
            # 5 seconds may be ok for a computer, but it doesn't seem enougn for the Raspberry Pi 4.
            time.sleep(10)

            # Logging to screen
            print('Logged in.')
            #print(driver.page_source)
            #sys.exit()
        # else:
        #     print('Already logged.')

        # Getting the website to check again
        # in case it was redirected to another website and
        # avoid using a timer for waiting for the login redirect. DIDN'T WORK
        appointment_url = base_url + '/' + appointment_url_id + '/appointment'
        driver.get(appointment_url)
        print('Checking for changes.')

        # # For debugging false positives.
        #with open('debugging/page_source.html', 'w', encoding='utf-8') as f:
        #    f.write(driver.page_source)

        # Getting main text
        main_page = driver.find_element(by=By.ID, value='main')

        # For debugging false positives.
        with open('debugging/main_page', 'w') as f:
            f.write(main_page.text)

        if "There are no available appointments" in main_page.text:
            print("There are no available appointments")
            send_message(current_time + ' There are no available appointments.')
            #time.sleep(1800)
            return

        dates_list = []

        try:
            print("Clicking on Calendar")
            driver.find_element(by=By.XPATH, value='//input[@id="appointments_consulate_appointment_date"]').click()
        except:
            print("Couldn't click on calendar")

        try:
            for i in range(4):
                month_element=driver.find_element(by=By.XPATH, value='//div[@class="ui-datepicker-group ui-datepicker-group-first"]//span[@class="ui-datepicker-month"]')
                dates_elements=driver.find_elements(by=By.XPATH, value='//div[@class="ui-datepicker-group ui-datepicker-group-first"]//table[@class="ui-datepicker-calendar"]//td[@data-handler="selectDay"]')

                # # For debugging false positives.
                with open('debugging/page_source_cal.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                
                dates_list = []

                for date_elm in dates_elements:
                    dates_list.append(date_elm.text)

                #print(month_element.text)
                #print(dates_list)

                if dates_list:
                    if month_element.text == "June":
                        print('June Appointment found. Notifying it.')
                        send_message(current_time + ' Here is an screenshot.')
                        send_photo(driver.get_screenshot_as_png())
                    if month_element.text == "May":
                        print('May Appointment found. Notifying it.')
                        send_message(current_time + ' Here is an screenshot.')
                        send_photo(driver.get_screenshot_as_png())
                    print(current_time + ' - First Availability: ' + month_element.text + " : " + dates_list[0])
                    send_message(current_time + ' - First Availability: ' + month_element.text + " : " + dates_list[0])
                    break
                else:
                    driver.find_element(by=By.XPATH, value='//span[@class="ui-icon ui-icon-circle-triangle-e"]').click()
            if not dates_list:
                print(current_time + " No Appointment till July..")
                send_message(current_time + " No Appointment till July..")
        except Exception as e:
            print(e)
            send_message(current_time + ' Script failed, trying again....')
            print("Script failed, trying again....")

        # If the "no appointment" text is not found return True. A change was found. 
        return no_appointment_text not in dates_list

    # To run Chrome in a virtual display with xvfb (just in Linux)
    # display = Display(visible=0, size=(800, 600))
    # display.start()

    seconds_between_checks = 10 * 60

    # Setting Chrome options to run the scraper headless.
    chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    chrome_options.add_argument("--headless") # Comment for visualy debugging

    # Initialize the chromediver (must be installed and in PATH)
    # Needed to implement the headless option
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    while True:
        try:
            current_time = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
            print(f'Starting a new check at {current_time}.')
            if has_website_changed():
                print("Checking finished")
                #print('Appointment found. Notifying it.')
                #send_message(current_time + ' Here is an screenshot.')
                #send_photo(driver.get_screenshot_as_png())

                # Closing the driver before quitting the script.
                #driver.close()
                #exit()
                # print(f'No change was found. Checking again in {seconds_between_checks} seconds.')
                # time.sleep(seconds_between_checks)
            for seconds_remaining in range(int(seconds_between_checks), 0, -1):
                sys.stdout.write('\r')
                sys.stdout.write(
                    f'Checking again in {seconds_remaining} seconds.')
                sys.stdout.flush()
                time.sleep(1)
            print('\n')
        except:
            print("Check failed, trying again......")
            send_message(current_time + " Check failed, trying again......")



def main():
    base_url = f'https://ais.usvisa-info.com/' + country_code + '/niv/schedule'
    # Checking for an appointment
    text = 'There are no available appointments at this time.'


    run_visa_scraper(base_url, text)

if __name__ == "__main__":
    main()
