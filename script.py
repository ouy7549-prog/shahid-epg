import time
import json
import os
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

    # 🚀 تشغيل صامت للـ GitHub Actions
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # تحديد دقة الشاشة لتكون الصورة واضحة
    driver.set_window_size(1920, 1080)
    
    found_url = None

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20) # الانتظار حتى 20 ثانية
        
        # 1️⃣ الضغط على Accept All Cookies
        try:
            print("تحرير المتصفح من شريط الكوكيز...")
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            time.sleep(3)
        except:
            print("لم يتم العثور على شريط الكوكيز.")

        # 2️⃣ محاولة إغلاق نافذة تسجيل الدخول (X)
        try:
            print("محاولة إغلاق نافذة تسجيل الدخول المنبثقة...")
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close'], .close-button, .popup-close, .vjs-close-button")))
            close_btn.click()
            print("✅ تم إغلاق النافذة بنجاح!")
            time.sleep(5) # الانتظار قليلاً بعد الإغلاق
        except:
            print("⚠️ لم نجد زر الإغلاق، سنتابع...")

        # 📸 3️⃣ التقاط صورة الآن (Screenshot) - هذه هي الخطوة السحرية!
        print("📸 جاري التقاط صورة لشاشة المتصفح الصامت...")
        driver.save_screenshot("debug_screenshot.png")
        print("📸 تم حفظ الصورة باسم debug_screenshot.png")

        # 4️⃣ التنصت على الشبكة واستخراج الرابط
        print("الانتظار 30 ثانية لتحميل البث واستخراج الرابط...")
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

# التشغيل النهائي وحفظ النتيجة
found_link = extract_from_dubaiplus()

# حفظ الملف النهائي
with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 نجاح! تم العثور على الرابط: {found_link}")
    else:
        f.write("# لم يتم العثور على الرابط. ربما يتطلب الموقع تسجيل دخول حقيقي.")
        print("❌ لم نتمكن من العثور على الرابط في سجلات الشبكة.")
