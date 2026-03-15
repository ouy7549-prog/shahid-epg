import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import time
import os

def update_combined_epg():
    # 1. إعدادات القناة المطلوبة من Playco
    playco_ch_id = "720335400128"
    start_ts = int((datetime.now(timezone.utc)).replace(hour=0, minute=0, second=0).timestamp())
    end_ts = start_ts + 86400 
    playco_url = f"https://epg.aws.playco.com/api/v1.1/epg/category/events/{playco_ch_id}-sp?ts_start={start_ts}&ts_end={end_ts}&lang=ar&pg=18&category=all&limit=999"

    # 2. إعدادات شاهد و m3u4u
    channel_ids = "387238,387251,387296,387290,387293" # اختصرت القائمة للتبسيط في الكود
    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = (now + timedelta(days=2)).strftime("%Y-%m-%dT23:59:59.000Z")
    shahid_url = f"https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds={channel_ids}&language=ar&from={from_date}&to={to_date}&country=SA"
    m3u4u_url = "http://m3u4u.com/xml/5z3end4v6mud9jr2nqpk"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    root = ET.Element("tv", {"generator-info-name": "Combined EPG"})

    # --- الجزء الأول: جلب بيانات شاهد ---
    try:
        print("📡 محاولة جلب بيانات شاهد...")
        response = requests.get(shahid_url, headers=headers, timeout=15)
        response.raise_for_status()
        shahid_data = response.json().get('items', [])
        for channel in shahid_data:
            ch_id = str(channel.get('channelId'))
            ch_node = ET.SubElement(root, "channel", id=ch_id)
            ET.SubElement(ch_node, "display-name").text = f"Shahid {ch_id}"
            for p in channel.get('items', []):
                start = p['from'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                stop = p['to'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                prog = ET.SubElement(root, "programme", start=start, stop=stop, channel=ch_id)
                ET.SubElement(prog, "title", lang="ar").text = p.get('title', 'N/A')
                ET.SubElement(prog, "desc", lang="ar").text = p.get('description', '')
        print("✅ اكتمل جزء شاهد.")
    except Exception as e:
        print(f"⚠️ فشل جلب شاهد (تم التخطي): {e}")

    # --- الجزء الثاني: جلب بيانات Playco ---
    try:
        print(f"📡 محاولة جلب بيانات Playco ID: {playco_ch_id}...")
        res = requests.get(playco_url, headers=headers, timeout=15)
        res.raise_for_status()
        playco_data = res.json()
        ET.SubElement(root, "channel", id=playco_ch_id).append(ET.Element("display-name"))
        root.find(f"channel[@id='{playco_ch_id}']/display-name").text = f"Playco {playco_ch_id}"
        events = playco_data.get('data', {}).get('events', [])
        for event in events:
            start_str = datetime.fromtimestamp(int(event['tsStart']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            stop_str = datetime.fromtimestamp(int(event['tsEnd']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            prog = ET.SubElement(root, "programme", start=start_str, stop=stop_str, channel=playco_ch_id)
            ET.SubElement(prog, "title", lang="ar").text = event.get('title', 'N/A')
            ET.SubElement(prog, "desc", lang="ar").text = event.get('description', '')
        print("✅ اكتمل جزء Playco.")
    except Exception as e:
        print(f"⚠️ فشل جلب Playco (تم التخطي): {e}")

    # --- الجزء الثالث: جلب بيانات m3u4u ---
    try:
        print("📡 محاولة جلب بيانات m3u4u...")
        response = requests.get(m3u4u_url, headers=headers, timeout=20)
        m3u4u_xml = ET.fromstring(response.content)
        for channel in m3u4u_xml.findall("channel"): root.append(channel)
        for programme in m3u4u_xml.findall("programme"): root.append(programme)
        print("✅ اكتمل جزء m3u4u.")
    except Exception as e:
        print(f"⚠️ فشل جلب m3u4u (تم التخطي): {e}")

    # --- حفظ الملف النهائي (سيتم الحفظ حتى لو فشل أحد المصادر) ---
    try:
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        filename = "combined_final.xml"
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        print("-" * 30)
        print(f"✨ تم إنشاء الملف بنجاح: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"❌ خطأ فادح في كتابة الملف: {e}")

if __name__ == "__main__":
    update_combined_epg()
