import time
import logging
import win32api
import win32gui
import win32con
from typing import List,Tuple
from selenium.common.exceptions import TimeoutException

class Windows:
    def __init__(
        self, 
        class_name: str | None = None, 
        window_name: str | None = None, 
        timeout: float = 5.0, 
        retry_interval: float = 0.5,
        log_name: str | None = None,
    ):
        self.class_name = class_name
        self.window_name = window_name
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.hwnd = self._init_window()
        self.logger = logging.getLogger(log_name)
    
    @classmethod
    def from_hwnd(cls, hwnd: int, log_name: str | None = None):
        if not hwnd or not win32gui.IsWindow(hwnd):
            raise ValueError(f"Invalid Window Handle: {hwnd}")
        # --
        instance = cls.__new__(cls)
        instance.hwnd = hwnd
        instance.class_name = None
        instance.window_name = None
        instance.timeout = 5.0
        instance.retry_interval = 0.5
        instance.logger = logging.getLogger(log_name)
        try:
            instance.class_name = win32gui.GetClassName(hwnd)
            instance.window_name = win32gui.GetWindowText(hwnd)
        except Exception as e:
            instance.logger.warning(f"Could not retrieve window info: {e}")
        return instance
        

    def _init_window(
        self, 
    ) -> int:
        start_time = time.time()
        while True:
            if hwnd := win32gui.FindWindow(self.class_name, self.window_name):
                return hwnd
            if (time.time() - start_time) > self.timeout:
                raise TimeoutException("Window not found within the timeout period.")
            time.sleep(self.retry_interval)

    def enum_child_windows(self) -> List[Tuple[int, str, str]]:
        """Liệt kê tất cả child windows và controls"""
        def callback(hwnd: int, results: list):
            class_name = win32gui.GetClassName(hwnd)
            window_text = win32gui.GetWindowText(hwnd)
            results.append((hwnd, class_name, window_text))
            return True
        time.sleep(self.retry_interval)
        child_windows = []
        win32gui.EnumChildWindows(self.hwnd, callback, child_windows)
        return child_windows
    
    def find_child(self, class_name: str = None, text: str = None):
        time.sleep(self.retry_interval)
        children = self.enum_child_windows()
        for hwnd, child_class, child_text in children:
            if class_name and class_name != child_class:
                continue
            if text and text != child_text:
                continue
            return self.__class__.from_hwnd(hwnd)
        
    def find_children(self, class_name: str = None, text: str = None) -> List['Windows']:
        time.sleep(self.retry_interval)
        windows = []
        children = self.enum_child_windows()
        for hwnd, child_class, child_text in children:
            if class_name and class_name != child_class:
                continue
            if text and text != child_text:
                continue
            windows.append(self.__class__.from_hwnd(hwnd))
        return windows
    
    def set_text(
        self,
        message:str,
        wparam:int = 0,
    ) -> int:    
        return win32gui.SendMessage(
            self.hwnd,
            win32con.WM_SETTEXT,    
            wparam,
            message,
        )

    def click(self, double_click: bool = False): 
        win32gui.SetForegroundWindow(self.hwnd)
        x_screen, y_screen = win32gui.ClientToScreen(self.hwnd, (0, 0))
        win32api.SetCursorPos((x_screen, y_screen))
        count = 2 if double_click else 1
        for _ in range(count):
            win32gui.PostMessage(self.hwnd, win32con.BM_CLICK, 0, 0)
            time.sleep(0.05)
        

    def minimize(self):
        """Minimize window"""
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)

    def maximize(self):
        """Maximize window"""
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)

    def restore(self):
        """Restore window to its previous size"""
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)

    def close(self):
        """Close window"""
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
    
__all__ = ['Windows']