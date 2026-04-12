import requests
import json

# ملاحظة: ستحتاج لمكتبة لفك تشفير الرابط إذا كان مشفراً بنفس الطريقة في المتصفح
# هذا مثال على إرسال الطلب (Request) كما يفعله الموقع
def fetch_dubai_one():
    url = "https://www.elahmad.org/tv/live/shahid_shaka.php?id=dubaione" # الرابط المباشر للـ API
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.elahmad.org/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {"id": "dubaione"}

    try:
        response = requests.post(url, data=payload, headers=headers)
        data = response.json()
        
        # هنا يتم استخراج الرابط (قد يتطلب فك تشفير 'link_4' بناءً على المفاتيح المرسلة)
        # هذا مثال لو كان الرابط يظهر مباشرة أو بعد المعالجة
        raw_link = data.get("link_4") 
        print(f"Stream Data Found: {raw_link}")
        
        # حفظ الرابط في ملف نصي
        with open("live_link.txt", "w") as f:
            f.write(raw_link)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_dubai_one()
