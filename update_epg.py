import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import time
import os

def update_combined_epg():
    # 1. Settings
    playco_ch_id = "720335400128"
    
    now = datetime.now(timezone.utc)
    
    # Shahid Times
    from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = (now + timedelta(days=2)).strftime("%Y-%m-%dT23:59:59.000Z")
    
    # Playco Times (Unix Timestamp)
    start_ts = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_ts = start_ts + (24 * 3600)

    # URLs
    shahid_ch_ids = "387238,387251,387296,387290,387293,49923122575716,387294,387937,400919,946945,946940,946938,995495,999927,49923088749329,49923068171559,49923697545394,946946,49923697648201,49923697657389,946942,49923691806580,49923697659290,49923120452582,49923088717401,49923088781412,49923697650617,49923697642137,49923088814140,49923697342447,49923712885383,969745,977946,975435,963543,1005232,49923086870104,988045,992538,983124,976272,409385,409390,387286,387288,946948,862837,49923569816895,1003218,49923693965985,49923446898171,49923639151416,997605,1001845,49923434082342,409387,418308,400917,400921,400924,989622,986064,986069,951783,49922904934759,986346,986014,986024,49923172117967,49922763891977,49923172215352,49922763510387,49923518527492,414449,1029746,388567,388566"
    shahid_url = f"https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds={shahid_ch_ids}&language=ar&from={from_date}&to={to_date}&country=SA"
    playco_url = f"https://epg.aws.playco.com/api/v1.1/epg/category/events/{playco_ch_id}-sp?ts_start={start_ts}&ts_end={end_ts}&lang=ar&pg=18&category=all&limit=999"
    m3u4u_url = "http://m3u4u.com/xml/5z3end4v6mud9jr2nqpk"

    headers = {'User-Agent': 'Mozilla/5.0'}
    root = ET.Element("tv", {"generator-info-name": "Combined EPG"})

    # --- Section 1: Shahid ---
    try:
        print("Processing Shahid...")
        response = requests.get(shahid_url, headers=headers, timeout=20)
        items = response.json().get('items', [])
        for channel in items:
            ch_id = str(channel.get('channelId'))
            ch_node = ET.SubElement(root, "channel", id=ch_id)
            ET.SubElement(ch_node, "display-name").text = f"Shahid {ch_id}"
            for p in channel.get('items', []):
                start = p['from'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                stop = p['to'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                prog = ET.SubElement(root, "programme", start=start, stop=stop, channel=ch_id)
                ET.SubElement(prog, "title", lang="ar").text = p.get('title', 'N/A')
                ET.SubElement(prog, "desc", lang="ar").text = p.get('description', '')
    except Exception as e:
        print(f"Shahid Error: {e}")

    # --- Section 2: Playco ---
    try:
        print(f"Processing Playco ID: {playco_ch_id}...")
        response = requests.get(playco_url, headers=headers, timeout=20)
        p_data = response.json()
        ch_node = ET.SubElement(root, "channel", id=playco_ch_id)
        ET.SubElement(ch_node, "display-name").text = f"Playco {playco_ch_id}"
        events = p_data.get('data', {}).get('events', [])
        for event in events:
            s_t = datetime.fromtimestamp(int(event['tsStart']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            e_t = datetime.fromtimestamp(int(event['tsEnd']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            prog = ET.SubElement(root, "programme", start=s_t, stop=e_t, channel=playco_ch_id)
            ET.SubElement(prog, "title", lang="ar").text = event.get('title', 'N/A')
            ET.SubElement(prog, "desc", lang="ar").text = event.get('description', '')
    except Exception as e:
        print(f"Playco Error: {e}")

    # --- Section 3: m3u4u ---
    try:
        print("Processing m3u4u...")
        response = requests.get(m3u4u_url, headers=headers, timeout=30)
        m_xml = ET.fromstring(response.content)
        for c in m_xml.findall("channel"): root.append(c)
        for p in m_xml.findall("programme"): root.append(p)
    except Exception as e:
        print(f"m3u4u Error: {e}")

    # --- Final Save ---
    try:
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        tree.write("combined_final.xml", encoding="utf-8", xml_declaration=True)
        print("Success! File saved as: combined_final.xml")
    except Exception as e:
        print(f"Save Error: {e}")

if __name__ == "__main__":
    update_combined_epg()
