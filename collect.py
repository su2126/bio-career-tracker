"""Conservative official job-posting collector. No Google News or fabricated openings.
Only emit an item when a direct official posting URL, a recruitment-like title,
and a dated application period are present in the same local HTML element.
Unsupported/blocked sites are reported, never treated as having zero openings.
"""
import datetime as dt
import hashlib
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KST = dt.timezone(dt.timedelta(hours=9))
NOW = dt.datetime.now(KST)
DATE = re.compile(r'20\d{2}[.\-/]\d{1,2}[.\-/]\d{1,2}')
KEYWORDS = re.compile(r'채용|모집|신입|경력|인턴|QC|QA|품질|연구|생산|공정|분석')
# These are the ONLY sources for which direct job-link extraction is attempted.
# A page that cannot be parsed is reported as unsupported, not silently guessed.
SOURCES = [
    ('대웅제약', 'https://career.daewoong.co.kr/apply/posting', 'career.daewoong.co.kr'),
    ('GC녹십자', 'https://recruit.gccorp.com/kor/recruit/list', 'recruit.gccorp.com'),
]

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(); self.depth=0; self.active=None; self.items=[]
    def handle_starttag(self, tag, attrs):
        self.depth+=1
        if tag=='a' and self.active is None:
            self.active={'href':dict(attrs).get('href',''),'text':[],'depth':self.depth}
    def handle_data(self, data):
        if self.active:self.active['text'].append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.active and self.active['depth']==self.depth:
            self.active['text']=' '.join(' '.join(self.active['text']).split())
            self.items.append(self.active);self.active=None
        self.depth=max(0,self.depth-1)

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; BioCareerTracker/2.0; official-job-list-monitor)'})
    with urllib.request.urlopen(req,timeout=18) as response:
        charset=response.headers.get_content_charset() or 'utf-8'
        return response.read(2_000_000).decode(charset,errors='replace')

def parse(company,page,domain,html):
    parser=Anchors();parser.feed(html)
    found=[]
    for item in parser.items:
        title=item['text']; href=item['href']; link=urllib.parse.urljoin(page,href)
        parts=urllib.parse.urlparse(link)
        # Require a link to an individual posting, not just the list page.
        path=(parts.path+'?'+parts.query).lower()
        individual=bool(re.search(r'(posting|recruit|notice|job|apply).*(detail|view|no=|id=|idx=|seq=|drno=)',path))
        if not (parts.scheme=='https' and parts.hostname==domain and individual):continue
        if not (8<=len(title)<=170 and KEYWORDS.search(title)):continue
        # Do not assume an application period or open status from ambiguous markup.
        # Extract a period only if explicitly in the anchor text.
        dates=DATE.findall(title)
        if len(dates)<2:continue
        period=' ~ '.join(dates[:2]); id=hashlib.sha256(link.encode()).hexdigest()[:20]
        found.append({'id':id,'company':company,'title':title,'url':link,'period':period,'source':'공식 채용공고','first_seen':NOW.date().isoformat()})
    return list({x['id']:x for x in found}.values())

def main():
    prior={}
    try:prior={x['id']:x for x in json.loads((ROOT/'jobs.json').read_text())['jobs'] if 'id' in x}
    except (OSError,ValueError,KeyError):pass
    companies=json.loads((ROOT/'companies.json').read_text())
    statuses=[]; gathered=[]
    for company,url,domain in SOURCES:
        try:
            page=fetch(url); items=parse(company,url,domain,page)
            statuses.append({'company':company,'url':url,'status':'ok' if items else 'unsupported','count':len(items),'note':'개별 공고 제목·기간·직접 링크 확인' if items else '공식 목록 접근 가능하나 개별 공고의 기간/링크를 안전하게 추출하지 못함'})
            gathered+=items
        except Exception as ex:
            statuses.append({'company':company,'url':url,'status':'error','count':0,'note':type(ex).__name__})
    checked={s['company'] for s in statuses}
    for c in companies:
        if c['name'] not in checked:
            statuses.append({'company':c['name'],'url':c.get('recruit_url') or c.get('url'),'status':'not_configured','count':0,'note':'자동 수집 미지원 · 공식 링크에서 직접 확인 필요'})
    # Preserve previously confirmed items for temporary errors; do not falsely label old data current.
    by_id=dict(prior)
    for x in gathered:
        if x['id'] in prior:x['first_seen']=prior[x['id']].get('first_seen',x['first_seen'])
        by_id[x['id']]=x
    jobs=list(by_id.values());jobs.sort(key=lambda x:x.get('first_seen',''),reverse=True)
    for x in jobs:
        try:x['is_new']=0 <= (NOW.date()-dt.date.fromisoformat(x['first_seen'])).days <= 2
        except (ValueError,KeyError):x['is_new']=False
    output={'updated':NOW.strftime('%Y-%m-%d %H:%M KST'),'mode':'official-only','sources':statuses,'jobs':jobs[:200], 'note':'공식 개별 공고 확인된 항목만 표시; 일부 기업은 수집 미지원'}
    (ROOT/'jobs.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('official postings:',len(gathered),'sources:',statuses)
if __name__=='__main__':main()
