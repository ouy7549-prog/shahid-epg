import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import os

def prettify(elem, level=0):
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            prettify(subelem, level + 1)
        if not subelem.tail or not subelem.tail.strip():
            subelem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def update_combined_epg():
    playco_ch_id = "720335400128"
    now = datetime.now(timezone.utc)
    
    # حساب الوقت بدقة (بداية اليوم ونهايته)
    start_ts = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_ts = start_ts + 86400
    
    from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = (now + timedelta(days=2)).strftime("%Y-%m-%dT23:59:59.000Z")

    # الروابط
    url_playco = "https://epg.aws.playco.com/api/v1.1/epg/category/events/" + playco_ch_id + "-sp?ts_start=" + str(start_ts) + "&ts_end=" + str(end_ts) + "&lang=ar&pg=18&category=all&limit=999"
    url_shahid = "https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds=387238,387251,387296&language=ar&from=" + from_date + "&to=" + to_date + "&country=SA"
    url_m3u4u = "http://m3u4u.com/xml/5z3end4v6mud9jr2nqpk"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://starzplay.com/',
        'Origin': 'https://starzplay.com'
    }

    root = ET.Element("tv")

    # --- معالجة Playco ---
    try:
        print("Requesting Playco data...")
        r = requests.get(url_playco, headers=headers, timeout=20)
        json_obj = r.json()
        
        # التأكد من مكان وجود البيانات في الـ JSON
        # السيرفر أحياناً يضع البيانات داخل 'data' وأحياناً مباشرة
        events = []
        if 'data' in json_obj and 'events' in json_obj['data']:
            events = json_obj['data']['events']
        elif 'events' in json_obj:
            events = json_obj['events']
            
        if events:
            # إضافة القناة فقط إذا وجدت برامج
            ch_node = ET.SubElement(root, "channel", id=playco_ch_id)
            ET.SubElement(ch_node, "display-name").text = "Playco Channel"
            
            for ev in events:
                st = datetime.fromtimestamp(int(ev['tsStart']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                en = datetime.fromtimestamp(int(ev['tsEnd']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                prog = ET.SubElement(root, "programme", start=st, stop=en, channel=playco_ch_id)
                ET.SubElement(prog, "title", lang="ar").text = ev.get('title', 'No Title')
                ET.SubElement(prog, "desc", lang="ar").text = ev.get('description', '')
            print("Successfully added " + str(len(events)) + " programs from Playco.")
        else:
            print("Playco returned 0 events. Check if the ID " + playco_ch_id + " is still active.")
    except Exception as e:
        print("Playco Request Failed: " + str(e))

    # --- معالجة m3u4u ---
    try:
        print("Requesting m3u4u data...")
        r = requests.get(url_m3u4u, headers=headers, timeout=25)
        m_xml = ET.fromstring(r.content)
        count = 0
        for c in m_xml.findall("channel"): 
            root.append(c)
        for p in m_xml.findall("programme"): 
            root.append(p)
            count += 1
        print("Successfully merged " + str(count) + " programs from m3u4u.")
    except Exception as e:
        print("m3u4u Error: " + str(e))

    # --- الحفظ النهائي ---
    try:
        prettify(root)
        tree = ET.ElementTree(root)
        output = "combined_final.xml"
        tree.write(output, encoding="utf-8", xml_declaration=True)
        
        size = os.path.getsize(output)
        print("File saved. Size: " + str(size) + " bytes.")
        if size < 200:
            print("CRITICAL: File is almost empty. Check your internet or source links.")
    except Exception as e:
        print("Final Save Error: " + str(e))

if __name__ == "__main__":
    update_combined_epg()
