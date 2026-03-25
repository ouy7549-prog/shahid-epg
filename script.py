import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 🔒 1. جلب التوقيع الزمني من أسرار جيت هاب
akamai_token = os.environ.get("DUBAI_ACCESS_TOKEN")

# 🔗 2. الرابط الأساسي الصافي
base_url = "https://dmi-live-a.akamaized.net/Content/Channel/onetv/DASH/master.mpd"

if akamai_token:
    # نقوم ببناء الرابط النهائي
    final_link = f"{base_url}?hdntl={akamai_token}"
else:
    final_link = None

# 📸 3. تشغيل سيلينيوم لالتقاط الصورة للتأكد (بدون أي مسافات خاطئة)
if final_link:
    print("🚀 جاري فتح الرابط النهائي للتأكد والتقاط الصورة...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(1920, 1080)
    
    try:
        driver.get(final_link)
        time.sleep(15) # ننتظر قليلاً ليحمل الملف
        driver.save_screenshot("debug_screenshot.png")
        print("✅ تم التقاط الصورة بنجاح باسم debug_screenshot.png!")
    except Exception as e:
        print(f"⚠️ فشل التقاط الصورة: {e}")
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

# 📝 4. تحديث ملف الـ m3u
with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Dubai One\n")
    if final_link:
        f.write(final_link)
        print("🎯 تم تحديث ملف الـ m3u بالرابط الصحيح!")
    else:
        f.write("# خطأ: لم يتم العثور على التوكن في الـ Secrets\n")
