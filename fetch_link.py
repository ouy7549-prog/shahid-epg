import cloudscraper
import base64
from Crypto.Cipher import AES
import re

def decrypt_payload(ciphertext, key_str, iv_str):
    try:
        # تحويل البيانات إلى Bytes مع التأكد من الترميز
        key = key_str.encode('utf-8')
        iv = iv_str.encode('utf-8')
        
        # فك ترميز Base64 للنص المشفر
        encrypted_data = base64.b64decode(ciphertext)
        
        # الحل الجذري: تعريف الـ Mode بشكل رقمي مباشر (رقم 2 يرمز لـ CBC) 
        # لضمان عدم حدوث تعارض في الاستيراد داخل GitHub Actions
        cipher = AES.new(key, 2, iv) 
        
        decrypted_raw = cipher.decrypt(encrypted_data)
        
        # تحويل النتيجة لنص مع تجاهل الحروف غير القابلة للقراءة (Padding)
        decrypted_text = decrypted_raw.decode('utf-8', errors='ignore')
        
        # البحث عن الرابط باستخدام Regex (تعبير نمطي) لضمان الدقة
        found_links = re.findall(r'https?://[^\s<>"]+|(?<=link":")[^"]+', decrypted_text)
        
        if found_links:
            # تنظيف الرابط الناتج من أي بقايا تشفير
            final_link = found_links[0].split('\\')[0].replace('"', '').strip()
            return final_link
        
        return f"Decrypted, but no link found in: {decrypted_text[:50]}"

    except Exception as e:
        return f"Root Error: {str(e)}"

def run():
    scraper = cloudscraper.create_scraper()
    # بيانات الطلب لقناة دبي ون
    api_url = "https://www.elahmad.org/tv/live/shahid_shaka.php"
    payload = {"id": "dubaione"}
    headers = {"Referer": "https://www.elahmad.org/"}

    try:
        resp = scraper.post(api_url, data=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            
            # جلب الثلاثي المعتمد للتشفير
            c_text = data.get("link_4")
            key = data.get("key")
            iv = data.get("iv")
            
            if all([c_text, key, iv]):
                result = decrypt_payload(c_text, key, iv)
                with open("live_link.txt", "w") as f:
                    f.write(result)
                print("Done: Link extracted.")
            else:
                print("Error: Missing JSON fields.")
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    run()
