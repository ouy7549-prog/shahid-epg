import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_link_github_vfinal():
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 🚫 خطوة الحماية الذهبية: منع تجميد المتصفح عبر الـ Debugger
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # 🌍 تفعيل البروكسي السعودي Socks5 الذي وجدته!
    proxy_ip = "213.165.58.5:1080"
    chrome_options.add_argument(f"--proxy-server=socks5://{proxy_ip}")

    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print("جاري تحميل الصفحة في الخلفية وتخطي حماية التجميد...")
        
        # تنفيذ جافا سكريبت لتعطيل الـ Debugger تماماً لمنع الموقع من تجميد الصفحة
        driver.execute_script("""
            window.setInterval = (function(oldSetInterval) {
                return function(func, time) {
                    if (func.toString().includes('debugger')) return;
                    return oldSetInterval(func, time);
                };
            })(window.setInterval);
        """)
        
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(25) # زيادة وقت الانتظار لأن البروكسي المجاني أبطأ قليلاً
        
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

# التشغيل والحفظ
found_link = get_link_github_vfinal()
with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"✅ تم صيد الرابط بنجاح من GitHub عبر البروكسي السعودي: {found_link[:50]}...")
    else:
        f.write("# لم يتم العثور على الرابط. قد يحتاج البروكسي للتغيير.")
        print("❌ فشل السحب التلقائي. قد يكون البروكسي المجاني بطيئاً جداً أو توقف.")
