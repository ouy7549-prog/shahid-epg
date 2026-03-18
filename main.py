import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import json

def update_epg_from_starzplay():
    # الرابط الخاص بك
    url = "https://epg.aws.playco.com/api/v1.1/epg/category/events/d9521174b8d441a784909666d4d1ad7f-sp?ts_start=1773788400&ts_end=1773853200&lang=ar&pg=18&category=all&page=11&limit=10&pageNumberForCache=11"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    print("📡 جاري تحليل بيانات الرابط...")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()

        # بناء جذر ملف XMLTV
        root = ET.Element("tv", {"generator-info-name": "Gemini-StarzPlay-Fixer"})
        
        # معرف القناة (سنستخدم أول GUID متاح أو اسم ثابت)
        channel_id = "PET_CLUB_TV"
        
        # إنشاء عنصر القناة
        chan_elem = ET.SubElement(root, "channel", id=channel_id)
        ET.SubElement(chan_elem, "display-name").text = "Pet Club TV"

        found_events = 0

        # الدخول إلى data ثم events
        if "data" in json_data and isinstance(json_data["data"], list):
            for entry in json_data["data"]:
                # البرامج موجودة داخل مفتاح 'events' في كل عنصر من 'data'
                events = entry.get("events", [])
                for event in events:
                    title = event.get("title", "N/A")
                    desc = event.get("description", "")
                    start_ts = event.get("tsStart")
                    end_ts = event.get("tsEnd")
                    
                    if start_ts and end_ts:
                        # تحويل الوقت لتنسيق XMLTV
                        start_xml = datetime.fromtimestamp(int(start_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                        stop_xml = datetime.fromtimestamp(int(end_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                        
                        # إنشاء عنصر البرنامج
                        prog = ET.SubElement(root, "programme", start=start_xml, stop=stop_xml, channel=channel_id)
                        ET.SubElement(prog, "title", lang="en").text = title
                        ET.SubElement(prog, "desc", lang="en").text = desc
                        
                        # استخراج الصورة (أول صورة متوفرة)
                        images = event.get("images", [])
                        if images:
                            ET.SubElement(prog, "icon", src=images[0].get("url", ""))
                        
                        found_events += 1

        if found_events > 0:
            # حفظ الملف
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            tree.write("epg_auto_updated.xml", encoding="utf-8", xml_declaration=True)
            print(f"✅ نجاح! تم العثور على {found_events} برنامج وحفظهم في epg_auto_updated.xml")
        else:
            print("⚠️ لم يتم العثور على برامج داخل حقل 'events'. تأكد من أن الرابط يحتوي على بيانات.")

    except Exception as e:
        print(f"❌ خطأ أثناء التشغيل: {e}")

if __name__ == "__main__":
    update_epg_from_starzplay()
