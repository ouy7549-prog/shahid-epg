import requests

def get_link_from_worker():
    # ⚠️ ضع هنا رابط الـ Worker الذي نسخته من Cloudflare
    worker_url = "https://winter-rain-e223.ouy7549.workers.dev/" 
    
    try:
        response = requests.get(worker_url, timeout=15)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f"Error fetching from worker: {e}")
    return None

found_link = get_link_from_worker()

with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXTINF:-1, Dubai One\n")
    if found_link:
        f.write(found_link)
        print("✅ تم صيد الرابط بنجاح عبر الخادم الوسيط!")
    else:
        f.write("# فشل السحب التلقائي عبر الـ Cloudflare Worker.")
        print("❌ لم يتم العثور على الرابط.")
