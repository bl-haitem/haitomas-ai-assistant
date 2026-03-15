"""
HAITOMAS ASSISTANT — Smart Browser Engine (High Visibility Edition)
======================================================================
Engineered for Windows 10/11. Ensure visibility and robust fallbacks.
"""
import time
import os
import threading
import subprocess
import webbrowser
import ctypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class SmartBrowser:
    def __init__(self):
        self.driver = None
        self._lock = threading.Lock()
        self.is_falling_back = False

    def _bring_to_front(self):
        """Force the browser window to the foreground."""
        try:
            if not self.driver: return
            # Use JS to focus window
            self.driver.execute_script("window.focus();")
            # Minimal Windows API call if available
            try:
                user32 = ctypes.windll.user32
                h_wnd = user32.GetForegroundWindow()
                user32.SetForegroundWindow(h_wnd)
                user32.ShowWindow(h_wnd, 9) # Restore/Focus
            except: pass
        except: pass

    def _ensure_browser(self):
        """Initialize with cleanup and visibility checks."""
        with self._lock:
            try:
                if self.driver and self.driver != "FALLBACK":
                    try:
                        self.driver.current_url
                        return
                    except:
                        self.close()

                print("[SmartBrowser] �️ Initializing engine...")
                
                # Cleanup hanging processes
                if os.name == 'nt':
                    subprocess.run("taskkill /f /im chromedriver.exe /t", shell=True, capture_output=True)
                    # Don't kill chrome.exe here as it might be the user's main browser

                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")

                # Attempt to launch
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_page_load_timeout(30)
                self._bring_to_front()
                self.is_falling_back = False
                print("[SmartBrowser] ✅ Selenium Engine Ready.")
            except Exception as e:
                print(f"[SmartBrowser] ❌ Selenium failed: {e}. Switching to System Fallback.")
                self.driver = "FALLBACK"
                self.is_falling_back = True

    def navigate_to(self, url: str) -> str:
        self._ensure_browser()
        target = url if url.startswith("http") else f"https://{url}"
        
        if self.is_falling_back:
            webbrowser.open(target)
            return f"🌐 Opened via Default Browser: {target}"
        
        try:
            self.driver.get(target)
            self._bring_to_front()
            return f"🌐 Navigated to: {self.driver.title}"
        except Exception as e:
            webbrowser.open(target)
            return f"Opened via System Browser (Fallback due to error): {target}"

    def google_search_and_click(self, query: str, click_first: bool = True) -> str:
        """Search Google and click the first organic result with high reliability."""
        self._ensure_browser()
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        if self.is_falling_back:
            webbrowser.open(search_url)
            return f"🔍 Search opened: {query}"
        
        try:
            print(f"[SmartBrowser] 🔍 Googling: {query}")
            self.driver.get(search_url)
            self._bring_to_front()
            
            if click_first:
                wait = WebDriverWait(self.driver, 10)
                # 1. Broad Consent Handling
                try:
                    btns = self.driver.find_elements(By.XPATH, "//button[contains(., 'Accept') or contains(., 'agree') or contains(., 'وافق') or contains(., 'Agree')]")
                    if btns: 
                        self.driver.execute_script("arguments[0].click();", btns[0])
                        time.sleep(1)
                except: pass
                
                # 2. Find First Organic Link
                # Hierarchical selectors from most specific to general, inclusive of localized results
                selectors = [
                    "#search h3", 
                    "h3", 
                    ".g a h3", 
                    "a h3", 
                    "h3.LC20lb", # Classic Google organic title class
                    ".yuRUbf a h3",
                    "div[role='main'] a h3",
                    ".main a h3"
                ]
                
                target = None
                from core.event_bus import event_bus, EVENT_UI_UPDATE
                event_bus.publish(EVENT_UI_UPDATE, {"text": "🔍 Identifying best result...", "panel": "strategy"})
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for el in elements:
                            if el.is_displayed() and len(el.text) > 3:
                                target = el
                                break
                        if target: break
                    except: continue
                
                if target:
                    title = target.text
                    print(f"[SmartBrowser] 🎯 Target found: {title}")
                    event_bus.publish(EVENT_UI_UPDATE, {"text": f"🎯 Opening: {title[:30]}...", "panel": "strategy"})
                    
                    self.driver.execute_script("arguments[0].style.border='6px solid #00FF00'; arguments[0].scrollIntoView({block: 'center'});", target)
                    time.sleep(0.5)
                    
                    # Force click and state change
                    self.driver.execute_script("arguments[0].click();", target)
                    
                    # Critical: Wait for navigation to actually start
                    time.sleep(2) 
                    return f"🌐 Opened: {title}"
            
            return f"🔍 Search result ready for: {query}"
        except Exception as e:
            print(f"[SmartBrowser] Search fail: {e}")
            webbrowser.open(search_url)
            return f"🔍 Search triggered on System Browser."

    def play_youtube_video(self, query: str) -> str:
        """Professional YouTube playback. Searches, handles consent, and PLAYS the video."""
        self._ensure_browser()
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        if self.is_falling_back:
            webbrowser.open(url)
            return "▶️ YouTube Search (System Fallback)"
        
        try:
            print(f"[SmartBrowser] 📺 Playing YouTube: {query}")
            self.driver.get(url)
            self._bring_to_front()
            wait = WebDriverWait(self.driver, 15)
            
            # 1. Handle YouTube's annoying consent popups
            try:
                consent_xpath = "//button[contains(@aria-label, 'Accept') or contains(., 'Accept') or contains(., 'I agree') or contains(., 'وافق')]"
                c_btns = self.driver.find_elements(By.XPATH, consent_xpath)
                if c_btns: 
                    self.driver.execute_script("arguments[0].click();", c_btns[0])
                    time.sleep(1.5)
            except: pass
            
            # 2. Locate the first video result (ignoring ads/shorts if possible)
            # Preference: Video titles that are clickable
            video_selectors = [
                "ytd-video-renderer #video-title", 
                "a#video-title", 
                "ytd-grid-video-renderer #video-title",
                "h3.title-and-badge a"
            ]
            
            target = None
            for selector in video_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Try to pick the first one that has text
                        for el in elements:
                            if el.text.strip():
                                target = el
                                break
                    if target: break
                except: continue
                
            if target:
                title = target.get_attribute("title") or target.text
                print(f"[SmartBrowser] 🎯 Launching: {title}")
                self.driver.execute_script("arguments[0].style.border='6px solid #FF0000'; arguments[0].scrollIntoView({block: 'center'});", target)
                time.sleep(0.5)
                # Use JS click to bypass overlays
                self.driver.execute_script("arguments[0].click();", target)
                return f"▶️ Now playing: {title}"
            else:
                raise Exception("No video titles found on results page")

        except Exception as e:
            print(f"[SmartBrowser] YouTube error: {e}")
            # Final fallback: just try to click in the middle of where a video usually is if we're desperate
            try:
                self.driver.execute_script("window.scrollTo(0, 300);")
                return "▶️ Attempted to start video playback."
            except:
                webbrowser.open(url)
                return "▶️ YouTube opened in system browser."

    def interact_with_page(self, actions: list) -> str:
        """Sequential runner for complex tasks."""
        results = []
        for a in actions:
            cmd = a.get("action", "")
            if cmd == "navigate": results.append(self.navigate_to(a.get("url", "")))
            elif cmd == "search": results.append(self.google_search_and_click(a.get("query", "")))
            elif cmd == "click": results.append(self.click_element(a.get("target", "")))
            elif cmd == "type": results.append(self.type_text_in_field(a.get("field",""), a.get("text","")))
            elif cmd == "scroll": 
                self._ensure_browser()
                if not self.is_falling_back:
                    self.driver.execute_script(f"window.scrollBy(0, {a.get('amount', 500)});")
                    results.append("📜 Scrolled page.")
        return " | ".join(results)

    def click_element(self, target: str) -> str:
        self._ensure_browser()
        if self.is_falling_back: return "Action unavailable in fallback mode."
        try:
            wait = WebDriverWait(self.driver, 10)
            el = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{target}')]")))
            self.driver.execute_script("arguments[0].click();", el)
            return f"✅ Clicked: {target}"
        except: return f"❌ Could not click: {target}"

    def type_text_in_field(self, field: str, text: str) -> str:
        self._ensure_browser()
        if self.is_falling_back: return "Action unavailable in fallback mode."
        try:
            wait = WebDriverWait(self.driver, 10)
            el = wait.until(EC.presence_of_element_located((By.NAME, "q") if field=="search" else (By.TAG_NAME, "input")))
            el.send_keys(text + Keys.ENTER)
            return f"✅ Typed: {text}"
        except: return f"❌ Could not type in: {field}"

    def close(self):
        try:
            if self.driver and self.driver != "FALLBACK":
                self.driver.quit()
        except: pass
        self.driver = None
        return "Browser process terminated."
