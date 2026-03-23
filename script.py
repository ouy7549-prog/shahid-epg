import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_link_from_elahmad():
    # الرابط الجديد الذي وجدته
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # تفعيل مراقبة سجلات الشبكة
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري فحص صفحة الأحمد لاستخراج البث المباشر...")
        time.sleep(20) # ننتظر تحميل الصفحة والمشغل
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    
                    # نبحث عن امتدادات البث الشهيرة (m3u8 أو mpd)
                    if ".m3u8" in request_url or ".mpd" in request_url:
                        # نتأكد أنه ليس رابط إعلانات بل رابط بث حقيقي
                        if "elahmad.com" in request_url or "akamaized.net" in request_url:
                            return request_url
            except:
                continue
        return None
    finally:
        driver.quit()

found_url = get_link_from_elahmad()

# حفظ الرابط في الملف
with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_url:
        f.write(found_url)
        print(f"✅ تم العثور على الرابط بنجاح: {found_url}")
    else:
        f.write("# لم يتم العثور على الرابط تلقائياً من موقع الأحمد")
        print("❌ فشل العثور على الرابط في سجلات الشبكة لموقع الأحمد.")
