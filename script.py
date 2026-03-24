import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_exact_link_with_proxy():
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 🌐 هنا نخدع السيرفر ببروكسي عربي (يمكنك تجربة بروكسيات مجانية عربية متجددة)
    # مثال لـ Proxy سعودي أو إماراتي (IP:Port)
    # chrome_options.add_argument('--proxy-server=http://IP_العربي:المنفذ') 

    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(30) # وقت كافٍ لتجاوز الحظر والتحميل
        
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    if "akamaized.net" in request_url and ".mpd" in request_url:
                        return request_url
            except:
                continue
        return None
    finally:
        driver.quit()

found_link = get_exact_link_with_proxy()

file_name = "dubai_one.m3u"
with open(file_name, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"✅ نجاح! تم صيد الرابط عبر البروكسي.")
    else:
        f.write("# فشل السحب التلقائي بسبب الحظر الجغرافي.")
        print("❌ فشل السحب التلقائي.")
