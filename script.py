import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def fetch_live_akamai():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    # استخدام undetected_chromedriver لتخطي حظر السيرفرات السحابية وCloudflare
    options = uc.ChromeOptions()
    options.add_argument("--headless") # تشغيل مخفي في الخلفية
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # التنصت على الشبكة لسحب التوكن المباشر
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = uc.Chrome(options=options)
    found_url = None

    try:
        driver.get(url)
        time.sleep(20) # ننتظر تحميل الصفحة ومشغل الفيديو لإنتاج الـ Token الأصلي من المتصفح

        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    if "master.mpd" in request_url and "hdntl=" in request_url:
                        found_url = request_url
                        break
            except:
                continue
    finally:
        driver.quit()

    return found_url

# التشغيل الفعلي وتحديث ملف الـ m3u
new_link = fetch_live_akamai()

    try:
        # سنفتح الرابط للتأكد من تحميل السيرفر له
        driver.get(final_link)
        time.sleep(15) # ننتظر قليلاً ليحمل الملف
        
        # حفظ الصورة للتأكد
        driver.save_screenshot("debug_screenshot.png")
        print("✅ تم التقاط الصورة بنجاح باسم debug_screenshot.png!")
    except Exception as e:
        print(f"⚠️ فشل التقاط الصورة: {e}")
    finally:
        driver.quit()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if new_link:
        f.write(new_link)
        print(f"🎯 نجاح! تم تجديد الرابط ووضعه في الملف الثابت: {new_link}")
    else:
        f.write("# فشل التحديث التلقائي هذه المرة بسبب الحظر.\n")
        print("❌ فشل العثور على رابط جديد.")
