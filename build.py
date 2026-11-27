#!/usr/bin/env python3
"""Build index.html from the travel CSV.
   usage: python3 build.py [csv] [--external]   (--external = link logos/ instead of inlining)"""
import csv,re,sys,os,json,base64,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from airports import COORD,ALIAS,EXTRA

CSVP=next((a for a in sys.argv[1:] if not a.startswith('--')),
          '/Users/jzair/Downloads/Jeff Air Travel Track - Main Sheet.csv')
EXTERNAL='--external' in sys.argv
HERE=os.path.dirname(os.path.abspath(__file__))

NAME={'3K':'Jetstar Asia','7C':'Jeju Air','9C':'Spring Airlines','A3':'Aegean','AA':'American',
'AI':'Air India','AK':'AirAsia','AS':'Alaska','AY':'Finnair','AZ':'ITA Airways','B6':'JetBlue',
'CA':'Air China','CI':'China Airlines','CX':'Cathay Pacific','CZ':'China Southern','DL':'Delta',
'EK':'Emirates','ET':'Ethiopian','EY':'Etihad','FD':'Thai AirAsia','FM':'Shanghai Airlines',
'GJ':'Loong Air','HB':'Greater Bay','HK':'Hong Kong Airlines','HO':'Juneyao Air','HU':'Hainan Airlines',
'HX':'Hong Kong Airlines','JL':'Japan Airlines','KE':'Korean Air','KQ':'Kenya Airways','KU':'Kuwait Airways',
'LJ':'Jin Air','LX':'SWISS','MH':'Malaysia Airlines','MM':'Peach','MS':'EgyptAir','MU':'China Eastern',
'NH':'ANA','NK':'Spirit','NT':'Air Japan','NX':'Air Macau','OD':'Batik Air','OZ':'Asiana',
'PG':'Bangkok Airways','PR':'Philippine Airlines','QH':'Bamboo Airways','QR':'Qatar Airways',
'SC':'Shandong Airlines','SL':'Thai Lion Air','SQ':'Singapore Airlines','TG':'Thai Airways',
'TK':'Turkish Airlines','TR':'Scoot','UA':'United','VJ':'Vietjet','VN':'Vietnam Airlines',
'VZ':'Thai Vietjet','WK':'Edelweiss','WS':'WestJet','XW':'NokScoot','YP':'Air Premia','ZH':'Shenzhen Airlines'}
CN2EN={'中国':'China','新加坡':'Singapore','美国':'United States','卡塔尔':'Qatar',
'泰国':'Thailand','香港':'Hong Kong','菲律宾':'Philippines','老挝':'Laos','韩国':'South Korea',
'肯尼亚':'Kenya','加拿大':'Canada','阿联酋':'UAE','日本':'Japan','意大利':'Italy',
'埃及':'Egypt','瑞士':'Switzerland','越南':'Vietnam','马来西亚':'Malaysia','芬兰':'Finland',
'瑞典':'Sweden','印度':'India','科威特':'Kuwait','马尔代夫':'Maldives',
'哥斯达黎加':'Costa Rica','土耳其':'Turkey','台湾':'Taiwan','德国':'Germany',
'希腊':'Greece','澳门':'Macau'}
ZH_NAME={'3K': '捷星亚洲',
 '7C': '济州航空',
 '9C': '春秋航空',
 'A3': '爱琴海航空',
 'AA': '美国航空',
 'AI': '印度航空',
 'AK': '亚洲航空',
 'AS': '阿拉斯加航空',
 'AY': '芬兰航空',
 'AZ': '意大利航空',
 'B6': '捷蓝航空',
 'CA': '中国国际航空',
 'CI': '中华航空',
 'CX': '国泰航空',
 'CZ': '中国南方航空',
 'DL': '达美航空',
 'EK': '阿联酋航空',
 'ET': '埃塞俄比亚航空',
 'EY': '阿提哈德航空',
 'FD': '泰国亚洲航空',
 'FM': '上海航空',
 'GJ': '长龙航空',
 'HB': '大湾区航空',
 'HK': '香港航空',
 'HO': '吉祥航空',
 'HU': '海南航空',
 'HX': '香港航空',
 'JL': '日本航空',
 'KE': '大韩航空',
 'KQ': '肯尼亚航空',
 'KU': '科威特航空',
 'LJ': '真航空',
 'LX': '瑞士国际航空',
 'MH': '马来西亚航空',
 'MM': '乐桃航空',
 'MS': '埃及航空',
 'MU': '中国东方航空',
 'NH': '全日空',
 'NK': '精神航空',
 'NT': '',
 'NX': '澳门航空',
 'OD': '峇迪航空',
 'OZ': '韩亚航空',
 'PG': '曼谷航空',
 'PR': '菲律宾航空',
 'QH': '越竹航空',
 'QR': '卡塔尔航空',
 'SC': '山东航空',
 'SL': '泰国狮子航空',
 'SQ': '新加坡航空',
 'TG': '泰国国际航空',
 'TK': '土耳其航空',
 'TR': '酷航',
 'UA': '美国联合航空',
 'VJ': '越捷航空',
 'VN': '越南航空',
 'VZ': '泰越捷航空',
 'WK': '埃德尔维斯航空',
 'WS': '西捷航空',
 'XW': '酷鸟航空',
 'YP': '',
 'ZH': '深圳航空'}
CLS={'economy':'E','premium economy':'P','business':'J','first':'F'}

def code(c):
    c=(c or '').strip().upper()
    return ALIAS.get(c,c)
def num(s):
    s=re.sub(r'[^0-9.]','',s or '')
    return float(s) if s else 0.0
def gcmiles(a,b):
    la,lo=math.radians(a[1]),math.radians(a[0]); lb,ln=math.radians(b[1]),math.radians(b[0])
    return round(3958.8*2*math.asin(min(1,math.sqrt(math.sin((lb-la)/2)**2+
           math.cos(la)*math.cos(lb)*math.sin((ln-lo)/2)**2))))

rows=list(csv.DictReader(open(CSVP,encoding='utf-8')))

# in this sheet the column headed "Destination Country" actually holds the city in English,
# 城市 the city in Chinese and 国家 the country in Chinese.
city={}
for r in rows:
    d=code(r.get('Destination'))
    if not d or d in city: continue
    en=(r.get('Destination Country') or '').strip()
    if en: city[d]=(en,(r.get('城市') or '').strip(),(r.get('国家') or '').strip())
for k,v in EXTRA.items():
    if k not in city: city[k]=(v[0],v[1],v[3])

legs=[];used=set()
for r in rows:
    o,d=code(r.get('Origin')),code(r.get('Destination'))
    f=re.sub(r'\s+','',(r.get('Flight #') or '')).upper()
    dt=(r.get('Date') or '').strip()
    if not(o and d and f and dt and o in COORD and d in COORD): continue
    mm,dd,yy=[int(x) for x in dt.split('/')]
    al=f[:2]
    mi=int(num(r.get('Miles'))) or 0
    est=0
    if not mi: mi=gcmiles(COORD[o],COORD[d]); est=1
    # NOTE: cabin class and ticket price are deliberately NOT emitted -
    # index.html is published publicly, so only what the animation shows goes in.
    legs.append(['%04d-%02d-%02d'%(yy,mm,dd),f,al,o,d,mi,est,
                 (r.get('Note') or '').strip()[:70],int(num(r.get('Time Lag')) or 0)])
    used.add(o);used.add(d)
legs.sort(key=lambda x:x[0])

AP={}
for c in sorted(used):
    en,zh,cz=city.get(c,(c,'',''))
    AP[c]=[COORD[c][0],COORD[c][1],en,zh,cz,CN2EN.get(cz,'')]

AL={}
for c in sorted({l[2] for l in legs}):
    p=os.path.join(HERE,'logos',c+'.png')
    if os.path.exists(p):
        logo='logos/%s.png'%c if EXTERNAL else 'data:image/png;base64,'+base64.b64encode(open(p,'rb').read()).decode()
    else: logo=''
    AL[c]=[NAME.get(c,c),logo,ZH_NAME.get(c,'')]

tmpl=open(os.path.join(HERE,'template.html'),encoding='utf-8').read()
out=(tmpl.replace('/*__AP__*/','var AP='+json.dumps(AP,ensure_ascii=False,separators=(',',':'))+';')
         .replace('/*__AL__*/','var AL='+json.dumps(AL,ensure_ascii=False,separators=(',',':'))+';')
         .replace('/*__LG__*/','var LG='+json.dumps(legs,ensure_ascii=False,separators=(',',':'))+';'))
open(os.path.join(HERE,'index.html'),'w',encoding='utf-8').write(out)
tot=sum(l[5] for l in legs)
print('flights %d  airports %d  airlines %d (%d with logos)'%(
      len(legs),len(AP),len(AL),sum(1 for v in AL.values() if v[1])))
print('miles %s   est. rows %d   index.html %d KB'%(f'{tot:,}',sum(l[6] for l in legs),
      os.path.getsize(os.path.join(HERE,'index.html'))//1024))
