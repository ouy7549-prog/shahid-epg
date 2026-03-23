import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_link_final_attempt():
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # تفعيل تسجيلات الشبكة المتقدمة
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري فحص حركة الشبكة بحثاً عن رابط DASH (.mpd)...")
        
        # الانتظار لفترة كافية لتحميل المشغل وطلب الرابط
        time.sleep(30) 
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    u = msg["params"]["request"]["url"]
                    
                    # البحث عن الرابط الذي وجدته أنت يدوياً
                    if "akamaized.net" in u and ".mpd" in u and "hdntl=" in u:
                        return u
            except:
                continue
        return None
    finally:
        driver.quit()

found_url = get_link_final_attempt()

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
