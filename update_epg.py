import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import os

def prettify(elem, level=0):
    """Manual function to replace ET.indent for older Python versions"""
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            prettify(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def update_combined_epg():
    # Configuration
    playco_ch_id = "720335400128"
    now = datetime.now(timezone.utc)
    
    # Times
    from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = (now + timedelta(days=2)).strftime("%Y-%m-%dT23:59:59.000Z")
    start_ts = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_ts = start_ts + (24 * 3600)

    # URLs
    s_ids = "387238,387251,387296,387290,387293,49923122575716,387294,387937,400919,946945,946940,946938,995495,999927,49923088749329,49923068171559,49923697545394,946946,49923697648201,49923697657389,946942,49923691806580,49923697659290,49923120452582,49923088717401,49923088781412,49923697650617,49923697642137,49923088814140,49923697342447,49923712885383,969745,977946,975435,963543,1005232,49923086870104,988045,992538,983124,976272,409385,409390,387286,387288,946948,862837,49923569816895,1003218,49923693965985,49923446898171,49923639151416,997605,1001845,49923434082342,409387,418308,400917,400921,400924,989622,986064,986069,951783,49922904934759,986346,986014,986024,49923172117967,49922763891977,49923172215352,49922763510387,49923518527492,414449,1029746,388567,388566"
    
    url_shahid = "https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds=" + s_ids + "&language=ar&from=" + from_date + "&to=" + to_date + "&country=SA"
    url_playco = "https://epg.aws.playco.com/api/v1.1/epg/category/events/" + playco_ch_id + "-sp?ts_start=" + str(start_ts) + "&ts_end=" + str(end_ts) + "&lang=ar&pg=18&category=all&limit=999"
    url_m3u4u = "http://m3u4u.com/xml/5z3end4v6mud9jr2nqpk"

    headers = {'User-Agent': 'Mozilla/5.0'}
    root = ET.Element("tv")

    # Part 1: Shahid
    try:
        print("Working on Shahid...")
        r = requests.get(url_shahid, headers=headers, timeout=20)
        for ch in r.json().get('items', []):
            cid = str(ch.get('channelId'))
            node = ET.SubElement(root, "channel", id=cid)
            ET.SubElement(node, "display-name").text = "Shahid " + cid
            for p in ch.get('items', []):
                st = p['from'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                en = p['to'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                prog = ET.SubElement(root, "programme", start=st, stop=en, channel=cid)
                ET.SubElement(prog, "title", lang="ar").text = p.get('title', 'N/A')
                ET.SubElement(prog, "desc", lang="ar").text = p.get('description', '')
    except: pass

    # Part 2: Playco
    try:
        print("Working on Playco...")
        r = requests.get(url_playco, headers=headers, timeout=20)
        data = r.json()
        node = ET.SubElement(root, "channel", id=playco_ch_id)
        ET.SubElement(node, "display-name").text = "Playco " + playco_ch_id
        for ev in data.get('data', {}).get('events', []):
            st = datetime.fromtimestamp(int(ev['tsStart']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            en = datetime.fromtimestamp(int(ev['tsEnd']), tz=timezone.utc).strftime('%Y%m%d%H%M%S +0000')
            prog = ET.SubElement(root, "programme", start=st, stop=en, channel=playco_ch_id)
            ET.SubElement(prog, "title", lang="ar").text = ev.get('title', 'N/A')
            ET.SubElement(prog, "desc", lang="ar").text = ev.get('description', '')
    except: pass

    # Part 3: m3u4u
    try:
        print("Working on m3u4u...")
        r = requests.get(url_m3u4u, headers=headers, timeout=30)
        m_xml = ET.fromstring(r.content)
        for c in m_xml.findall("channel"): root.append(c)
        for p in m_xml.findall("programme"): root.append(p)
    except: pass

    # Save
    try:
        prettify(root)
        tree = ET.ElementTree(root)
        tree.write("combined_final.xml", encoding="utf-8", xml_declaration=True)
        print("Completed! Check: combined_final.xml")
    except Exception as e:
        print("Final Error: " + str(e))

if __name__ == "__main__":
    update_combined_epg()
