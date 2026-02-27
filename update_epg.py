import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

def update_combined_epg():
    # 1. قائمة القنوات لـ "شاهد"
    channel_ids = "387238,387251,387296,387290,387293,49923122575716,387294,387937,400919,946945,946940,946938,995495,999927,49923088749329,49923068171559,49923697545394,946946,49923697648201,49923697657389,946942,49923691806580,49923697659290,49923120452582,49923088717401,49923088781412,49923697650617,49923697642137,49923088814140,49923697342447,49923712885383,969745,977946,975435,963543,1005232,49923086870104,988045,992538,983124,976272,409385,409390,387286,387288,946948,862837,49923569816895,1003218,49923693965985,49923446898171,49923639151416,997605,1001845,49923434082342,409387,418308,400917,400921,400924,989622,986064,986069,951783,49922904934759,986346,986014,986024,49923172117967,49922763891977,49923172215352,49922763510387,49923518527492,414449,1029746,388567,388566"
    
    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = (now + timedelta(days=2)).strftime("%Y-%m-%dT23:59:59.000Z")
    
    shahid_url = f"https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds={channel_ids}&language=ar&from={from_date}&to={to_date}&country=SA"
    m3u4u_url = "http://m3u4u.com/xml/5z3end4v6mud9jr2nqpk"

    headers = {'User-Agent': 'Mozilla/5.0'}

    root = ET.Element("tv", {"generator-info-name": "Combined Shahid & m3u4u"})

    # --- الجزء الأول: جلب بيانات "شاهد" ---
    try:
        print("📡 جاري جلب بيانات شاهد...")
        response = requests.get(shahid_url, headers=headers)
        shahid_data = response.json().get('items', [])
        for channel in shahid_data:
            ch_id = str(channel.get('channelId'))
            ET.SubElement(root, "channel", id=ch_id).append(ET.Element("display-name"))
            root.find(f"channel[@id='{ch_id}']/display-name").text = f"Shahid {ch_id}"
            
            for p in channel.get('items', []):
                start = p['from'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                stop = p['to'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                prog = ET.SubElement(root, "programme", start=start, stop=stop, channel=ch_id)
                ET.SubElement(prog, "title", lang="ar").text = p.get('title', 'N/A')
                ET.SubElement(prog, "desc", lang="ar").text = p.get('description', '')
                if p.get('productPoster'):
                    img = p['productPoster'].replace('{height}', '400').replace('{width}', '600').replace('{croppingPoint}', 'original')
                    ET.SubElement(prog, "icon", src=img)
    except Exception as e:
        print(f"⚠️ خطأ في جلب بيانات شاهد: {e}")

    # --- الجزء الثاني: جلب ودمج بيانات m3u4u ---
    try:
        print("📡 جاري جلب ودمج بيانات m3u4u...")
        response = requests.get(m3u4u_url, headers=headers)
        m3u4u_xml = ET.fromstring(response.content)
        
        # دمج القنوات (Channels)
        for channel in m3u4u_xml.findall("channel"):
            root.append(channel)
        
        # دمج البرامج (Programmes)
        for programme in m3u4u_xml.findall("programme"):
            root.append(programme)
    except Exception as e:
        print(f"⚠️ خطأ في دمج m3u4u: {e}")

    # حفظ الملف النهائي
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write("shahid_final.xml", encoding="utf-8", xml_declaration=True)
    print("✅ تم الدمج بنجاح في ملف واحد!")

if __name__ == "__main__":
    update_combined_epg()
