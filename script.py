import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 🍪 ضع الكوكيز الكاملة التي قمت بنسخها هنا بين القوسين المربعين [ ]
MY_COOKIES = [
    # ألصق الـ JSON الكامل الذي نسخته هنا...
]

def run_with_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # تشغيل مخفي في السيرفر
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # التنصت على الشبكة لسحب رابط الـ MPD الأصلي والتوكن
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    found_url = None

    try:
        # 1. فتح الموقع لتهيئة النطاق (Domain)
        print("🌍 فتح النطاق الرئيسي...")
        driver.get("https://www.dubaiplus.net")
        time.sleep(3)

        # 2. حقن الكوكيز
        print("💉 جاري حقن كوكيز تسجيل الدخول الحقيقية...")
        for cookie in MY_COOKIES:
            # نقوم بمسح الـ id الزائد لأنه يعطي خطأ أحياناً في السيلينيوم
            if "id" in cookie: 
                del cookie["id"]
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ فشل حقن كوكي: {cookie.get('name')} | السبب: {e}")

        # 3. تحديث الصفحة بعد الحقن للدخول كعضو مسجل
        print("✅ تم الحقن! الانتقال لصفحة البث المباشر الآن...")
        driver.get("https://www.dubaiplus.net/epg?channel=702096936070")
        time.sleep(20) # ننتظر قليلاً ليقوم المشغل بطلب الفيديو والتوكن

        # 4. صيد الرابط والتوكن من الشبكة تلقائياً!
        print("🕵️‍♂️ جاري البحث عن رابط الـ .mpd والتوكن في الشبكة...")
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
        import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 🍪 ضع الكوكيز الكاملة التي قمت بنسخها هنا بين القوسين المربعين [ ]
MY_COOKIES = [
    # ألصق الـ JSON الكامل الذي نسخته هنا...
]

def run_with_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # تشغيل مخفي في السيرفر
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # التنصت على الشبكة لسحب رابط الـ MPD الأصلي والتوكن
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    found_url = None

    try:
        # 1. فتح الموقع لتهيئة النطاق (Domain)
        print("🌍 فتح النطاق الرئيسي...")
        driver.get("https://www.dubaiplus.net")
        time.sleep(3)

        # 2. حقن الكوكيز
        print("💉 جاري حقن كوكيز تسجيل الدخول الحقيقية...")
        for cookie in MY_COOKIES:
            # نقوم بمسح الـ id الزائد لأنه يعطي خطأ أحياناً في السيلينيوم
            if "id" in cookie: 
                del cookie["id"]
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ فشل حقن كوكي: {cookie.get('name')} | السبب: {e}")

        # 3. تحديث الصفحة بعد الحقن للدخول كعضو مسجل
        print("✅ تم الحقن! الانتقال لصفحة البث المباشر الآن...")
        driver.get("https://www.dubaiplus.net/epg?channel=702096936070")
        time.sleep(20) # ننتظر قليلاً ليقوم المشغل بطلب الفيديو والتوكن

        # 4. صيد الرابط والتوكن من الشبكة تلقائياً!
        print("🕵️‍♂️ جاري البحث عن رابط الـ .mpd والتوكن في الشبكة...")
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

    # 5. كتابة الملف الثابت m3u للأبد
    with open("dubai_one.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
        if found_url:
            f.write(found_url)
            print(f"🎯 مبروك! تم تحديث الملف بالرابط الذهبي والتوكن الجديد تلقائياً: {found_url}")
        else:
            f.write("# فشل سحب الرابط التلقائي هذه المرة.\n")
            print("❌ لم نجد رابط mpd يحتوي على توكن في هذه الجلسة.")

# تشغيل الأتمتة
run_with_cookies()

    # 5. كتابة الملف الثابت m3u للأبد
    with open("dubai_one.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
        if found_url:
            f.write(found_url)
            print(f"🎯 مبروك! تم تحديث الملف بالرابط الذهبي والتوكن الجديد تلقائياً: {found_url}")
        else:
            f.write("# فشل سحب الرابط التلقائي هذه المرة.\n")
            print("❌ لم نجد رابط mpd يحتوي على توكن في هذه الجلسة.")

# تشغيل الأتمتة
run_with_cookies()
