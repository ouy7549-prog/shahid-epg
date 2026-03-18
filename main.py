import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import json

def update_epg_comprehensive():
    # الرابط الخاص بك
    url = "https://epg.aws.playco.com/api/v1.1/epg/category/events/d9521174b8d441a784909666d4d1ad7f-sp?ts_start=1773788400&ts_end=1773853200&lang=ar&pg=18&category=all&page=11&limit=10&pageNumberForCache=11"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    print("📡 جاري محاولة استخراج البرامج من جميع القنوات في الرابط...")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()

        root = ET.Element("tv", {"generator-info-name": "StarzPlay-Comprehensive-Fix"})
        
        found_events = 0

        # الدخول إلى القائمة الرئيسية 'data'
        if "data" in json_data and isinstance(json_data["data"], list):
            for entry in json_data["data"]:
                # 1. استخراج معرف القناة من الرابط المباشر أو الـ ID
                # سنحاول جلب اسم القناة من الـ streamingUrl إذا وجد
                channel_id = entry.get("id", "UNKNOWN_CH")
                channel_name = entry.get("category", "General")
                
                # إضافة القناة للملف
                chan_elem = ET.SubElement(root, "channel", id=str(channel_id))
                ET.SubElement(chan_elem, "display-name").text = str(channel_name).upper()

                # 2. استخراج البرامج من قائمة 'events'
                events = entry.get("events", [])
                for event in events:
                    title = event.get("title") or event.get("slug") or "No Title"
                    desc = event.get("description", "")
                    
                    # محاولة جلب الوقت بكل الطرق الممكنة (CamelCase أو underscores)
                    start_ts = event.get("tsStart") or event.get("ts_start") or event.get("startTime")
                    end_ts = event.get("tsEnd") or event.get("ts_end") or event.get("endTime")
                    
                    if start_ts and end_ts:
                        # تحويل الوقت
                        s_val = int(start_ts)
                        e_val = int(end_ts)
                        start_xml = datetime.fromtimestamp(s_val, tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                        stop_xml = datetime.fromtimestamp(e_val, tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                        
                        prog = ET.SubElement(root, "programme", start=start_xml, stop=stop_xml, channel=str(channel_id))
                        ET.SubElement(prog, "title", lang="ar").text = str(title)
                        ET.SubElement(prog, "desc", lang="ar").text = str(desc)
                        
                        # جلب الصورة
                        imgs = event.get("images", [])
                        if imgs and isinstance(imgs, list):
                            ET.SubElement(prog, "icon", src=imgs[0].get("url", ""))
                        
                        found_events += 1

        # حفظ الملف
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write("epg_auto_updated.xml", encoding="utf-8", xml_declaration=True)
        print(f"✅ تم بنجاح! استخراج {found_events} برنامج من قنوات مختلفة.")

    except Exception as e:
        print(f"❌ خطأ تقني: {e}")

if __name__ == "__main__":
    update_epg_comprehensive()
