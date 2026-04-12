import cloudscraper
import os

def fetch_dubai_one():
    # استخدام cloudscraper لتجاوز الحماية
    scraper = cloudscraper.create_scraper()
    
    url = "https://www.elahmad.org/tv/live/shahid_shaka.php"
    payload = {"id": "dubaione"}
    headers = {
        "Referer": "https://www.elahmad.org/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = scraper.post(url, data=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # استخراج الرابط المشفر (link_4)
            link = data.get("link_4", "link_not_found")
            
            # التأكد من كتابة الملف في المسار الحالي
            file_path = os.path.join(os.getcwd(), "live_link.txt")
            with open(file_path, "w") as f:
                f.write(link)
            print(f"File created successfully at: {file_path}")
        else:
            print(f"Failed! Status code: {response.status_code}")
            # إنشاء ملف حتى في حالة الفشل لتجنب خطأ الـ Action
            with open("live_link.txt", "w") as f:
                f.write("status_code_error")
    except Exception as e:
        print(f"An error occurred: {e}")
        with open("live_link.txt", "w") as f:
            f.write("exception_error")

if __name__ == "__main__":
    fetch_dubai_one()
