import cloudscraper
import base64
from Crypto.Cipher import AES
import json

def decrypt_link(ciphertext, key_str, iv_str):
    try:
        # CryptoJS غالباً ما يستخدم التشفير بمفاتيح نصية
        # يجب أن يكون طول المفتاح والـ IV متوافقاً مع AES (16 bytes)
        key = key_str.encode('utf-8')
        iv = iv_str.encode('utf-8')
        
        # التأكد من أن النص المشفر هو Base64 صحيح
        raw_data = base64.b64decode(ciphertext)
        
        # استخدام نمط CBC مع إيقاف الـ Padding يدوياً إذا لزم الأمر
        # سنقوم بتجربة فك التشفير بدون فرض unpad في البداية لتجنب الانهيار
        cipher = AES.new(key, iv, AES.MODE_CBC)
        decrypted = cipher.decrypt(raw_data)
        
        # تحويل النتيجة لنص وتنظيفها من حروف الـ Padding (مثل \x08 أو \x05)
        # هذه الطريقة يدوية لكنها تمنع خطأ "Mode not supported" أو "Padding error"
        decoded_text = decrypted.decode('utf-8', errors='ignore')
        
        # البحث عن رابط يبدأ بـ http داخل النص الناتج
        start_index = decoded_text.find("http")
        if start_index != -1:
            # تنظيف النص من أي رموز غير مرغوبة في نهاية الرابط
            # الروابط عادة لا تحتوي على مسافات أو رموز تحكم
            result = ""
            for char in decoded_text[start_index:]:
                if ord(char) < 32: # التوقف عند أول حرف تحكم (غير مرئي)
                    break
                result += char
            return result
        
        return f"Raw decrypted (No link found): {decoded_text[:50]}"
            
    except Exception as e:
        return f"Decryption Error: {str(e)}"

def fetch_dubai_one():
    scraper = cloudscraper.create_scraper()
    url = "https://www.elahmad.org/tv/live/shahid_shaka.php"
    payload = {"id": "dubaione"}
    headers = {
        "Referer": "https://www.elahmad.org/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = scraper.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            ciphertext = data.get("link_4")
            key = data.get("key")
            iv = data.get("iv")
            
            if ciphertext and key and iv:
                final_link = decrypt_link(ciphertext, key, iv)
                
                with open("live_link.txt", "w") as f:
                    f.write(final_link)
            else:
                with open("live_link.txt", "w") as f:
                    f.write("Error: Missing data from server response")
        else:
            with open("live_link.txt", "w") as f:
                f.write(f"Server Error: {response.status_code}")
    except Exception as e:
        with open("live_link.txt", "w") as f:
            f.write(f"Python Error: {str(e)}")

if __name__ == "__main__":
    fetch_dubai_one()
