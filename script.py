import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 🔑 القيمة الطويلة التي استخرجتها أنت بنفسك من المتصفح
MY_SECRET_TOKEN = "09AKhCRwgpB0dkdhm6yByLD9wDTw3fe-eF9CH7i1ccQZvjVqSzUX8HskV0vWy95iiljDk2w_D9bz-_vOCBcDOCYYE"

def extract_with_full_auth():
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
        print("🚀 فتح الموقع لحقن الهوية الشاملة...")
        driver.get("https://www.dubaiplus.net")
        time.sleep(5)

        # 1️⃣ حقن التوكن في الـ Cookies بـ 4 أسماء مشهورة دفعة واحدة لتفادي الخطأ
        possible_cookie_names = ["access_token", "jwt", "session_token", "id_token", "auth_token"]
        for name in possible_cookie_names:
            try:
                driver.add_cookie({
                    "domain": ".www.dubaiplus.net",
                    "name": name,
                    "value": MY_SECRET_TOKEN,
                    "path": "/"
                })
            except:
                continue

        # 2️⃣ حقن التوكن في الـ LocalStorage والـ SessionStorage عبر جافا سكريبت
        print("💾 جاري حقن الهوية في الـ Local Storage...")
        driver.execute_script(f"""
            // تجربة كل المفاتيح الشائعة التي تستخدمها المواقع الحديثة
            localStorage.setItem('access_token', '{MY_SECRET_TOKEN}');
            localStorage.setItem('jwt', '{MY_SECRET_TOKEN}');
            localStorage.setItem('token', '{MY_SECRET_TOKEN}');
            localStorage.setItem('user_session', '{MY_SECRET_TOKEN}');
            
            sessionStorage.setItem('access_token', '{MY_SECRET_TOKEN}');
            sessionStorage.setItem('jwt', '{MY_SECRET_TOKEN}');
        """)

        print("🔄 تحديث الصفحة بالهوية الجديدة الشاملة...")
        driver.get(url)
        time.sleep(20) # وقت كافٍ للموقع للتعرف على الجلسة وتحميل البث

        # التقاط صورة للتأكد
        driver.save_screenshot("debug_screenshot.png")

        print("📡 التنصت على سجلات الشبكة...")
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
found_link = extract_with_full_auth()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 مبروك! نجح الحقن الشامل وحصلنا على الرابط: {found_link}")
    else:
        f.write("# لم نجد الرابط بعد محاولة الحقن الشامل.")
        print("❌ لم يتم العثور على الرابط.")
