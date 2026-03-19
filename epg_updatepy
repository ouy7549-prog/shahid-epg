import requests
import re

# روابط المصادر الموثوقة من مشروع iptv-org
sources = [
    "https://iptv-org.github.io/epg/guides/sa.xml",
    "https://iptv-org.github.io/epg/guides/eg.xml",
    "https://iptv-org.github.io/epg/guides/ae.xml"
]

def generate_epg():
    all_channels = []
    all_programmes = []
    
    for url in sources:
        try:
            print(f"جاري جلب البيانات من: {url}")
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                content = response.text
                # استخراج القنوات والبرامج باستخدام Regex بسيط للحفاظ على السرعة
                channels = re.findall(r'<channel.*?>.*?</channel>', content, re.DOTALL)
                programmes = re.findall(r'<programme.*?>.*?</programme>', content, re.DOTALL)
                
                all_channels.extend(channels)
                all_programmes.extend(programmes)
        except Exception as e:
            print(f"خطأ في جلب {url}: {e}")

    # بناء ملف XML النهائي
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<tv generator-info-name="MyAutoEPG">\n')
        f.write("\n".join(all_channels))
        f.write("\n".join(all_programmes))
        f.write('\n</tv>')
    print("تم تحديث ملف epg.xml بنجاح!")

if __name__ == "__main__":
    generate_epg()
