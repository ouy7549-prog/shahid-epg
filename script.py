import requests
import re

def get_live_link():
    # رابط صفحة البث التي زودتني بها
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.dubaiplus.net/'
    }

    try:
        response = requests.get(url, headers=headers)
        # البحث عن الرابط داخل كود الصفحة
        # المواقع أحياناً تغير النمط، لذا سنبحث عن أي رابط يحتوي على .mpd و Akamai
        match = re.search(r'https://dmi-live-a\.akamaized\.net/[^"\']+\.mpd\?hdntl=[^"\']+', response.text)
        
        if match:
            link = match.group(0)
            print(f"تم العثور على الرابط: {link}")
            return link
        else:
            print("فشل السكريبت في العثور على الرابط داخل الصفحة.")
            return None
    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال: {e}")
        return None

# تنفيذ الجلب
final_link = get_live_link()

if final_link:
    # إنشاء الملف فقط في حال تم العثور على الرابط
    with open("dubai_one.m3u", "w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXTINF:-1, Dubai One\n")
        f.write(final_link)
    print("تم إنشاء ملف dubai_one.m3u بنجاح.")
else:
    # إنشاء ملف فارغ مؤقتاً لتجنب خطأ الـ Git في GitHub Actions
    with open("dubai_one.m3u", "w") as f:
        f.write("# الرابط غير متوفر حالياً، سيتم التحديث في المحاولة القادمة")
    print("تم إنشاء ملف تنبيه بدلاً من رابط البث.")
