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
    # لتتمكن من رؤية ما يحدث أثناء الاختبار على جهازك، قم بتعطيل الـ headless مؤقتاً
    # chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # 1️⃣ الضغط على Accept All Cookies لإزالة الشريط السفلي
        try:
            print("تحرير المتصفح من شريط الكوكيز...")
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            time.sleep(2)
        except:
            print("لم يتم العثور على شريط الكوكيز أو تم إغلاقه مسبقاً.")

        # 2️⃣ إغلاق نافذة تسجيل الدخول الإجبارية عبر الضغط على الـ (X)
        try:
            print("محاولة إغلاق نافذة تسجيل الدخول المنبثقة...")
            # البحث عن زر الـ X باستخدام الـ Class الخاص بالنافذة المنبثقة
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close'], .close-button, .popup-close")))
            close_btn.click()
            print("✅ تم إغلاق النافذة بنجاح!")
            time.sleep(2)
        except Exception as e:
            print(f"لم نتمكن من الضغط على زر الإغلاق بالطريقة العادية: {e}")
            # محاولة الإغلاق عبر الـ JavaScript إذا فشل الضغط العادي
            try:
                driver.execute_script("document.querySelector('.close-modal-selector').click();") 
            except:
                pass

        # 3️⃣ الانتظار لبدء البث والتنصت على الشبكة
        print("الانتظار لتحميل البث واستخراج الرابط...")
        time.sleep(20) 
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    if "akamaized.net" in request_url and (".mpd" in request_url or ".m3u8" in request_url):
                        return request_url
            except:
                continue
        return None

    finally:
        driver.quit()

found_link = extract_from_dubaiplus()
if found_link:
    print(f"🎯 تم العثور على الرابط المباشر: {found_link}")
else:
    print("❌ لم يتم العثور على الرابط بعد تخطي النوافذ.")
