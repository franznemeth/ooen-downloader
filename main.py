import logging
import os
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def wait_for_download(issue_name: str, path: str, retry=10) -> None:
    # Muehlviertel is abbreviated to Mhlviertel for some reason
    issue_sanitized = issue_name.replace("ue", "")
    datestr = datetime.today().strftime("%Y%m%d")  # Get date today in yyyymmdd
    file_pattern = f"epaper_{issue_sanitized}_{datestr}.pdf"

    filestr = f"{path}/{file_pattern}"
    i = 0
    while i < retry:
        logger.debug(f"Trying to find file {filestr}. Try #{i + 1}")
        if os.path.exists(filestr):
            logger.info(f"Found {filestr}")
            return
        i += 1
        time.sleep(5)

    raise TimeoutError


def main():
    download_folder = os.getenv('OOEN_DOWNLOAD_DIR', '/download')
    ooen_username = os.getenv('OOEN_USERNAME', None)
    ooen_password = os.getenv('OOEN_PASSWORD', None)
    debug = os.getenv('DEBUG', False) == 'True'

    if None in [ooen_username, ooen_password]:
        logger.error(
            "Username and password have to be set via the OOEN_USERNAME and OOEN_PASSWORD environment variable")

    if debug:
        logger.setLevel(logging.DEBUG)

    options = Options()
    options.headless = not debug
    options.set_preference('browser.download.folderList', 2)  # custom location
    options.set_preference('browser.download.manager.showWhenStarting', False)
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.viewableInternally.enabledTypes", "")
    options.set_preference("pdfjs.disabled", True)  # disable the built-in PDF viewer
    options.set_preference('browser.download.dir', download_folder)
    options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
    browser = webdriver.Firefox(options=options)
    browser.implicitly_wait(10)
    browser.get("https://www.nachrichten.at")
    # Accept cookies
    WebDriverWait(browser, 15).until(
        expected_conditions.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Akzeptieren & Schließen")]'))
    ).click()

    # delete onetrust overlay
    onetrust = browser.find_element(By.ID, "onetrust-consent-sdk")
    browser.execute_script("var element = arguments[0]; element.parentNode.removeChild(element);", onetrust)

    # Click the login button in the top right
    WebDriverWait(browser, 10).until(
        expected_conditions.element_to_be_clickable((By.CLASS_NAME, "mainLogin__li--anmelden"))
    ).click()

    # Enter username
    username = browser.find_element(By.ID, "email")
    username.send_keys(ooen_username)
    browser.find_element(By.NAME, "go").click()

    # Enter password
    WebDriverWait(browser, 10).until(
        expected_conditions.visibility_of_element_located((By.ID, "password"))
    )
    password = browser.find_element(By.ID, "password")
    password.send_keys(ooen_password)
    browser.find_element(By.NAME, "go").click()
    # Wait for login to finish
    WebDriverWait(browser, 10).until(
        expected_conditions.invisibility_of_element((By.CLASS_NAME, "login--aktiv"))
    )

    # TODO: Find out why wait time before browser.get() is so long -> implicit wait?
    # Navigate to epaper instead of following the dropdown clickpath
    browser.get("https://www.nachrichten.at/nachrichten/epaper/")
    # Different issues of epaper
    issues = ["Linz", "Wels", "Steyr", "Muehlviertel", "Innviertel", "Salzkammergut"]
    # Iterate through all issues of OOEN and download the daily edition
    for issue in issues:
        issue_selector = browser.find_element(By.ID, "selectEpaperEdition")
        select = Select(issue_selector)

        WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "selectEpaperEdition"))
        )
        select.select_by_value(issue)
        logger.info(f"Selecting issue: {issue}")
        browser.find_element(By.CLASS_NAME, "epaperissue--hauptausgabe").click()
        logger.info(f"Clicking download button for issue: {issue}")
        WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, "//span[@class='btn-icon download']"))
        ).click()
        # Downloading issue
        try:
            WebDriverWait(browser, 15).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, '//button[contains(text(), "Download ganze Ausgabe")]'))
            ).click()
            logger.info(f"Starting download for issue: {issue}")
            wait_for_download(issue, download_folder)
        except TimeoutError as e:
            logger.error(f"Failed downloading {issue} in time. {e}")
        browser.get("https://www.nachrichten.at/nachrichten/epaper/")

    browser.close()


if __name__ == '__main__':
    main()
