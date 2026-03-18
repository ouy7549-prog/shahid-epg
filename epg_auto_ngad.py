import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

def update_combined_epg():
    # --- 1. حساب التوقيت التلقائي (Unix Timestamp) ---
    now = datetime.now(timezone.utc)
    # بداية اليوم الحالي (الساعة 00:00:00)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    ts_start = int(start_of_day.timestamp())
    
    # نهاية اليوم التالي (بعد 48 ساعة تقريباً) لتغطية جدول يومين
    end_of_period = start_of_day + timedelta(days=2)
    ts_end = int(end_of_period.timestamp())

    # --- 2. بناء الرابط الجديد مع المعطيات التلقائية ---
    # استبدلنا الأرقام الثابتة بـ {ts_start} و {ts_end}
    base_url = "https://epg.aws.playco.com/api/v1.1/epg/category/events/d9521174b8d441a784909666d4d1ad7f-sp"
    params = {
        "ts_start": ts_start,
        "ts_end": ts_end,
        "lang": "ar",
        "category": "all",
        "limit": 50, # زدت الحد لجلب برامج أكثر في طلب واحد
        "page": 1
    }

    m3u4u_url = "http://m3u4u.com/xml/5z3end4v6mud9jr2nqpk"
    headers = {'User-Agent': 'Mozilla/5.0'}

    root = ET.Element("tv", {"generator-info-name": "Dynamic AWS Playco EPG"})

    # --- 3. جلب بيانات AWS Playco ---
    try:
        print(f"📡 جاري جلب البيانات للفترة من {start_of_day} إلى {end_of_period}...")
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        # ملاحظة: في روابط Playco، البيانات قد تكون مباشرة في قائمة أو داخل 'data'
        events = data.get('data', []) if isinstance(data.get('data'), list) else data.get('items', [])

        for event in events:
            # استخراج المعرف (معالجة اختلاف الأسماء البرمجية)
            ch_id = event.get('channel_id') or event.get('channelId') or "AWS_CH"
            
            # تحويل الوقت من Unix Timestamp إلى تنسيق XMLTV
            s_ts = event.get('start_time') or event.get('startTime') or event.get('ts_start')
            e_ts = event.get('end_time') or event.get('endTime') or event.get('ts_end')
            
            if s_ts and e_ts:
                start_xml = datetime.fromtimestamp(int(s_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                stop_xml = datetime.fromtimestamp(int(e_ts), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')

                prog = ET.SubElement(root, "programme", start=start_xml, stop=stop_xml, channel=str(ch_id))
                ET.SubElement(prog, "title", lang="ar").text = event.get('title', 'N/A')
                ET.SubElement(prog, "desc", lang="ar").text = event.get('description', '')
                
                # إضافة بوستر البرنامج إن وجد
                img = event.get('image') or event.get('poster')
                if img:
                    ET.SubElement(prog, "icon", src=img)

    except Exception as e:
        print(f"⚠️ خطأ في جلب بيانات AWS: {e}")

    # --- 4. دمج بيانات m3u4u ---
    try:
        print("📡 جاري دمج بيانات m3u4u...")
        res_m3u = requests.get(m3u4u_url, headers=headers)
        if res_m3u.status_code == 200:
            m3u_xml = ET.fromstring(res_m3u.content)
            for item in m3u_xml:
                root.append(item)
    except Exception as e:
        print(f"⚠️ خطأ في دمج m3u4u: {e}")

    # --- 5. حفظ الملف ---
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write("epg_auto_updated.xml", encoding="utf-8", xml_declaration=True)
    print(f"✅ تم التحديث! الملف جاهز: epg_auto_updated.xml (يحتوي على {len(root.findall('programme'))} برنامج)")

if __name__ == "__main__":
    update_combined_epg()
