import cloudscraper
import base64
from Crypto.Cipher import AES
import re

def decrypt_payload(ciphertext, key_str, iv_str):
    try:
        # الحل الجذري لطول المفتاح: 
        # تحويل المفتاح والـ IV من نص Hex إلى Bytes
        # الـ Hex المكون من 64 حرف سيتحول إلى 32 بايت (وهو الطول المثالي لـ AES-256)
        key = bytes.fromhex(key_str)
        iv = bytes.fromhex(iv_str)
        
        encrypted_data = base64.b64decode(ciphertext)
        
        # استخدام النمط CBC (رقم 2)
        cipher = AES.new(key, 2, iv) 
        
        decrypted_raw = cipher.decrypt(encrypted_data)
        decrypted_text = decrypted_raw.decode('utf-8', errors='ignore')
        
        # البحث عن الرابط
        found_links = re.findall(r'https?://[^\s<>"]+', decrypted_text)
        
        if found_links:
            # تنظيف الرابط من أي علامات هروب (Backslashes)
            return found_links[0].replace('\\', '')
        
        return f"Decrypted, but no link found in: {decrypted_text[:50]}"

    except Exception as e:
        # إذا فشل تحويل Hex، نجرب الطول العادي (للاحتياط)
        try:
            key = key_str.encode('utf-8')[:32]
            iv = iv_str.encode('utf-8')[:16]
            cipher = AES.new(key, 2, iv)
            decrypted_raw = cipher.decrypt(base64.b64decode(ciphertext))
            return re.findall(r'https?://[^\s<>"]+', decrypted_raw.decode('utf-8', errors='ignore'))[0]
        except:
            return f"Final Attempt Error: {str(e)}"

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
