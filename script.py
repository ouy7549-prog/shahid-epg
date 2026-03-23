import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_exact_link_github():
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    # ⚠️ ضروري جداً لعمل المتصفح على سيرفرات GitHub بدون واجهة رسومية
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # تفعيل تسجيلات الشبكة
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري تحميل الصفحة في الخلفية...")
        
        # النزول لأسفل قليلاً لتفعيل تحميل المشغل
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(15)
        
        print("جاري الانتظار وفحص سجلات الشبكة (30 ثانية)...")
        time.sleep(30) 
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    
                    # الفلترة الذكية للرابط المطلوب
                    if (".mpd" in request_url or "akamaized.net" in request_url) and "hdntl=" in request_url:
                        return request_url
            except:
                continue
        return None
    finally:
        driver.quit()

# 1. جلب الرابط
found_link = get_exact_link_github()

# 2. حفظ الملف (باسم الملف الذي يستخدمه GitHub لديك)
file_name = "dubai_one.m3u"

with open(file_name, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"\n✅ نجاح باهر! تم صيد الرابط: {found_link[:60]}...")
    else:
        f.write("# لم يتم العثور على الرابط من سيرفرات GitHub")
        print("\n❌ للأسف لم يظهر الرابط في سجلات الشبكة الخاصة بـ GitHub.")
