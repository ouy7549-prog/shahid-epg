import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_link_safe():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري فحص الشبكة بدقة (انتظار 20 ثانية)...")
        time.sleep(20) # وقت كافٍ للمشغل لطلب رابط الـ .mpd
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                # التأكد من وجود مفتاح 'request' ومفتاح 'url' قبل القراءة
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    
                    # البحث عن الرابط المطلوب
                    if "akamaized.net" in request_url and ".mpd" in request_url:
                        return request_url
            except (KeyError, TypeError):
                continue # تخطي السجلات غير المكتملة
        return None
    finally:
        driver.quit()

found_url = get_link_safe()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_url:
        f.write(found_url)
        print(f"تم بنجاح! الرابط: {found_url}")
    else:
        f.write("# الرابط لم يظهر في السجلات بعد، جرب زيادة وقت الانتظار")
        print("لم يتم العثور على الرابط المطلوب في حركة الشبكة.")
