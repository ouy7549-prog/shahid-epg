import requests
import os

def fetch_dubai_one():
    url = "https://www.elahmad.org/tv/live/shahid_shaka.php?id=dubaione"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.elahmad.org/",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {"id": "dubaione"}

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        # إذا كان الرد ناجحاً
        if response.status_code == 200:
            data = response.json()
            # استخراج الرابط (تعديل حسب المفتاح الصحيح في الـ JSON)
            link = data.get("link_4", "No Link Found")
            
            with open("live_link.txt", "w") as f:
                f.write(link)
            print("Successfully created live_link.txt")
        else:
            print(f"Server returned status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred: {e}")
        # إنشاء ملف فارغ على الأقل لتجنب خطأ الـ Git
        with open("live_link.txt", "w") as f:
            f.write("error_fetching_link")

if __name__ == "__main__":
    fetch_dubai_one()
