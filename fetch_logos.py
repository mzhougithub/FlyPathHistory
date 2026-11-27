"""Download + shrink one PNG logo per airline IATA code into ./logos/ (cached)."""
import csv,re,os,sys,io,urllib.request
from PIL import Image

CSVP=sys.argv[1] if len(sys.argv)>1 else '/Users/jzair/Downloads/Jeff Air Travel Track - Main Sheet.csv'
OUT='logos'; os.makedirs(OUT,exist_ok=True)
SRC=["https://pics.avs.io/200/200/%s.png",
     "https://content.airhex.com/content/logos/airlines_%s_200_200_s.png"]
# the sheet uses a few codes that belong to other carriers
FIX={"HK":"HX","NT":"NQ"}
# defunct carriers whose code now resolves to an unrelated logo
DROP={"XW"}

codes=set()
for r in csv.DictReader(open(CSVP,encoding='utf-8')):
    f=re.sub(r'\s+','',r.get('Flight #') or '')
    if len(f)>=3 and (r.get('Origin') or '').strip(): codes.add(f[:2].upper())

def shrink(data):
    im=Image.open(io.BytesIO(data)).convert('RGBA')
    bg=Image.new('RGBA',im.size,(255,255,255,255))
    im=Image.alpha_composite(bg,im).convert('RGB')
    px=im.load();W,H=im.size;x0,y0,x1,y1=W,H,-1,-1
    for y in range(H):
        for x in range(W):
            r,g,b=px[x,y]
            if r<245 or g<245 or b<245:
                if x<x0:x0=x
                if y<y0:y0=y
                if x>x1:x1=x
                if y>y1:y1=y
    if x1<0 or (x1-x0)<8 or (y1-y0)<4: return None          # blank / placeholder
    im=im.crop((x0,y0,x1+1,y1+1))
    if im.width/im.height>9: return None                     # a bare rule, not a logo
    h=40;w=max(1,round(im.width*h/im.height))
    if w>260: w=260; im=im.resize((w,h),Image.LANCZOS)
    else: im=im.resize((w,h),Image.LANCZOS)
    im=im.quantize(colors=20,method=Image.FASTOCTREE)
    b=io.BytesIO();im.save(b,'PNG',optimize=True)
    return b.getvalue()

got=miss=0
for c in sorted(codes):
    p=os.path.join(OUT,c+'.png')
    if c in DROP: miss+=1; print('skip',c,'(no reliable logo)'); continue
    if os.path.exists(p): got+=1; continue
    data=None
    for u in SRC:
        try:
            req=urllib.request.Request(u%FIX.get(c,c),headers={'User-Agent':'logo-fetch/1.0'})
            raw=urllib.request.urlopen(req,timeout=20).read()
            if len(raw)>200:
                data=shrink(raw)
                if data: break
        except Exception: pass
    if data: open(p,'wb').write(data); got+=1; print('ok  ',c,len(data))
    else: miss+=1; print('MISS',c)
print('codes',len(codes),'have',got,'missing',miss)
