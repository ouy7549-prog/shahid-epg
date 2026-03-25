import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def take_screenshot_without_proxy():
    chrome_options = Options()
    # 🚫 وضع الـ Headless (بدون واجهة رسومية) وهو المطلوب في السيرفرات
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 🚫 نتأكد من عدم وجود أي إعدادات بروكسي في المتصفح
    chrome_options.add_argument("--no-proxy-server")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 📐 ضبط حجم الشاشة ليكون واضحاً وعريضاً (Full HD)
    driver.set_window_size(1920, 1080)

    try:
        url = "https://www.elahmad.com/tv/dubaione.htm"
        print(f"🌍 جاري فتح الرابط المباشر: {url}")
        driver.get(url)
        
        print("⏳ ننتظر 15 ثانية ليتم تحميل المشغل بالكامل...")
        time.sleep(15) 

        # 📸 أخذ لقطة الشاشة
        screenshot_name = "elahmad_screenshot.png"
        driver.save_screenshot(screenshot_name)
        print(f"✅ تم التقاط الصورة بنجاح وحفظها باسم: {screenshot_name}")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء التقاط الصورة: {e}")
        
    finally:
        driver.quit()

# تشغيل الدالة
take_screenshot_without_proxy()
