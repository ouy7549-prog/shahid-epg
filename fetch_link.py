import cloudscraper
import base64
import re
from Crypto.Cipher import AES

def decrypt_payload(ciphertext, key_hex, iv_hex):
    try:
        # تحويل الـ Hex المرسل من الموقع إلى Bytes صالحة لـ AES
        key = bytes.fromhex(key_hex)
        iv = bytes.fromhex(iv_hex)
        
        # فك تشفير Base64
        encrypted_data = base64.b64decode(ciphertext)
        
        # استخدام نمط CBC (الرقم 2)
        cipher = AES.new(key, 2, iv)
        decrypted_raw = cipher.decrypt(encrypted_data)
        
        # تحويل النتيجة لنص مع تجاهل الأخطاء وتنظيف رموز الـ Padding (الحل الجذري للرموز الغريبة)
        decrypted_text = decrypted_raw.decode('utf-8', errors='ignore')
        
        # البحث عن الرابط باستخدام Regex
        found = re.findall(r'https?://[^\s<>"]+', decrypted_text)
        
        if found:
            # تنظيف الرابط من أي رموز غير مرئية (مثل 0x05) أو علامات هروب
            link = found[0].replace('\\', '')
            clean_link = "".join(char for char in link if 31 < ord(char) < 127)
            return clean_link
        
        return "Error: Link not found in decrypted text"
    except Exception as e:
        return f"Decryption Fail: {str(e)}"

def run():
    scraper = cloudscraper.create_scraper()
    api_url = "https://www.elahmad.org/tv/live/shahid_shaka.php"
    payload = {"id": "dubaione"}
    
    # تحسين الـ Headers لمحاكاة المتصفح الذي أنتج الرابط اليدوي الناجح
    headers = {
        "Origin": "https://www.elahmad.org",
        "Referer": "https://www.elahmad.org/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        resp = scraper.post(api_url, data=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            
            # استخراج البيانات
            c_text = data.get("link_4")
            k_hex = data.get("key")
            i_hex = data.get("iv")
            
            if all([c_text, k_hex, i_hex]):
                final_result = decrypt_payload(c_text, k_hex, i_hex)
                with open("live_link.txt", "w") as f:
                    f.write(final_result)
            else:
                with open("live_link.txt", "w") as f:
                    f.write("Error: Missing JSON fields from server")
    except Exception as e:
        with open("live_link.txt", "w") as f:
            f.write(f"Scraper Error: {str(e)}")

if __name__ == "__main__":
    run()
