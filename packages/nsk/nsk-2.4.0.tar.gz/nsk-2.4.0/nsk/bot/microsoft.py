import os
import re
import time
from urllib.parse import urlparse
import threading
from typing import List, Tuple
from urllib.parse import unquote
from nsk.windows import FileUploader
import pandas as pd
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from nsk.bot.base import IBot
from nsk.utils import retry_if_exception

class Microsoft365(IBot):
    def __init__(self, username: str, password: str, **kwargs):
        super().__init__(**kwargs)
        self.url = "https://login.microsoftonline.com/"
        self.authenticated = self._authentication(username, password)
        if not self.authenticated:
            raise ConnectionRefusedError("The username or password is incorrect.")
    
    @retry_if_exception(
        exceptions=(
            StaleElementReferenceException,
            ElementClickInterceptedException,
            TimeoutException,
        ),
        failure_return=False,
    )
    def _authentication(self, username: str, password: str) -> bool:
        self.navigate(self.url)
        time.sleep(self.retry_interval)
        if self.browser.current_url.startswith("https://m365.cloud.microsoft/?auth="):
            self.logger.info("Authenticated")
            return True
        try:
            # -- Username
            time.sleep(self.retry_interval)
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"]'))
            ).send_keys(username)
            # -- Next
            time.sleep(self.retry_interval)
            self.wait.until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            ).click()
            # -- Password
            time.sleep(self.retry_interval)
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]'))
            ).send_keys(password)
            # -- Sign in
            time.sleep(self.retry_interval)
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='idSIButton9']"))
            ).click()
        finally:
            time.sleep(self.retry_interval)
            try:
                # -- Alert
                alert = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='alert']"))
                )
                if alert.text:
                    raise ConnectionRefusedError(alert.text)
                return self._authentication(username, password)
            except TimeoutException:
                # -- Stay signed in
                self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='idSIButton9']"))
                ).click()
        time.sleep(self.retry_interval)
        if not self.browser.current_url.startswith("https://m365.cloud.microsoft/?auth="):
            raise ConnectionRefusedError("Authentication failed")
        self.logger.info("Authenticated to Microsoft 365")
        return True


class SharePoint(Microsoft365):
    redundant_name = r'[\ue000-\uf8ff]|\n|Press C to open file hover card'
    _upload_lock = threading.Lock()

    def __init__(self, url: str, username: str, password: str, **kwargs):
        super().__init__(
            username=username,
            password=password,
            **kwargs
        )
        self.url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.navigate(self.url)
        if not self.browser.current_url.startswith(self.url) or self.browser.current_url.startswith("https://login.microsoftonline.com"):
            raise ConnectionRefusedError("Access to SharePoint site was denied.")

    def navigate(self, url, wait_for_complete = True):
        super().navigate(url, wait_for_complete)
        try:
            ms_error_header = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,"div[id='ms-error-header']"))
            )
            self.logger.error(ms_error_header.text)
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,"div[id='ms-error'] a"))
            ).click()
            time.sleep(self.retry_interval)
            while self.browser.execute_script("return document.readyState") != "complete":
                continue
            time.sleep(self.retry_interval)
            return self.navigate(url, wait_for_complete)
        except Exception:
            pass
 
    @retry_if_exception(
        exceptions=(
            StaleElementReferenceException,
            ElementClickInterceptedException,
            TimeoutException,
        ),
        failure_return=pd.DataFrame()
    )
    def info(self,site_url:str) -> pd.DataFrame:
        """ Lấy danh sách file và folder từ 'site_url' trên SharePoint.
        Args:
            site_url (str): Đường dẫn URL của site SharePoint cần lấy thông tin.
        Returns:
            pd.DataFrame: DataFrame chứa thông tin các file và folder khớp với mẫu, 
        """
        self.logger.info(f"Get info {site_url}")
        result = []
        self.navigate(site_url)
        rows = self.wait.until(
            method = EC.any_of(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div[id^='virtualized-list'][role='row']")),
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div[data-automationid='DetailsRow'][role='row']")),
            )
        )
        for row in rows:
            # -- Type
            type_el = row.find_element(
                by = By.CSS_SELECTOR,
                value="div[data-automationid='field-DocIcon'],div[data-automation-key^='fileTypeIconColumn']"
            )
            try:
                type_name = type_el.find_element(By.TAG_NAME,'img').get_attribute('alt')
            except NoSuchElementException:
                type_name = None
            # -- Name
            name_el = row.find_element(
                by = By.CSS_SELECTOR,
                value="div[data-automationid='field-LinkFilename'],div[data-automation-key^='displayNameColumn']"
            )
            name = name_el.text
            name = re.sub(self.__class__.redundant_name,'',name)
            # Agg
            result.append({
                "Type":type_name,
                "Name":name,
            })
        return pd.DataFrame(result)

    @retry_if_exception(
        exceptions=(
            StaleElementReferenceException,
            ElementClickInterceptedException,
            TimeoutException,
        ),
        failure_return=[(None,None,"Download Error"),]
    )
    def download(self,site_url:str,file_pattern:str) -> List[Tuple[str | None,str,str]]:
        self.logger.info(f"Search {file_pattern} - {site_url}")
        result = []
        self.navigate(site_url)
        # Folder
        folder_found = False
        folders: List[str] = file_pattern.split("/")[:-1]
        for step in folders:
            time.sleep(self.retry_interval)
            gridcells = self.wait.until(
                EC.any_of(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div[role='gridcell'][data-automationid='field-LinkFilename']")),
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div[role='gridcell'][data-automation-key^='displayNameColumn']")),
                )
            )
            for gridcell in gridcells:
                text = re.sub(self.__class__.redundant_name,'',gridcell.text)
                if re.match(step,text):
                    button = gridcell.find_element(
                        By.XPATH,
                        './/button | .//span[@role="button"]'
                    )
                    self.wait.until(EC.element_to_be_clickable(button)).click()
                    time.sleep(self.timeout)
                    folder_found = True
                    break
            time.sleep(self.retry_interval)  
        if not folder_found:
            raise LookupError(f"Folder Not Found: {file_pattern}")
        # File
        file: str = file_pattern.split("/")[-1]
        gridcells = self.wait.until(
            EC.any_of(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div[role='gridcell'][data-automationid='field-LinkFilename']")),
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div[role='gridcell'][data-automation-key^='displayNameColumn']")),
            )
        )
        for gridcell in gridcells:
            file_name = re.sub(self.__class__.redundant_name, '', gridcell.text)
            if re.match(file,file_name):
                button = gridcell.find_element(
                    By.XPATH,
                    './/button | .//span[@role="button"]'
                )
                self.wait.until(EC.element_to_be_clickable(button))
                time.sleep(self.retry_interval)
                # Copy Link
                link = None
                button.click()
                time.sleep(2)
                new_window = self.browser.window_handles[-1]  
                if new_window != self.root_window:
                    self.browser.switch_to.window(new_window)
                    while self.browser.execute_script("return document.readyState") != "complete":
                        time.sleep(self.retry_interval)
                    link = unquote(self.browser.current_url)
                    self.browser.close()
                    self.browser.switch_to.window(self.root_window)
                else:
                    close_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,"button[id='closeCommand']"))
                    )
                    time.sleep(self.retry_interval)
                    close_button.click()
                    time.sleep(self.timeout)
                # Download File
                ActionChains(self.browser).context_click(button).perform()
                download_btn = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,"button[data-automationid='downloadCommand']")
                    )
                )
                self.wait.until(EC.element_to_be_clickable(download_btn)).click()
                time.sleep(5)
                file_path, status = self.wait_for_download_to_finish()
                self.logger.info(f"Download {file_name}: {file_path if not status else status},")
                result.append((link,os.path.join(self.download_directory,file_path),status))
        return result
        
    @retry_if_exception(
        exceptions=(
            StaleElementReferenceException,
            ElementClickInterceptedException,
            TimeoutException,
        ),
        failure_return=False,
    )    
    def upload(self,site_url:str, path: str) -> bool:
        with self._upload_lock:
            path = os.path.abspath(path)
            if not os.path.isfile(path):
                raise FileNotFoundError(f"File Not Found Error: {path}")
            self.logger.info(f"Upload to {unquote(site_url)}")
            # ----- Close -----
            time.sleep(self.retry_interval)
            while True:
                try:
                    uploader = FileUploader("Open")
                    uploader.close()
                except TimeoutException:
                    break
            # ----- Open -----
            self.navigate(site_url)
            time.sleep(self.retry_interval)
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,"button[data-id='UploadCommand']"))
            ).click()
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,f"button[data-automationid='uploadFileCommand']"))
            ).click()
            # --
            uploader = FileUploader("Open")
            if not uploader.upload(path):
                self.logger.error(f"Failed to upload {path}")
                return False
            time.sleep(1)
            message = self.wait.until(
                EC.presence_of_element_located((By.XPATH,"//div[@role='alert']//div[starts-with(@class, 'messageRow')]"))
            ).text
            if not message.startswith((
                f"Uploaded {os.path.basename(path)} to ",
                f"Uploading {os.path.basename(path)} to "
            )):
                self.logger.error(message)
                return False
            self.logger.info(message)
            return True
            
            
        
class PowerApp(Microsoft365):
    def __init__(self, url: str, username365:str,password365:str,username: str | None = None , password: str | None = None, **kwargs):
        """
        Args:
            url (str): PowerApp URL
            username365 (str): Microsoft 365 username
            password365 (str): Microsoft 365 password
            username (str | None, optional): PowerApp username. Defaults to None.
            password (str | None, optional): PowerApp password. Defaults to None.
        """
        super().__init__(
            username=username365,
            password=password365,
            **kwargs
        )
        self.url = url
        time.sleep(self.retry_interval)
        self.navigate(self.url)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[id='progressBarWrapper']")))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[id='progressBarWrapper']")))
        self.wait.until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[id='fullscreen-app-host']"))
        )
        if username and password:
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,"input[appmagic-control='idtextbox']"))
            ).send_keys(username)
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,"input[appmagic-control='pwtextbox']"))
            ).send_keys(password)
            try:
                login_btn = self.wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(@class, 'appmagic-button-container') and contains(@class, 'no-focus-outline')]"
                        "[.//div[text()='Login']]"
                    ))
                )
                login_btn.click()
                self.wait.until(EC.invisibility_of_element(login_btn))
            except TimeoutException:
                raise ConnectionRefusedError("Authentication failed ")
            self.logger.info("Authenticated to PowerApp")


__all__ = ["Microsoft365","SharePoint","PowerApp"]
