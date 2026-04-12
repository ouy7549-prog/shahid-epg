import cloudscraper
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_link(ciphertext, key_str, iv_str):
    try:
        # تحويل المفتاح والـ IV إلى Bytes
        key = key_str.encode('utf-8')
        iv = iv_str.encode('utf-8')
        raw_data = base64.b64decode(ciphertext)
        
        # إعداد فك التشفير (AES-CBC)
        cipher = AES.new(key, iv, AES.MODE_CBC)
        decrypted = unpad(cipher.decrypt(raw_data), AES.block_size)
        return decrypted.decode('utf-8')
    except Exception as e:
        return f"Decryption Error: {e}"

def fetch_dubai_one():
    scraper = cloudscraper.create_scraper()
    url = "https://www.elahmad.org/tv/live/shahid_shaka.php"
    payload = {"id": "dubaione"}
    headers = {"Referer": "https://www.elahmad.org/"}

    try:
        response = scraper.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # جلب البيانات المطلوبة لفك التشفير من الـ JSON
            ciphertext = data.get("link_4")
            key = data.get("key")
            iv = data.get("iv")
            
            if ciphertext and key and iv:
                # فك التشفير للحصول على رابط m3u8 الحقيقي
                final_link = decrypt_link(ciphertext, key, iv)
                
                with open("live_link.txt", "w") as f:
                    f.write(final_link)
                print("Success: Decrypted link saved.")
            else:
                print("Missing encryption data.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_dubai_one()
