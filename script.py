import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def extract_from_dubaiplus():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(1920, 1080)
    
    found_url = None

    try:
        print("جاري فتح الموقع...")
        driver.get(url)
        wait = WebDriverWait(driver, 25)
        
        # 1️⃣ قبول الكوكيز
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            time.sleep(3)
        except:
            pass

        # 2️⃣ إغلاق نافذة التسجيل الإجبارية (X)
        try:
            print("محاولة إغلاق النافذة المنبثقة...")
            # البحث عن الـ X بشتى الطرق الممكنة
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.vjs-close-button, button[aria-label='Close'], .popup-close")))
            driver.execute_script("arguments[0].click();", close_btn)
            print("✅ تم إغلاق النافذة!")
            time.sleep(5)
        except:
            print("⚠️ لم نجد زر الإغلاق، سنقوم بمحاولة إغلاقها قسراً عبر جافا سكريبت...")
            try:
                driver.execute_script("""
                    document.querySelectorAll("button[aria-label='Close'], .vjs-close-button").forEach(b => b.click());
                """)
                time.sleep(5)
            except:
                pass

        # 📸 التقاط الصورة بالاسم الصحيح الذي يبحث عنه ملف الـ YAML
        print("📸 جاري التقاط الصورة...")
        driver.save_screenshot("debug_screenshot.png")

        # 3️⃣ التنصت على الشبكة
        print("الانتظار 30 ثانية لاستخراج الرابط...")
        time.sleep(30) 
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    if "akamaized.net" in request_url and (".mpd" in request_url or ".m3u8" in request_url):
                        found_url = request_url
                        break
            except:
                continue

    finally:
        driver.quit()
        
    return found_url

# التشغيل النهائي
found_link = extract_from_dubaiplus()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 تم العثور على الرابط: {found_link}")
    else:
        f.write("# لم يتم العثور على الرابط بعد إغلاق النافذة. ربما يتطلب تسجيل دخول حقيقي.")
        print("❌ لم يتم العثور على الرابط في السجلات.")
