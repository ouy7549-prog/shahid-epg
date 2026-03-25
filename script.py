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

    # 🚀 تشغيل صامت ومناسب لـ GitHub Actions
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # 🚫 تجاوز الحماية
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    found_url = None

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # 1️⃣ الضغط على Accept All Cookies
        try:
            print("تحرير المتصفح من شريط الكوكيز...")
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            time.sleep(2)
        except:
            print("لم يتم العثور على شريط الكوكيز.")

        # 2️⃣ إغلاق نافذة تسجيل الدخول المنبثقة (الضغط على X)
        try:
            print("محاولة إغلاق نافذة تسجيل الدخول المنبثقة...")
            # جلب الزر عبر الـ Aria-label أو الـ Class
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close'], .close-button, .popup-close")))
            close_btn.click()
            print("✅ تم إغلاق النافذة بنجاح!")
            time.sleep(3)
        except:
            print("⚠️ لم ننجح في إغلاق الـ Pop-up بالطريقة العادية، سنجرب بالـ JavaScript...")
            try:
                driver.execute_script("document.querySelector(\"button[aria-label='Close']\").click();")
                time.sleep(3)
            except:
                print("⚠️ فشلت محاولة إغلاق النافذة بالكامل.")

        # 3️⃣ الانتظار والتنصت على الشبكة بحثاً عن الروابط
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
                        break # نكتفي بأول رابط نجده
            except:
                continue

    finally:
        driver.quit()
        
    return found_url

# التشغيل النهائي وحفظ النتيجة
found_link = extract_from_dubaiplus()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 نجاح! تم العثور على الرابط: {found_link}")
    else:
        f.write("# لم يتم العثور على الرابط. ربما يتطلب الموقع تسجيل دخول حقيقي.")
        print("❌ لم نتمكن من العثور على الرابط في سجلات الشبكة.")
