import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def update_combined_epg():
    # الرابط الخاص بك
    url_aws = "https://epg.aws.playco.com/api/v1.1/epg/category/events/d9521174b8d441a784909666d4d1ad7f-sp?ts_start=1773788400&ts_end=1773853200&lang=ar&pg=18&category=all&page=11&limit=10&pageNumberForCache=11"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    root = ET.Element("tv", {"generator-info-name": "AWS Playco Fix"})

    try:
        print("📡 جاري محاولة استخراج البيانات من الرابط...")
        response = requests.get(url_aws, headers=headers)
        response.raise_for_status()
        full_data = response.json()

        # الوصول لمكان البيانات الصحيح في روابط Playco
        # الرابط يعيد كائن يحتوي على 'data' وبداخلها قائمة 'events' أو 'items'
        items = []
        if 'data' in full_data:
            if isinstance(full_data['data'], list):
                items = full_data['data']
            elif 'items' in full_data['data']:
                items = full_data['data']['items']
        
        if not items:
            print("⚠️ تنبيه: تم الاتصال بالرابط ولكن لم يتم العثور على برامج (قائمة فارغة).")
        
        for item in items:
            # استخراج الحقول مع دعم المسميات المختلفة
            title = item.get('title') or item.get('name') or "برنامج غير معروف"
            desc = item.get('description') or item.get('short_description') or ""
            start_ts = item.get('ts_start') or item.get('start_time') or item.get('startTime')
            end_ts = item.get('ts_end') or item.get('end_time') or item.get('endTime')
            ch_id = item.get('channel_id') or "AWS_CH_1"

            if start_ts and end_ts:
                # تحويل الوقت من ثواني إلى تنسيق XMLTV
                start_xml = datetime.fromtimestamp(int(start_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                stop_xml = datetime.fromtimestamp(int(end_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')

                prog = ET.SubElement(root, "programme", start=start_xml, stop=stop_xml, channel=str(ch_id))
                ET.SubElement(prog, "title", lang="ar").text = title
                ET.SubElement(prog, "desc", lang="ar").text = desc
                
                # إضافة الصورة
                img = item.get('image') or item.get('poster_url')
                if img:
                    ET.SubElement(prog, "icon", src=img)

        print(f"✅ تم استخراج {len(items)} برنامج بنجاح.")

    except Exception as e:
        print(f"❌ خطأ تقني: {e}")

    # حفظ الملف
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write("epg_auto_updated.xml", encoding="utf-8", xml_declaration=True)
    print("📁 تم تحديث الملف: epg_auto_updated.xml")

if __name__ == "__main__":
    update_combined_epg()
