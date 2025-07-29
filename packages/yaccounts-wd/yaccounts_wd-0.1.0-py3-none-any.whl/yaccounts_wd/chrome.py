import platform
import shutil
import subprocess

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from .yutils import get_app_data_dir
from .run_report import _new_workday_tab


def get_default_chrome_path():
    system = platform.system()
    if system == "Windows":
        return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif system == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Linux":
        return (
            shutil.which("google-chrome")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


# def get_default_chrome_user_data_dir():
#     system = platform.system()
#     if system == "Windows":
#         return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
#     elif system == "Darwin":
#         return os.path.expanduser("~/Library/Application Support/Google/Chrome")
#     elif system == "Linux":
#         return os.path.expanduser("~/.config/google-chrome")
#     else:
#         raise RuntimeError(f"Unsupported platform: {system}")


def run_chrome(port=9222):
    chrome_path = get_default_chrome_path()
    subprocess.Popen(
        [
            chrome_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={get_app_data_dir() / 'chrome-user-data'}",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    chrome_options = Options()
    chrome_options.debugger_address = f"127.0.0.1:{port}"

    driver = webdriver.Chrome(options=chrome_options)
    _new_workday_tab(driver)


def get_chrome_webdriver(profile_name="Default", remote_debugging_port=9222):
    # Connect to running Chrome
    chrome_options = Options()
    chrome_options.debugger_address = f"127.0.0.1:{remote_debugging_port}"

    driver = webdriver.Chrome(options=chrome_options)

    return driver
