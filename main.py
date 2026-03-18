import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import json

def update_combined_epg():
    # 1. حساب الوقت الحالي تلقائياً لضمان وجود بيانات
    now = datetime.now(timezone.utc)
    ts_start = int(now.replace(hour=0, minute=0, second=0).timestamp())
    ts_end = int((now + timedelta(days=1)).replace(hour=23, minute=59, second=59).timestamp())

    # الرابط مع المتغيرات الزمنية التلقائية
    url_aws = f"https://epg.aws.playco.com/api/v1.1/epg/category/events/d9521174b8d441a784909666d4d1ad7f-sp?ts_start={ts_start}&ts_end={ts_end}&lang=ar&category=all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    root = ET.Element("tv", {"generator-info-name": "AWS Playco Auto-Fix"})

    try:
        print(f"📡 محاولة الاتصال بالرابط: {url_aws}")
        response = requests.get(url_aws, headers=headers)
        response.raise_for_status()
        
        # طباعة أول 500 حرف من البيانات للتأكد من وصولها (للـ Debug)
        full_data = response.json()
        print("🔍 فحص بنية البيانات المستلمة...")
        
        # محاولة العثور على القائمة التي تحتوي على البرامج
        items = []
        if isinstance(full_data, list):
            items = full_data
        elif 'data' in full_data:
            data_content = full_data['data']
            items = data_content if isinstance(data_content, list) else data_content.get('items', [])
        elif 'items' in full_data:
            items = full_data['items']

        print(f"📊 عدد البرامج التي تم العثور عليها: {len(items)}")

        for index, item in enumerate(items):
            # استخراج البيانات الأساسية
            title = item.get('title') or item.get('name') or "عنوان غير متوفر"
            desc = item.get('description') or ""
            
            # معالجة الوقت (نبحث في كل المفاتيح الممكنة للوقت)
            s_ts = item.get('ts_start') or item.get('start_time') or item.get('startTime')
            e_ts = item.get('ts_end') or item.get('end_time') or item.get('endTime')
            ch_id = item.get('channel_id') or item.get('channel_external_id') or "CH_UNKNOWN"

            if s_ts and e_ts:
                start_xml = datetime.fromtimestamp(int(s_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                stop_xml = datetime.fromtimestamp(int(e_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')

                prog = ET.SubElement(root, "programme", start=start_xml, stop=stop_xml, channel=str(ch_id))
                ET.SubElement(prog, "title", lang="ar").text = str(title)
                ET.SubElement(prog, "desc", lang="ar").text = str(desc)
                
                img = item.get('image') or item.get('poster')
                if img:
                    ET.SubElement(prog, "icon", src=str(img))

    except Exception as e:
        print(f"❌ حدث خطأ أثناء التحليل: {e}")

    # حفظ الملف النهائي
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    file_name = "epg_auto_updated.xml"
    tree.write(file_name, encoding="utf-8", xml_declaration=True)
    print(f"✅ تم الانتهاء! الملف المحفوظ: {file_name}")

if __name__ == "__main__":
    update_combined_epg()
