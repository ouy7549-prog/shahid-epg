import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_exact_link_local():
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    # سنقوم بإلغاء headless مؤقتاً لترى ماذا يحدث، إذا نجح يمكنك إعادته
    # chrome_options.add_argument("--headless") 
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري تحميل الصفحة... يرجى الانتظار")
        
        # النزول لأسفل قليلاً لتفعيل تحميل المشغل
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(10)
        
        # محاولة البحث عن أي إطار (iframe) والتبديل إليه إذا وجد
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"تم العثور على {len(iframes)} إطارات في الصفحة.")

        print("جاري فحص سجلات الشبكة لمدة 30 ثانية أخرى...")
        time.sleep(30) 
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    
                    # البحث عن الرابط بالكلمات المفتاحية التي وجدتها أنت يدوياً
                    if (".mpd" in request_url or "akamaized.net" in request_url) and "hdntl=" in request_url:
                        return request_url
            except:
                continue
        return None
    finally:
        driver.quit()

# 1. جلب الرابط
found_link = get_exact_link_local()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_url:
        # تحويل الرابط من .mpd إلى .m3u8 إذا لزم الأمر، 
        # لكن معظم المشغلين الحديثين يدعمون .mpd مباشرة
        f.write(found_url)
        print(f"✅ تم اصطياد الرابط بنجاح: {found_url}")
    else:
        f.write("# فشل السكريبت في العثور على الرابط، بينما وجدته أنت يدوياً.")
        print("❌ لم يتم العثور على الرابط. قد يكون هناك حظر لـ IP الخاص بـ GitHub.")
