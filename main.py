import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def diagnose_and_fix_epg():
    # الرابط الذي زودتني به (سنستخدمه كما هو للتأكد من المحتوى)
    url = "https://epg.aws.playco.com/api/v1.1/epg/category/events/d9521174b8d441a784909666d4d1ad7f-sp?ts_start=1773788400&ts_end=1773853200&lang=ar&pg=18&category=all&page=11&limit=10&pageNumberForCache=11"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://shashatity.com', # بعض السيرفرات تطلب هذا المصدر
        'Referer': 'https://shashatity.com/'
    }

    print("🚀 جاري فحص الرابط مباشرة...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📡 حالة الرد من السيرفر: {response.status_code}")
        
        # تحويل الرد إلى JSON
        data = response.json()
        
        # --- السحر هنا: سنطبع مفاتيح البيانات لنعرف أين المشكلة ---
        print("🔑 المفاتيح الموجودة في الرد:", list(data.keys()))
        
        # إذا كانت هناك رسالة خطأ من السيرفر نفسه
        if 'message' in data:
            print(f"💬 رسالة السيرفر: {data['message']}")

        # البحث عن القائمة الفعلية
        # في نظام Playco، البيانات غالباً تكون تحت 'data' -> 'items' أو 'data' مباشرة
        items = []
        if 'data' in data:
            if isinstance(data['data'], list):
                items = data['data']
            elif 'items' in data['data']:
                items = data['data']['items']
        
        if not items:
            print("❌ لم يتم العثور على أي برامج. السيرفر أرسل رداً فارغاً.")
            # طباعة الرد كاملاً لنفهمه
            print("📝 محتوى الرد الكامل:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return

        # بناء ملف XML إذا وجدنا بيانات
        root = ET.Element("tv", {"generator-info-name": "AWS Playco Manual Fix"})
        for item in items:
            start_t = item.get('ts_start') or item.get('start_time')
            end_t = item.get('ts_end') or item.get('end_time')
            
            if start_t and end_t:
                start_xml = datetime.fromtimestamp(int(start_t), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                stop_xml = datetime.fromtimestamp(int(end_t), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                
                prog = ET.SubElement(root, "programme", start=start_xml, stop=stop_xml, channel="CH1")
                ET.SubElement(prog, "title", lang="ar").text = item.get('title', 'N/A')
                ET.SubElement(prog, "desc", lang="ar").text = item.get('description', '')

        tree = ET.ElementTree(root)
        tree.write("debug_epg.xml", encoding="utf-8", xml_declaration=True)
        print(f"✅ تم استخراج {len(items)} برنامج وحفظهم في debug_epg.xml")

    except Exception as e:
        print(f"💥 خطأ قاتل: {e}")

import json
if __name__ == "__main__":
    diagnose_and_fix_epg()
