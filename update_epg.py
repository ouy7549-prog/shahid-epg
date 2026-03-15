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
    # Settings
    playco_ch_id = "720335400128"
    now = datetime.now(timezone.utc)
    
    # Precise Timestamps
    start_ts = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_ts = start_ts + (24 * 3600)
    
    from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = (now + timedelta(days=2)).strftime("%Y-%m-%dT23:59:59.000Z")

    # Corrected URLs
    url_shahid = "https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds=387238,387251,387296&language=ar&from=" + from_date + "&to=" + to_date + "&country=SA"
    url_playco = "https://epg.aws.playco.com/api/v1.1/epg/category/events/" + playco_ch_id + "-sp?ts_start=" + str(start_ts) + "&ts_end=" + str(end_ts) + "&lang=ar&pg=18&category=all&limit=999"
    url_m3u4u = "http://m3u4u.com/xml/5z3end4v6mud9jr2nqpk"

    # Browser-like Headers (Critical for Playco)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://starzplay.com'
    }

    root = ET.Element("tv")

    # --- 1. Playco Fetch (Priority) ---
    try:
        print("Checking Playco ID: " + playco_ch_id)
        r = requests.get(url_playco, headers=headers, timeout=20)
        data = r.json()
        
        # Add Channel Node
        ch_node = ET.SubElement(root, "channel", id=playco_ch_id)
        ET.SubElement(ch_node, "display-name").text = "Playco Channel"

        # Check for events in data
        events = data.get('data', {}).get('events', [])
        if not events:
            print("No events found for Playco in the JSON response.")
        
        for ev in events:
            st = datetime.fromtimestamp(int(ev['tsStart']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            en = datetime.fromtimestamp(int(ev['tsEnd']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            prog = ET.SubElement(root, "programme", start=st, stop=en, channel=playco_ch_id)
            ET.SubElement(prog, "title", lang="ar").text = ev.get('title', 'No Title')
            ET.SubElement(prog, "desc", lang="ar").text = ev.get('description', '')
        print("Playco: Done.")
    except Exception as e:
        print("Playco Error: " + str(e))

    # --- 2. m3u4u Fetch ---
    try:
        print("Checking m3u4u...")
        r = requests.get(url_m3u4u, headers=headers, timeout=25)
        m_xml = ET.fromstring(r.content)
        for c in m_xml.findall("channel"): root.append(c)
        for p in m_xml.findall("programme"): root.append(p)
        print("m3u4u: Done.")
    except: pass

    # --- 3. Save ---
    try:
        prettify(root)
        tree = ET.ElementTree(root)
        tree.write("combined_final.xml", encoding="utf-8", xml_declaration=True)
        
        # Verify if file has content
        if os.path.getsize("combined_final.xml") > 150:
            print("Success! File saved with data.")
        else:
            print("Warning: File created but looks empty.")
    except Exception as e:
        print("Save Error: " + str(e))

if __name__ == "__main__":
    update_combined_epg()
