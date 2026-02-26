import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

def convert_shahid_to_xmltv_v3():
    # 1. إعداد التواريخ (أمس واليوم وغداً) لضمان عدم وجود فراغات في الجدول
    now = datetime.now(timezone.utc)
    start_dt = now - timedelta(days=1)
    end_dt = now + timedelta(days=2) # جلب بيانات لـ 48 ساعة قادمة
    
    from_date = start_dt.strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = end_dt.strftime("%Y-%m-%dT23:59:59.000Z")
    
    # قائمة القنوات الكاملة
    channel_ids = "387238,387251,387296,387290,387293,49923122575716,387294,387937,400919,946945,946940,946938,995495,999927,49923088749329,49923068171559,49923697545394,946946,49923697648201,49923697657389,946942,49923691806580,49923697659290,49923120452582,49923088717401,49923088781412,49923697650617,49923697642137,49923088814140,49923697342447,49923712885383,969745,977946,975435,963543,1005232,49923086870104,988045,992538,983124,976272,409385,409390,387286,387288,946948,862837,49923569816895,1003218,49923693965985,49923446898171,49923639151416,997605,1001845,49923434082342,409387,418308,400917,400921,400924,989622,986064,986069,951783,49922904934759,986346,986014,986024,49923172117967,49922763891977,49923172215352,49922763510387,49923518527492,414449,1029746,388567,388566"
    
    api_url = f"https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds={channel_ids}&language=ar&from={from_date}&to={to_date}&country=SA"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://shahid.mbc.net/'
    }

    try:
        print(f"📡 جاري تحديث الجدول الزمني (3 أيام)...")
        response = requests.get(api_url, headers=headers)
        data = response.json()
        channels_list = data.get('items', [])
        
        root = ET.Element("tv", {"generator-info-name": "Shahid EPG Master"})

        for channel in channels_list:
            ch_id = str(channel.get('channelId'))
            programs = channel.get('items', [])
            
            # تعريف القناة
            channel_node = ET.SubElement(root, "channel", id=ch_id)
            ET.SubElement(channel_node, "display-name").text = f"Channel {ch_id}"
            
            for p in programs:
                # تحويل الوقت مع إضافة إزاحة +0000 ليكون UTC عالمي
                # أغلب التطبيقات تعالج +0000 وتعدله حسب توقيت الهاتف تلقائياً
                start_iso = p['from'].split('.')[0].replace('-', '').replace(':', '').replace('T', '')
                stop_iso = p['to'].split('.')[0].replace('-', '').replace(':', '').replace('T', '')
                
                prog_node = ET.SubElement(root, "programme", 
                                        start=f"{start_iso} +0000", 
                                        stop=f"{stop_iso} +0000", 
                                        channel=ch_id)
                
                ET.SubElement(prog_node, "title", lang="ar").text = p.get('title', 'N/A')
                ET.SubElement(prog_node, "desc", lang="ar").text = p.get('description', '')
                
                if p.get('productPoster'):
                    # تنظيف رابط الصورة ليعمل في كافة التطبيقات
                    img_url = p['productPoster'].replace('{height}', '400').replace('{width}', '600').replace('{croppingPoint}', 'original')
                    ET.SubElement(prog_node, "icon", src=img_url)

        tree = ET.ElementTree(root)
        # استخدام إزاحة بادئة (indentation) لجعل الملف مقروءاً وسهل التحميل
        ET.indent(tree, space="\t", level=0) 
        tree.write("shahid_final.xml", encoding="utf-8", xml_declaration=True)
        print(f"✅ تم تحديث الجدول بنجاح! الملف 'shahid_final.xml' جاهز.")

    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    convert_shahid_to_xmltv_v3()