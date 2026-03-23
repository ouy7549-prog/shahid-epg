import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_link_from_elahmad_final():
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري فحص الصفحة والإطارات الداخلية (30 ثانية)...")
        time.sleep(15) # انتظار التحميل الأولي
        
        # محاولة الضغط على أي زر تشغيل قد يظهر
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                btn.click()
        except:
            pass

        time.sleep(15) # انتظار توليد الرابط بعد الضغط
        
        logs = driver.get_log("performance")
        found_url = None
        
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    u = msg["params"]["request"]["url"]
                    # البحث عن روابط m3u8 أو mpd مع استثناء روابط الإعلانات
                    if (".m3u8" in u or ".mpd" in u) and ("google" not in u and "doubleclick" not in u):
                        found_url = u
                        break 
            except:
                continue
        return found_url
    finally:
        driver.quit()

found_url = get_link_from_elahmad_final()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_url:
        f.write(found_url)
        print(f"✅ تم العثور على الرابط: {found_url}")
    else:
        f.write("# لا يزال الرابط مخفياً في موقع الأحمد")
        print("❌ لم يتم العثور على الرابط.")
