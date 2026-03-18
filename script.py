import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_link_from_network():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # تفعيل مراقبة سجلات الشبكة
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("انتظار تحميل البث واستخراج الرابط من الشبكة...")
        time.sleep(15) # زيادة وقت الانتظار لضمان تشغيل المشغل
        
        logs = driver.get_log("performance")
        
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if "Network.requestWillBeSent" in log["method"]:
                request_url = log["params"]["request"]["url"]
                # البحث عن رابط Akamai الذي ينتهي بـ .mpd وفيه التوكن
                if "akamaized.net" in request_url and ".mpd" in request_url and "hdntl=" in request_url:
                    return request_url
        return None
    except Exception as e:
        print(f"خطأ: {e}")
        return None
    finally:
        driver.quit()

# التشغيل والحفظ
found_url = get_link_from_network()

with open("dubai_one.m3u", "w") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Dubai One\n")
    if found_url:
        f.write(found_url)
        print(f"تم بنجاح! الرابط المستخرج: {found_url}")
    else:
        f.write("# فشل استخراج الرابط من سجلات الشبكة")
        print("للأسف لم يتم العثور على الرابط في حركة الشبكة.")
