from typing import Optional
import time
import os
from curl_cffi import requests
from misato.config import HEADERS, RETRY, DELAY, TIMEOUT
from misato.logger import logger
from DrissionPage import ChromiumPage, ChromiumOptions


def get_chromium_options(browser_path: str, arguments: list) -> ChromiumOptions:
    """
    Configures and returns Chromium options.

    :param browser_path: Path to the Chromium browser executable.
    :param arguments: List of arguments for the Chromium browser.
    :return: Configured ChromiumOptions instance.
    """
    options = ChromiumOptions().auto_port()
    options.set_paths(browser_path=browser_path)
    for argument in arguments:
        options.set_argument(argument)
    return options

browser_path = os.getenv('CHROME_PATH', "/usr/bin/google-chrome")

arguments = [
    "-no-first-run",
    "-force-color-profile=srgb",
    "-metrics-recording-only",
    "-password-store=basic",
    "-use-mock-keychain",
    "-export-tagged-pdf",
    "-no-default-browser-check",
    "-disable-background-mode",
    "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
    "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
    "-deny-permission-prompts",
    "-disable-gpu",
    "-accept-lang=en-US",
]

options = get_chromium_options(browser_path, arguments)

class HttpClient:
    def get(self, url: str, cookies: Optional[dict] = None, retries: int = RETRY, delay: int = DELAY, timeout: int = TIMEOUT) -> Optional[bytes]:
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=HEADERS, cookies=cookies, timeout=timeout, verify=False)
                return response.content
            except Exception as e:
                logger.error(f"Failed to fetch data (attempt {attempt + 1}/{retries}): {e} url is: {url}")
                time.sleep(delay)
        logger.error(f"Max retries reached. Failed to fetch data. url is: {url}")
        return None

    def post(self, url: str, data: dict, cookies: Optional[dict] = None, retries: int = RETRY, delay: int = DELAY, timeout: int = TIMEOUT) -> Optional[requests.Response]:
        for attempt in range(retries):
            try:
                response = requests.post(url=url, data=data, headers=HEADERS, cookies=cookies, timeout=timeout, verify=False)
                return response
            except Exception as e:
                logger.error(f"Failed to post data (attempt {attempt + 1}/{retries}): {e} url is: {url}")
                time.sleep(delay)
        logger.error(f"Max retries reached. Failed to post data. url is: {url}")
        return None

    def get_page_html(self, url: str, cookies: Optional[str]) -> Optional[str]:
        driver = ChromiumPage(addr_or_opts=options)
        if cookies:
            driver.set.cookies(cookies)
        driver.get_tab().set.window.mini()
        try:
            driver.get(url)
            source = driver.html
            return source
        except Exception as e:
            logger.error("An error occurred: %s", str(e))
        finally:
            logger.info('Closing the browser.')
            driver.quit()
