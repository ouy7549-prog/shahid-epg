import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🔒 ضع حسابك الحقيقي هنا (تأكد من صحته)
USER_EMAIL = "your_email@example.com"
USER_PASSWORD = "your_password"

def extract_with_login_forced():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(1920, 1080)
    
    found_url = None

    try:
        print("🚀 فتح الموقع...")
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        
        # 1️⃣ تجاوز الكوكيز
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            time.sleep(2)
        except:
            pass

        # 2️⃣ الضغط على زر Log in قسراً عبر JavaScript
        print("🔘 الضغط على زر Log in قسرياً...")
        driver.execute_script("""
            // البحث عن أي زر يحتوي على كلمة Log in في الصفحة والضغط عليه
            const buttons = Array.from(document.querySelectorAll('button, a'));
            const loginBtn = buttons.find(b => b.textContent.trim() === 'Log in' || b.innerText.includes('Log in'));
            if (loginBtn) {
                loginBtn.click();
            } else {
                // محاولة الضغط على الزر الشفاف الذي يظهر في الصورة
                document.querySelectorAll('button').forEach(b => {
                    if(b.textContent.includes('Log in')) b.click();
                });
            }
        """)
        time.sleep(7) # ننتظر ظهور حقول الإيميل

        # 📸 التقاط صورة لنرى هل ظهرت حقول الإيميل والباسورد؟
        driver.save_screenshot("debug_screenshot.png")

        # 3️⃣ تعبئة الحقول والضغط على الدخول
        print("✍️ كتابة الإيميل والباسورد...")
        driver.execute_script(f"""
            const emailInput = document.querySelector("input[type='email'], input[name='email']");
            const passInput = document.querySelector("input[type='password'], input[name='password']");
            const submitBtn = document.querySelector("button[type='submit'], .submit-btn");

            if (emailInput && passInput) {{
                emailInput.value = '{USER_EMAIL}';
                passInput.value = '{USER_PASSWORD}';
                
                // تفعيل أحداث الكتابة ليتعرف عليها الموقع
                emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                passInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                if (submitBtn) {{
                    submitBtn.click();
                }}
            }}
        """)
        time.sleep(15) # انتظار تسجيل الدخول الفعلي

        # 4️⃣ سحب الرابط بعد الدخول
        print("📡 التنصت على الشبكة لسحب الرابط...")
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if "params" in msg and "request" in msg["params"]:
                    request_url = msg["params"]["request"]["url"]
                    if "akamaized.net" in request_url and (".mpd" in request_url or ".m3u8" in request_url):
                        found_url = request_url
                        break
            except:
                continue

    finally:
        driver.quit()
        
    return found_url

# التشغيل النهائي
found_link = extract_with_login_forced()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 نجاح! تم الحصول على الرابط: {found_link}")
    else:
        f.write("# لم يتم العثور على الرابط. تحقق من الصورة لترى أين توقف المتصفح.")
        print("❌ لم يتم العثور على الرابط.")
