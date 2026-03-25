import os

# 🔒 جلب التوكن بأمان من أسرار جيت هاب (GitHub Secrets)
# هذا يحمي حسابك من السرقة لأن الكود عام (Public)
access_token = os.environ.get("DUBAI_ACCESS_TOKEN")

# 🔗 الرابط الأم الذي استخرجته أنت بيدك من الشبكة (ثابت)
base_url = "https://dmi-live-a.akamaized.net/Content/Channel/onetv/DASH/master.mpd"

# 🛠️ دمج الرابط مع التوكن المسحوب
if access_token:
    # نقوم ببناء الرابط النهائي بـ Token الجديد المحدث
    final_link = f"{base_url}?hdntl={access_token}"
else:
    final_link = None

# 📝 تحديث ملف الـ m3u الثابت في المستودع
with open("dubai_one.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Dubai One\n")
    if final_link:
        f.write(final_link)
        print(f"🎯 نجاح! تم تحديث الرابط في الملف الثابت: {final_link}")
    else:
        f.write("# فشل التحديث التلقائي، التوكن غير موجود في الـ Secrets\n")
        print("❌ فشل! لم نجد التوكن في أسرار المستودع.")
