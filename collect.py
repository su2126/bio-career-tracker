"""Public Google News RSS discovery, not official job-opening verification."""
import datetime as dt, json, urllib.parse, urllib.request, xml.etree.ElementTree as ET, email.utils, os, smtplib
from email.message import EmailMessage
with open('companies.json',encoding='utf8') as f:
    names=[x['name'] for x in json.load(f)]
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
items=[]
for name in names:
    query=f'"{name}" (채용 OR 신입 OR 인턴) when:14d'
    url='https://news.google.com/rss/search?q='+urllib.parse.quote(query)+'&hl=ko&gl=KR&ceid=KR:ko'
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 BioCareerTracker/1.0'})
        with urllib.request.urlopen(req,timeout=20) as resp: root=ET.fromstring(resp.read())
        for e in root.findall('./channel/item')[:10]:
            title=e.findtext('title','').strip(); link=e.findtext('link','').strip(); pub=e.findtext('pubDate','')
            if not title or not link:continue
            try: date=email.utils.parsedate_to_datetime(pub).astimezone(now.tzinfo).strftime('%Y-%m-%d')
            except Exception: date=''
            items.append(dict(company=name,title=title,url=link,published=date))
    except Exception as exc: print(f'WARNING {name}: {exc}')
items=list({(x['company'],x['url']):x for x in items}.values())
items.sort(key=lambda x:x['published'],reverse=True)
old=[]
try:
    with open('jobs.json',encoding='utf8') as f: old=json.load(f).get('jobs',[])
except (FileNotFoundError,ValueError): pass
previous={x['url'] for x in old}
new=[x for x in items if x['url'] not in previous]
with open('jobs.json','w',encoding='utf8') as f: json.dump({'updated':now.strftime('%Y-%m-%d %H:%M KST'),'jobs':items},f,ensure_ascii=False,indent=2)
print(f'{len(items)} search results; {len(new)} new results')
if new and all(os.getenv(k) for k in ['SMTP_HOST','SMTP_USER','SMTP_PASSWORD','ALERT_TO']):
    msg=EmailMessage();msg['Subject']=f'[Bio Career Tracker] 새 채용 관련 검색 결과 {len(new)}건';msg['From']=os.environ['SMTP_USER'];msg['To']=os.environ['ALERT_TO']
    msg.set_content('채용 진행 여부 및 지원자격은 원문에서 확인하세요.\n\n'+'\n\n'.join(f"{x['company']} | {x['title']}\n{x['url']}" for x in new[:30]))
    with smtplib.SMTP_SSL(os.environ['SMTP_HOST'],int(os.getenv('SMTP_PORT','465'))) as server:
        server.login(os.environ['SMTP_USER'],os.environ['SMTP_PASSWORD']);server.send_message(msg)
