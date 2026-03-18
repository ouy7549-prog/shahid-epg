import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_link_with_interaction():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # محاكاة متصفح حقيقي تماماً
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري تحميل الصفحة...")
        time.sleep(10)
        
        # محاولة الضغط في منتصف الشاشة لتفعيل المشغل إذا كان متوقفاً
        try:
            action = webdriver.ActionChains(driver)
            action.move_by_offset(500, 500).click().perform()
            print("تمت محاولة الضغط على المشغل...")
        except:
            print("لم نتمكن من الضغط، نواصل البحث...")

        time.sleep(15) # وقت إضافي لتحميل ملف الـ .mpd
        
        # تصوير الشاشة للتأكد من الحالة (اختياري للـ Debugging)
        driver.save_screenshot("debug_screen.png")
        
        logs = driver.get_log("performance")
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if "Network.requestWillBeSent" in log["method"]:
                request_url = log["params"]["request"]["url"]
                # نبحث عن أي رابط يحتوي على .mpd أو .m3u8 من سيرفرات Akamai
                if "akamaized.net" in request_url and (".mpd" in request_url or ".m3u8" in request_url):
                    return request_url
        return None
    finally:
        driver.quit()

found_url = get_link_with_interaction()

# حفظ النتيجة
with open("dubai_one.m3u", "w") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_url:
        f.write(found_url)
        print(f"نجاح باهر! الرابط هو: {found_url}")
    else:
        f.write("# لا يزال الرابط مخفياً، قد يكون الموقع محظوراً في GitHub")
        print("فشل الاستخراج مجدداً.")
