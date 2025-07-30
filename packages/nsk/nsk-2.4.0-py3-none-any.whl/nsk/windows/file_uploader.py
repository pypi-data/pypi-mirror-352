import os
import time
import win32gui
from nsk.windows.base import Windows
from pywintypes import error
from nsk.utils.decorator import retry_if_exception

class FileUploader(Windows):
    def __init__(self,window_name = None, timeout: float = 5, retry_interval: float = 0.5):
        super().__init__("#32770", window_name, timeout, retry_interval)
        
    @retry_if_exception(
        exceptions=(
            error
        ),
        failure_return=False
    )
    def upload(self,path: str) -> bool:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File Not Found Error: {path} ")
        edit = self.find_child(class_name="Edit")
        edit.set_text(path)
        upload = self.find_child(class_name="Button",text="&Open")
        upload.click()
        timeout = time.time() + self.timeout
        while time.time() < timeout:
            if not win32gui.IsWindow(self.hwnd):
                return True 
            time.sleep(self.retry_interval)
        return False