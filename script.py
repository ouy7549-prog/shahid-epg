import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_undetected_with_screenshot():
    print("🕵️‍♂️ جاري تشغيل المتصفح المتخفي (Undetected Chromedriver)...")
    
    options = uc.ChromeOptions()
    # 🚫 وضع الـ Headless (مخفي) هو المطلوب ليعمل في السيرفر
    options.add_argument("--headless=new") 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 🚫 تفعيل قراءة روابط الشبكة في الخلفية لصيد الـ m3u8
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    # تشغيل المتصفح المتخفي
    driver = uc.Chrome(options=options)
    found_url = None

    try:
        url = "https://www.elahmad.com/tv/dubaione.htm"
        print(f"🌍 فتح الرابط المباشر: {url}")
        driver.get(url)
        
        # ⏳ ننتظر 25 ثانية لتجاوز Cloudflare تلقائياً وتحميل المشغل
        print("⏳ ننتظر 25 ثانية ليتجاوز الـ Cloudflare ويحمل المشغل...")
        time.sleep(25) 

        # 📸 أخذ لقطة الشاشة المطلوبة!
        screenshot_name = "debug_screenshot.png"
        driver.save_screenshot(screenshot_name)
        print(f"✅ تم التقاط الصورة بنجاح باسم: {screenshot_name}")

        # 🕵️‍♂️ فحص روابط الشبكة بالخلفية
        print("🔎 جاري فحص الروابط المسحوبة من الشبكة...")
        logs = driver.get_log("performance")
        
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    if (".m3u8" in request_url or ".mpd" in request_url) and "Segment" not in request_url:
                        found_url = request_url
                        break
            except:
                continue

    finally:
        driver.quit()

    # 📝 حفظ النتيجة في ملف الـ m3u8
    with open("dubai_one.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
        if found_url:
            f.write(found_url)
            print(f"🎯 مبروك! نجحنا في صيد الرابط: {found_url}")
        else:
            # رابط احتياطي في حال الفشل
            f.write("https://dmi-live-a.akamaized.net/Content/Channel/onetv/DASH/master.mpd\n")
            print("❌ لم نجد رابط البث المباشر في هذه الجلسة.")

# تشغيل الأتمتة
run_undetected_with_screenshot()
