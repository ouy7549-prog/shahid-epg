import time
import json
import undetected_chromedriver as uc

def run_undetected():
    print("🕵️‍♂️ جاري تشغيل المتصفح المتخفي (Undetected Chromedriver)...")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless") # تشغيل مخفي في السيرفر
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # التنصت على الشبكة لصيد الـ m3u8 أو الـ mpd
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    # تشغيل المتصفح المتخفي
    driver = uc.Chrome(options=options)
    found_url = None

    try:
        url = "https://www.elahmad.com/tv/dubaione.htm"
        print(f"🌍 فتح الرابط المباشر: {url}")
        driver.get(url)
        
        print("⏳ ننتظر 25 ثانية ليتجاوز الـ Cloudflare تلقائياً ويحمل المشغل...")
        time.sleep(25) 

        # 📸 أخذ لقطة الشاشة للتأكد أين وصلنا
        driver.save_screenshot("uc_screenshot.png")
        print("✅ تم التقاط الصورة بنجاح باسم uc_screenshot.png!")

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

    # 📝 حفظ النتيجة في ملف الـ m3u8
    with open("dubai_one.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
        if found_url:
            f.write(found_url)
            print(f"🎯 مبروك! نجحنا في صيد الرابط: {found_url}")
        else:
            f.write("# لم نتمكن من صيد الرابط هذه المرة.\n")
            print("❌ لم نجد رابط البث المباشر في هذه الجلسة.")

# تشغيل الفحص
run_undetected()
