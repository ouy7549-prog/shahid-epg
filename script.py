import requests
import re

def get_direct_link():
    # الرابط الذي وجدته أنت لا يتطلب تسجيل دخول
    url = "https://www.elahmad.com/tv/dubaione.htm"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.elahmad.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # البحث باستخدام التعبيرات النمطية (Regex) عن رابط الـ mpd أو m3u8
        match = re.search(r'(https?://[^\s"]+\.(?:mpd|m3u8)[^\s"]*)', response.text)
        
        if match:
            return match.group(0)
            
        # محاولة أخرى للبحث عن akamaized تحديداً
        match_akamai = re.search(r'(https?://[^\s"]*akamaized\.net[^\s"]*)', response.text)
        if match_akamai:
            return match_akamai.group(0)
            
        return None
    except Exception as e:
        print(f"حدث خطأ أثناء الطلب: {e}")
        return None

found_link = get_direct_link()

# حفظ الملف
with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print(f"✅ تم القنص بنجاح: {found_link[:50]}...")
    else:
        f.write("# فشل الاستخراج التلقائي عبر الطلب المباشر.\n")
        print("❌ فشل السحب التلقائي.")
