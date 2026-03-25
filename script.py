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
    
    # تحديد دقة الشاشة لتكون مماثلة للصورة المرفوعة
    driver.set_window_size(1920, 1080)
    
    found_url = None

    try:
        print("جاري فتح الموقع...")
        driver.get(url)
        wait = WebDriverWait(driver, 25) # زيادة وقت الانتظار قليلاً
        
        # 1️⃣ الضغط على Accept All Cookies (تأكد من وجود المحدد الصحيح)
        try:
            print("تحرير المتصفح من شريط الكوكيز...")
            # المحدد الأكثر دقة لشريط الكوكيز (OneTrust)
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            print("✅ تم قبول الكوكيز.")
            time.sleep(3)
        except:
            print("لم يتم العثور على شريط الكوكيز.")

        # 2️⃣ محاولة إغلاق نافذة تسجيل الدخول المنبثقة (الضربة القاضية)
        try:
            print("محاولة إغلاق نافذة تسجيل الدخول المنبثقة (X)...")
            
            # 🎯 هذا هو المحدد البرمجي الدقيق لزر الـ X الذي رأيناه في الصورة:
            # هو عنصر button يحتوي على عنصر span بداخله الرمز x، وموجود داخل نافذة تسجيل الدخول
            close_btn_selector = "button.vjs-close-button > span[aria-hidden='true']"
            
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_btn_selector)))
            
            # الضغط باستخدام الـ JavaScript لضمان التنفيذ حتى في الوضع الصامت
            driver.execute_script("arguments[0].click();", close_btn)
            print("✅✅✅ تم إغلاق النافذة بنجاح! المفترض البث بدأ الآن.")
            time.sleep(5) # الانتظار قليلاً ليتحدث المتصفح
        except Exception as e:
            print(f"لم نجد زر الإغلاق بالمحدد الجديد، سنجرب بالـ JavaScript العام: {e}")
            try:
                driver.execute_script("document.querySelector(\"button[aria-label='Close']\").click();")
                time.sleep(5)
            except:
                pass

        # 📸 التقاط صورة الآن للتأكد من اختفاء النافذة
        print("📸 جاري التقاط صورة جديدة للتأكد من اختفاء النافذة...")
        driver.save_screenshot("after_close_screenshot.png")

        # 3️⃣ التنصت على الشبكة واستخراج الرابط
        print("الانتظار 30 ثانية لتحميل البث واستخراج الرابط من الشبكة...")
        time.sleep(30) 
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    # البحث عن روابط الـ .m3u8 أو .mpd الرسمية من Akamai
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

# حفظ الملف النهائي وتحديث m3u
with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 نجاح باهر! تم العثور على الرابط وتحديث الملف: {found_link}")
    else:
        # هذه الرسالة تظهر في ملف الـ m3u إذا فشل
        f.write("# لم يتم العثور على الرابط بعد إغلاق النافذة. ربما يتطلب تسجيل دخول حقيقي.")
        print("❌ لم نتمكن من العثور على الرابط في سجلات الشبكة.")
