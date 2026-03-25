import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 🍪 نضع هنا الكوكيز الحقيقية التي استخرجتها أنت بنفسك
COOKIES_JSON = [
    {
        "domain": ".www.dubaiplus.net",
        "name": "OptanonAlertBoxClosed",
        "value": "2026-02-10T18:11:54.324Z",
        "path": "/"
    },
    {
        "domain": ".www.dubaiplus.net",
        "name": "OptanonConsent",
        "value": "isGpcEnabled=0&datestamp=Wed+Mar+25+2026+20%3A47%3A03+GMT%2B0300+(%D8%A7%D9%84%D8%AA%D9%88%D9%82%D9%8A%D8%AA+%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A+%D8%A7%D9%84%D8%B1%D8%B3%D9%85%D9%8A)&version=202601.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=23f5248f-f1b8-4b06-bd01-97e202905854&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=&intType=2&geolocation=SA%3B02&AwaitingReconsent=false",
        "path": "/"
    },
    {
        "domain": ".www.dubaiplus.net",
        "name": "access_token", # 👈 إذا كان اسم التوكن في المتصفح مختلفاً (مثل id_token أو session)، قم بتغييره هنا
        "value": "09AKhCRwgpB0dkdhm6yByLD9wDTw3fe-eF9CH7i1ccQZvjVqSzUX8HskV0vWy95iiljDk2w_D9bz-_vOCBcDOCYYE",
        "path": "/"
    }
]

def extract_with_auth_cookies():
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
        print("🚀 فتح النطاق لحقن التوكن...")
        driver.get("https://www.dubaiplus.net")
        time.sleep(5)

        print("🍪 جاري حقن توكن تسجيل الدخول الحقيقي...")
        for cookie in COOKIES_JSON:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"فشل حقن كوكي معينة: {e}")
                continue

        print("🔄 الانتقال لصفحة القناة بالهوية الجديدة...")
        driver.get(url)
        time.sleep(15) # نترك وقتاً للموقع ليعرف أنك مسجل دخول ويبدأ البث

        # 📸 التقاط صورة لنرى هل اختفت النافذة السوداء؟
        driver.save_screenshot("debug_screenshot.png")

        print("📡 التنصت على الشبكة لسحب الرابط الرسمي...")
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

# التشغيل وحفظ النتيجة
found_link = extract_with_auth_cookies()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"🎯 مبروك! نجحت خطة التوكن وحصلنا على الرابط: {found_link}")
    else:
        f.write("# لم نجد الرابط بعد حقن التوكن. راجع الصورة.")
        print("❌ لم يتم العثور على الرابط.")
