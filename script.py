import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_link_final():
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # تغيير اللغة لتبدو كأنها من منطقة عربية
    chrome_options.add_argument("--lang=ar-AE")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("انتظار تحميل المشغل (30 ثانية)...")
        time.sleep(30) # زيادة الوقت لأقصى حد
        
        # حفظ صورة للشاشة لمعرفة ماذا يرى السكريبت
        driver.save_screenshot("debug.png")
        print("تم حفظ صورة debug.png للمراجعة")
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    u = msg["params"]["request"]["url"]
                    # البحث عن أي رابط بث (m3u8 أو mpd)
                    if (".mpd" in u or ".m3u8" in u) and "akamaized" in u:
                        return u
            except:
                continue
        return None
    finally:
        driver.quit()

found_url = get_link_final()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_url:
        f.write(found_url)
        print(f"نجاح! الرابط المستخرج: {found_url}")
    else:
        f.write("# فشل الاستخراج. راجع صورة debug.png لمعرفة السبب")
        print("لم يتم العثور على رابط البث.")
