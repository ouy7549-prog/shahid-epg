import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_live_link_with_selenium():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    # إعدادات المتصفح الخفي (بدون واجهة رسومية)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري الانتظار لتحميل الصفحة وتوليد الرابط...")
        time.sleep(10) # ننتظر 10 ثواني لضمان تشغيل الجافا سكريبت
        
        # الحصول على كامل كود الصفحة بعد التعديل بواسطة جافا سكريبت
        page_source = driver.page_source
        
        # البحث عن الرابط
        match = re.search(r'https://dmi-live-a\.akamaized\.net/[^"\']+\.mpd\?hdntl=[^"\']+', page_source)
        
        if match:
            return match.group(0)
        return None
    except Exception as e:
        print(f"حدث خطأ: {e}")
        return None
    finally:
        driver.quit()

# تنفيذ الجلب
final_link = get_live_link_with_selenium()

with open("dubai_one.m3u", "w") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Dubai One\n")
    if final_link:
        f.write(final_link)
        print(f"نجاح! تم العثور على الرابط: {final_link}")
    else:
        f.write("# الرابط غير متوفر حالياً، سيتم التحديث لاحقاً")
        print("فشل العثور على الرابط حتى باستخدام المتصفح.")
