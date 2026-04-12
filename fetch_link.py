import cloudscraper
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_link(ciphertext, key_str, iv_str):
    try:
        # تحويل المفتاح والـ IV (الموقع غالباً يرسلهم كنصوص)
        key = key_str.encode('utf-8')
        iv = iv_str.encode('utf-8')
        
        # فك ترميز Base64 للنص المشفر
        enc = base64.b64decode(ciphertext)
        
        # تجربة نمط CBC وهو الأكثر شيوعاً في هذه المواقع
        # قمنا بإضافة التجاوز عن الأخطاء البسيطة في طول البيانات
        cipher = AES.new(key, iv, AES.MODE_CBC)
        decrypted = cipher.decrypt(enc)
        
        # محاولة إزالة الـ Padding (الحشو)
        try:
            return unpad(decrypted, AES.block_size).decode('utf-8')
        except:
            # إذا فشل الـ unpad، قد يكون النص مفكوكاً بالفعل ولكنه يحتوي على فراغات
            return decrypted.decode('utf-8', errors='ignore').strip()
            
    except Exception as e:
        return f"Decryption Error: {str(e)}"

def fetch_dubai_one():
    scraper = cloudscraper.create_scraper()
    url = "https://www.elahmad.org/tv/live/shahid_shaka.php"
    payload = {"id": "dubaione"}
    headers = {
        "Referer": "https://www.elahmad.org/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
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
                
                # تأكد من أن الرابط الناتج يبدأ بـ http
                if "http" in final_link:
                    # تنظيف الرابط من أي حروف غريبة قد تظهر بعد فك التشفير
                    clean_link = final_link[final_link.find("http"):]
                    with open("live_link.txt", "w") as f:
                        f.write(clean_link)
                else:
                    with open("live_link.txt", "w") as f:
                        f.write(f"Decrypted but not a link: {final_link}")
            else:
                print("Missing data in JSON response")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_dubai_one()
