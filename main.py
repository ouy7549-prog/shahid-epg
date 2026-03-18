import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import json

def update_epg_final():
    # الرابط الأصلي الخاص بك
    url = "https://epg.aws.playco.com/api/v1.1/epg/category/events/d9521174b8d441a784909666d4d1ad7f-sp?ts_start=1773788400&ts_end=1773853200&lang=ar&pg=18&category=all&page=11&limit=10&pageNumberForCache=11"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    print("📡 جاري محاولة سحب البيانات من السيرفر...")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        full_response = response.json()

        # --- الجزء الأهم: استخراج القائمة الصحيحة ---
        # سنبحث عن القائمة في كل مكان محتمل (data أو items أو events)
        items = []
        if isinstance(full_response, list):
            items = full_response
        elif 'data' in full_response:
            d = full_response['data']
            items = d if isinstance(d, list) else d.get('items', d.get('events', []))
        elif 'items' in full_response:
            items = full_response['items']

        if not items:
            print("⚠️ السيرفر استجاب ولكن لا توجد برامج في هذه الصفحة (Page 11).")
            print("📝 محتوى الرد للتشخيص:", json.dumps(full_response, indent=2, ensure_ascii=False)[:500])
            return

        # بناء ملف XMLTV
        root = ET.Element("tv", {"generator-info-name": "Gemini-AWS-Fixer"})
        
        # إضافة قناة وهمية لربط البرامج بها
        channel_id = "AWS_PLAYCO_CH"
        chan_elem = ET.SubElement(root, "channel", id=channel_id)
        ET.SubElement(chan_elem, "display-name").text = "AWS Channel"

        count = 0
        for item in items:
            # استخراج الوقت (دعم كل المسميات الممكنة)
            s_ts = item.get('ts_start') or item.get('start_time') or item.get('startTime')
            e_ts = item.get('ts_end') or item.get('end_time') or item.get('endTime')
            
            if s_ts and e_ts:
                # تحويل الوقت لتنسيق XMLTV
                start_xml = datetime.fromtimestamp(int(s_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                stop_xml = datetime.fromtimestamp(int(e_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                
                # إنشاء عنصر البرنامج
                prog = ET.SubElement(root, "programme", start=start_xml, stop=stop_xml, channel=channel_id)
                ET.SubElement(prog, "title", lang="ar").text = item.get('title') or item.get('name') or "بدون عنوان"
                ET.SubElement(prog, "desc", lang="ar").text = item.get('description') or ""
                
                img = item.get('image') or item.get('poster_url')
                if img:
                    ET.SubElement(prog, "icon", src=img)
                count += 1

        # حفظ الملف
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write("epg_auto_updated.xml", encoding="utf-8", xml_declaration=True)
        print(f"✅ نجاح! تم استخراج {count} برنامج وحفظهم في epg_auto_updated.xml")

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    update_epg_final()
