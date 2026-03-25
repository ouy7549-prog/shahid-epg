import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🔒 بيانات حسابك الحقيقي (قم بتغييرها هنا)
USER_EMAIL = "tressanoiheisse-2431@yopmail.com"
USER_PASSWORD = "T123456t@123"

def extract_with_login():
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
        print("جاري فتح الموقع لتسجيل الدخول الحقيقي...")
        driver.get(url)
        wait = WebDriverWait(driver, 25)
        
        # 1️⃣ قبول الكوكيز (لإبعاد الشريط السفلي)
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            time.sleep(2)
        except:
            pass

        # 2️⃣ الضغط على زر Log In من النافذة المنبثقة
        try:
            print("الضغط على زر تسجيل الدخول...")
            # البحث عن الزر النصي أو الكلاس الخاص بـ Login
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')] | //a[contains(text(), 'Log in')]")))
            login_btn.click()
            time.sleep(5)
        except:
            print("لم نجد زر Login المباشر، سنحاول البحث عنه عبر الـ Header...")
            try:
                login_header = driver.find_element(By.CSS_SELECTOR, ".login-btn, .sign-in-up")
                login_header.click()
                time.sleep(5)
            except:
                print("فشل العثور على زر تسجيل الدخول.")

        # 3️⃣ كتابة الإيميل والباسورد
        try:
            print("جاري تعبئة بيانات الحساب الحقيقي...")
            # السيلينيوم يبحث عن حقول الإدخال ويكتب فيها
            email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']")))
            email_field.send_keys(USER_EMAIL)
            
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            password_field.send_keys(USER_PASSWORD)
            time.sleep(1)
            
            # الضغط على زر Submit / Sign In
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .submit-btn")
            submit_btn.click()
            print("✅ تم إرسال بيانات الدخول! ننتظر تحميل الصفحة...")
            time.sleep(15) # انتظار تسجيل الدخول الفعلي وإعادة التوجيه
        except Exception as e:
            print(f"⚠️ فشل تعبئة الحقول: {e}")

        # التقاط صورة لنتأكد هل سجل الدخول؟
        driver.save_screenshot("debug_screenshot.png")

        # 4️⃣ التنصت على الشبكة لسحب الرابط
        print("الانتظار 30 ثانية لاستخراج الرابط من الشبكة...")
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

# التشغيل وحفظ النتيجة
found_link = extract_with_login()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 مبروك! نجح تسجيل الدخول الحقيقي ووجدنا الرابط: {found_link}")
    else:
        f.write("# لم يتم العثور على الرابط حتى بعد محاولة تسجيل الدخول.")
        print("❌ لم نتمكن من العثور على الرابط في السجلات.")
