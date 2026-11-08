"""Prepare public-source news snapshot. Never reads the API .env or keys."""
import csv
import json
import re
from collections import Counter
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from review_news import review_story

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'huggingnews/data/stories.json'
OUT=ROOT/'public/data'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'stories').mkdir(exist_ok=True)

def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
def has(pattern,text):return bool(re.search(pattern,text,re.I))

aliases={
 'OpenAI':[r'\bopenai\b',r'\bchatgpt\b',r'\bcodex\b'],
 'Anthropic':[r'\banthropic\b',r'\bclaude\b'],
 'xAI':[r'\bxai\b',r'\bgrok\b',r'\bspacexai\b'],
 'Mistral AI':[r'\bmistral\b'],
 'Microsoft':[r'\bmicrosoft\b',r'\bazure\b'],
 'Amazon / AWS':[r'\bamazon\b',r'\baws\b',r'\btrainium\b'],
 'Google':[r'\bgoogle\b',r'\balphabet\b',r'\bgemini\b'],
 'Oracle':[r'\boracle\b'], 'Meta':[r'\bmeta\b',r'\bllama\b'],
 'CoreWeave':[r'\bcoreweave\b'], 'Nebius':[r'\bnebius\b'], 'Nscale':[r'\bnscale\b'],
 'NVIDIA':[r'\bnvidia\b',r'\bblackwell\b',r'\bh100\b',r'\ba100\b',r'\bb200\b'],
 'AMD':[r'\bamd\b',r'\bepyc\b',r'\binstinct\b'],
 'Broadcom':[r'\bbroadcom\b'], 'MediaTek':[r'\bmediatek\b'], 'Marvell':[r'\bmarvell\b'],
 'TSMC':[r'\btsmc\b'], 'Intel':[r'\bintel\b'], 'SoftBank':[r'\bsoftbank\b'],
 'Cerebras':[r'\bcerebras\b'], 'Groq':[r'\bgroq\b'], 'Qualcomm':[r'\bqualcomm\b'],
 'Humain':[r'\bhumain\b'], 'Anysphere':[r'\banysphere\b',r'\bcursor\b'],
 'Harvey':[r'\bharvey\b'], 'Ambience':[r'\bambience\b'], 'Figure AI':[r'\bfigure ai\b']}

def model_access(s):
 title=s['title'];summary=s['summary']
 if has(r'open.source.*(?:engine|code|kernel|framework|router)|(?:engine|kernel|router).*open.source',title):
  return {'status':'not_established','evidence':'Open software is not evidence of model weight availability.'}
 subject=re.split(r'\b(?:versus|vs\.?|beats|outperforms|rivals|trails|tops|while|whereas|compared|as)\b',title,maxsplit=1,flags=re.I)[0]
 if has(r'nano banana|\bgemini\b|\bchatgpt\b|\bgpt[- ]?\d|\bclaude\b|\bopus\b',subject):
  return {'status':'not_established','evidence':'The subject is a hosted-model product; this record does not establish an open-weight release. Comparators and distribution platforms do not determine access.'}
 if has(r'leak|plans to|will release|to release|not yet|before.*release',title):
  return {'status':'not_established','evidence':'The headline describes a leak or planned release; public weight availability is not established.'}
 explicit=r'open[ -]weights?|open[ -]models?|open[ -]source(?:\s+\w+){0,2}\s+models?|(?:opens|releases|publishes)\s+(?:the\s+)?weights'
 if has(explicit,subject):
  return {'status':'open_reported','evidence':'The headline explicitly describes open models or released weights. Verify the exact version and license; open weights is not automatically an open-source license.'}
 family=r'(?:kimi|deepseek|qwen|glm[- ]?\d|llama|gemma|mistral)'
 openness=r'(?:open[ -]weight|open[ -]source|weights (?:are )?available|released weights)'
 if has(family,subject) and (has(family+r'.{0,100}'+openness,summary) or has(openness+r'.{0,100}'+family,summary)):
  return {'status':'open_reported','evidence':'The article links the subject model family to an open-model/weight-availability claim. Exact version and license still need verification.'}
 return {'status':'not_established','evidence':'No subject-level open-weight release claim was identified. OpenRouter availability or an open-model comparison is insufficient.'}

def pricing_context(s):
 text=s['title']+'\n'+s['summary']+'\n'+'\n'.join(t['text'] for t in s['selectedTweets'])
 if has(r'price|pricing',s['title']) and has(r'efficien',text) and has(r'tinker|baseten|together|fireworks',s['title']):
  return {'kind':'service_efficiency','basis':'The report attributes service pricing changes to efficiency. This does not establish model-publisher revenue pressure.','comparison':'Separate platform repricing from Flash-versus-base model prices; the latter is not a same-model historical price cut.'}
 return None

def classify(s):
 title=s['title'];text=title+'\n'+s['summary'];result=[]
 def add(cid,reason):result.append({'id':cid,'reason':reason})
 if model_access(s)['status']=='open_reported' and has(r'model|tokens|inference|weights|benchmark|intelligence|\b(?:kimi|qwen|deepseek|gemma|llama)\b',title):
  add('C1','Open-model capability, adoption or serving demand appears in the report.')
 infra=has(r'coreweave|nebius|oracle|softbank|hyperscaler|data cent[er]{2}|ai infrastructure|ai.*debt|gpu|cloud',text)
 if (infra and has(r'credit risk|credit insurance|\bcds\b|debt|free cash flow|financing|capex|capital expenditures|funding shortage|bond yield',title)) or has(r'ai bubble|ai.*price.*(fall|drop)|llm.*price.*(fall|drop)',title):
  add('C2','Infrastructure payback, funding or AI price pressure is the reported signal.')
 frontier=has(r'openai|anthropic|claude|chatgpt|gemini|gpt[- ]|frontier|token|tinker|inference|baseten',text)
 if frontier and has(r'price|pricing|costs?|token (use|usage|volume)|tokens per|enterprise revenue|usage limits|usage caps|business.*adoption|api.*revenue',title) and not has(r'stock|shares|ipo price|credit insurance|credit risk|embedding|\bimage\b|\bvideo\b',title):
  add('C3','Token pricing, usage or frontier-model economics is described; price and volume must be separated.')
 if has(r'gpu|h100|a100|b200|b300|rtx 3090|nvidia',text) and has(r'rental|leasing|leaseback|depreciation|residual value|older.gpu|older.generation',title) and not has(r'restrictions|export|policy',title):
  add('C4','GPU rental, older-hardware economics or useful life is the reported signal.')
 if has(r'custom (ai )?(chip|silicon|accelerator)|\basi[cs]\b|\basics\b|\btpus?\b|trainium|mediatek|broadcom|marvell|jalape',title):
  add('C5','Custom silicon or an ASIC supply-chain participant is central to the report.')
 if has(r'\bcpu\b|\bcpus\b|\bepyc\b|vera processors|server processors',title) and has(r'agent|ai|server|data center|cloud|inference',text):
  add('C6','Server CPU capacity or CPU intensity is linked to AI workloads.')
 if has(r'\boracle\b',title) and has(r'lease|rent|capacity|cash|revenue|financ|fundrais|capital|debt|credit|stargate|gpu|chip|gas|pipeline',text):
  add('C7','Oracle revenue, compute commitments or financing exposure is described.')
 if has(r'\bmodel\b|\bmodels\b|\b(?:gemini|gpt|claude)[ -]?\d',title) and has(r'releas|launch|debut|new.{0,35}model|model.{0,30}(benchmark|score)|gemini.{0,25}matches',title) and not has(r'robot|protein|weather|image|video|audio|voice|embedding|detector|security flaws|warned|lawsuit|leak|filter blocks',title):
  add('release','Model capability or release: compare prior versions and adoption before assessing compute demand.')
 if not any(x['id']=='release' for x in result) and (has(r'nano banana',title) or (has(r'kimi|deepseek|qwen|gemma|llama|gemini',title) and has(r'inference|tokens per|speed|benchmark|model',title))):
  add('release','Model capability, pricing or serving context; no open-weight status or hardware supplier is assumed.')
 if has(r'cowos|advanced packaging|interposer|substrate|amkor|optical.engine|silicon photonics',title):
  add('packaging','Advanced-packaging capacity, pricing or complementary components may affect shipment conversion and margins.')
 if has(r'\bhbm\w*\b|memory shortage|memory supply|dram shortage|memory costs',title):
  add('memory','Memory availability or cost can constrain system completion or add logic-base-die demand.')
 if has(r'data cent(er|re)|ai site|ai campus',title) and has(r'power|gas|grid|halts|ban|restrictions|delays|permit|construction',title):
  add('deployment','Power, permitting or construction can change hardware deployment timing.')
 if has(r'export|sanctions|trade restrictions|chip.*(ban|restrictions)|restrict.*(chip|gpu)|restricted.*(nvidia|gpu)',title) and has(r'ai|chip|gpu|nvidia|semiconductor',title):
  add('access','Market access and export rules may affect eligible demand and regional manufacturing mix.')
 if has(r'tsmc|samsung.*(foundry|2nm)|intel.*(18a|14a)|foundry orders|terafab',title):
  add('foundry','Foundry allocation, node execution or regional ramp economics may affect TSMC share, volume or margins.')
 return result

CATEGORY_NAMES=['Open vs. Closed Models','AI Adoption & Workloads','AI Pricing & Profitability','Compute Supply & Demand','Custom Silicon & ASICs','Cloud Capex & Financial Health','Infrastructure Capacity & Constraints']
def category_tags(s,matches):
 # Subject-led routing: headline signals outrank incidental entities in summaries.
 title=s['title'];scores={name:0 for name in CATEGORY_NAMES}
 rules=[
  (0,r'model|weights|gemini|claude|gpt|glm|kimi|qwen|deepseek|llama|gemma|nano banana',3),
  (1,r'adoption|users|usage|workloads|enterprise use|token.*(surge|grow)|agents',4),
  (2,r'prices?|pricing|costs?|profit|margins?|monetiz|cheaper',6),
  (3,r'gpu|nvidia|h100|h200|a100|b200|b300|blackwell|rubin|instinct|accelerator|\bcpus?\b|\btpus?\b|trainium|\basics?\b|compute|computing|processing capacity|server processors|epyc|vera processors|ai chips?|cloud capacity|serverless.*training|training.*platform',4),
  (4,r'\btpus?\b|trainium|asic|custom.*(chip|silicon|accelerator)|broadcom|marvell|mediatek',7),
  (5,r'capex|financ|fundrais|funding|debt|credit|\bcds\b|cash flow|bonds?|investment|revenue|\bleases?\b|\brented\b',6),
  (6,r'power|grid|permit|data cent|campus|\bhbm|memory|network|cowos|packaging|foundry|fab\b|tsmc|wafer|2nm|3nm|yield|export|sanction',5)]
 for i,pattern,weight in rules:
  if has(pattern,title):scores[CATEGORY_NAMES[i]]+=weight
 ids=[m['id'] for m in matches]
 fallback={'C1':0,'release':0,'C2':5,'C3':2,'C4':3,'C5':4,'C6':6,'C7':5,'packaging':6,'memory':6,'deployment':6,'access':6,'foundry':6}
 for cid in ids:
  if cid in fallback:scores[CATEGORY_NAMES[fallback[cid]]]+=1
 ranked=sorted(CATEGORY_NAMES,key=lambda n:-scores[n])
 # Unrelated archive entries need not be admitted to the TSMC feed.
 if not ids:return []
 tags=[ranked[0]]
 if scores[ranked[1]]>=4:tags.append(ranked[1])
 # Compute is cross-cutting: financing, custom silicon and capacity stories can
 # carry it alongside the primary topic even when another secondary scores higher.
 compute=CATEGORY_NAMES[3]
 if scores[compute]>=4 and compute not in tags:tags=tags[:1]+[compute]
 return tags

stories=json.loads(SOURCE.read_text());index=[];counts=Counter()

management_focus={
 'C1':'Incremental NVIDIA GPU orders, generation mix and TSMC manufacturing capture',
 'C2':'Investment payback, customer funding and order cancellation risk',
 'C3':'Realized revenue, compute per task and procurement appetite',
 'C4':'Older-fleet utilization, useful life and new-order conversion',
 'C5':'GPU versus ASIC mix, foundry allocation and package content',
 'C6':'Server-CPU demand and verified fabrication route',
 'C7':'Customer concentration, cash generation and counterparty exposure',
 'release':'Model adoption, prior-version trajectory and training/inference capacity',
 'packaging':'CoWoS bottlenecks, realized ASP, package mix and shipment conversion',
 'memory':'HBM qualification, system completion and logic-base-die demand',
 'deployment':'Energization dates, site substitution and hardware delivery schedules',
 'access':'Accessible markets, compliance and regional order mix',
 'foundry':'Process qualification, customer allocation, ramp costs and margins'}

def primary_lens(matches,title):
 ids=[x['id'] for x in matches]
 for key in ['C7','packaging','memory','deployment','access','foundry']:
  if key in ids:return key
 if 'release' in ids:
  return 'C1' if 'C1' in ids else 'release'
 for key in ['C4','C6','C5','C3','C2','C1']:
  if key in ids:return key
 return None

def outlook_for(lens,title):
 if lens in ['C1','release']:return 'mixed' if has(r'efficien|speed|faster|throughput|cost|huawei|leak|to build|plans|tool|framework|engine',title) else 'up'
 if lens=='C7':return 'up' if has(r'completes.*fundrais|revenue.*(grow|rise)|new.*funding',title) else 'down' if has(r'scale.*back|scrap|cancel|credit|debt risk',title) else 'mixed'
 if lens=='C2':return 'up' if has(r'agrees to back|secures.*financing|completes.*fundrais',title) else 'down' if has(r'credit.*(risk|cost)|distress|selloff|shortage|gap|pull.*back',title) else 'mixed'
 if lens=='C3':return 'down' if has(r'price.*(drop|cut)|cuts?.*(cost|price)|lower.*(cost|price)|caps?|usage limits',title) else 'up' if has(r'revenue.*tops|token.*(grow|increase|surge)',title) else 'mixed'
 if lens=='C4':return 'up' if has(r'rental.*(high|rise|increase)|raises?.*price|price.*(rise|increase)',title) else 'mixed'
 if lens=='C6':return 'mixed' if has(r'cut|reduc',title) else 'up'
 if lens=='deployment':return 'mixed' if has(r'opposing.*bans|pause|pledge|propos',title) else 'down' if has(r'halts|ban|restrict|delay|cost',title) else 'up' if has(r'construction.*growth|power.*secured',title) else 'mixed'
 if lens=='memory':return 'down' if has(r'defer|shortage|strike|pause',title) else 'mixed'
 if lens=='packaging':return 'up' if has(r'price hike|expands|signs',title) else 'mixed'
 return 'mixed'

for s in stories:
 slug=s['slug']; assert re.fullmatch(r'[\w-]+',slug)
 matches=classify(s);counts.update(x['id'] for x in matches)
 dt=datetime.fromisoformat(s['publishedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Taipei'))
 week=(dt.date()-timedelta(days=dt.weekday())).isoformat()
 entities=[name for name,patterns in aliases.items() if any(has(p,s['title']+' '+s['summary']) for p in patterns)]
 for t in s['selectedTweets']:
  quote=t['bestBit'];original=t['text']+'\n'+t.get('quotedTweetText','')
  if quote in original:t['displayQuote']=quote;t['quoteOrigin']='Source excerpt'
  else:
   raw=t['text'];end=raw.rfind(' ',0,280) if len(raw)>280 else len(raw)
   t['displayQuote']=raw[:end] if end>0 else raw[:280];t['quoteOrigin']='Post text';t['quoteTruncated']=len(raw)>end
 lens=primary_lens(matches,s['title'])
 s['pricingContext']=pricing_context(s)
 s['primaryLens']=primary_lens(matches,s['title'])
 s['review']=review_story(s,matches)
 if s['review']['included'] and not matches:matches=[{'id':'compute','reason':s['review']['reason']}];counts.update(['compute'])
 s['categories']=s['review']['categories']
 if s['review']['profile']=='indirect':s['review']['caveats'].append('Low direct TSMC relevance; retained as context rather than a procurement signal.')
 s['beliefs']=matches;s['companies']=entities;s['week']=week
 lens=primary_lens(matches,s['title']) or ('compute' if matches else None)
 s['modelAccess']=model_access(s)
 s['pricingContext']=pricing_context(s)
 s['primaryLens']=lens;s['outlook']=outlook_for(lens,s['title']);s['managementFocus']=management_focus.get(lens,'Review hardware demand and manufacturing exposure')
 if s['pricingContext']:s['outlook']='mixed';s['managementFocus']='Service cost savings versus workload growth; distinguish service-provider margins from model-publisher economics'
 # Same-entity or same-model earlier coverage is context, not proof of an identical version.
 model_terms=[m for m in ['gemini','kimi','deepseek','qwen','claude','gpt','llama','mistral','trainium','cowos','hbm','oracle'] if has(r'\b'+m,s['title'])]
 previous=[]
 for old in stories:
  if old['slug']==slug or old['publishedAt']>=s['publishedAt']:continue
  score=sum(3 for term in model_terms if has(r'\b'+term,old['title']))
  if not score:continue
  previous.append((score,old['publishedAt'],old['slug']))
 s['historySlugs']=[x[2] for x in sorted(previous,reverse=True)[:3]]
 s['counterpoints']=[]
 if any(x['id']=='C1' for x in matches) and has(r'huawei hardware|huawei.{0,30}chips|ascend',s['title']):
  s['counterpoints'].append({'text':'This record names Huawei/Ascend hardware. The proposed NVIDIA demand pathway is not established by this report.','basis':'Hardware-route limitation identified from the headline','sourceIds':[]})
 if 'microsoft-scales-back-rented-ai-cloud' in slug:
  s['counterpoints']=[{'text':'Oracle maintains that demand for its AI services remains strong and stated in September that some 4 year old GPU contracts were renewed at a 20% premium.','basis':'Counterpoint reported in the article summary','sourceIds':['2118760114131710144']}]
 dump(OUT/'stories'/f'{slug}.json',s)
 index.append({k:s[k] for k in ['slug','title','publishedAt','eventTimeApprox','tweetCount','authorCount','beliefs','companies','week','primaryLens','outlook','managementFocus','historySlugs','modelAccess','pricingContext','categories','review'] }|{'excerpt':(s['summary'][:240].rsplit(' ',1)[0]+'…' if len(s['summary'])>240 else s['summary']),'sourceCount':len(s['selectedTweets'])})

with open(ROOT.parent/'references/data/ai_relationships.csv',encoding='utf-8-sig',newline='') as f:rels=list(csv.DictReader(f))
with open(ROOT.parent/'references/data/ai_relationship_events.csv',encoding='utf-8-sig',newline='') as f:events=list(csv.DictReader(f))
nodes={};edges=[]
for r in rels:
 for side in ['from','to']:
  name=r[side+'_company'];nodes[name]={'id':name,'ticker':r[side+'_ticker'],'segment':r[side+'_segment']}
 grouped={}
 for e in events:
  if e['relationship_id']!=r['relationship_id']:continue
  key=e['event_seq']
  if key not in grouped:grouped[key]={'date':e['event_date'],'precision':e['date_precision'],'status':e['event_status'],'value':e['event_value'],'detail':e['event_detail'],'sources':[]}
  grouped[key]['sources'].append({'title':e['source_title'],'url':e['source_url'],'type':e['source_type']})
 edges.append({'id':r['relationship_id'],'from':r['from_company'],'to':r['to_company'],'category':r['category'],'status':r['status'],'value':r['headline_value'],'bn':float(r['value_usd_bn_approx'] or 0),'summary':r['summary'],'dealType':r['deal_type'],'via':r['via'],'first':r['first_event_date'],'latest':r['latest_event_date'],'events':[grouped[k] for k in sorted(grouped,key=int)],'origin':'Provided relationship CSV'})
# Add only this well-attributed reported lease relation, with source provenance.
root=next(s for s in stories if 'microsoft-scales-back-rented-ai-cloud' in s['slug'])
edges.append({'id':'msft-orcl-news','from':'Microsoft','to':'Oracle','category':'Service','status':'REPORTED · WINDING DOWN','value':'Selected AI capacity leases','bn':0,'summary':root['summary'].split('\n')[0],'dealType':'Compute lease','via':'Reported news; original agreement amount not supplied','first':root['eventTimeApprox'][:10],'latest':root['eventTimeApprox'][:10],'origin':'Added from HuggingNews · reported, not in CSV','events':[{'date':root['eventTimeApprox'][:10],'precision':'approx','status':'REPORTED','value':'Partial non-renewal','detail':root['summary'],'sources':[{'title':'@'+t['authorHandle'],'url':t['url'],'type':t['role']} for t in root['selectedTweets'][:2]]}]})
dump(OUT/'index.json',index)
dump(OUT/'graph.json',{'nodes':list(nodes.values()),'edges':edges})
dump(OUT/'manifest.json',{'snapshotDate':'2026-11-08','requestedStart':'2026-06-01','requestedEnd':'2026-11-08','earliest':min(s['publishedAt'] for s in stories),'latest':max(s['publishedAt'] for s in stories),'storyCount':len(stories),'matchedCount':sum(bool(s['beliefs']) for s in index),'selectedSourceCount':sum(len(s['selectedTweets']) for s in stories),'beliefCounts':dict(counts),'historyComplete':False,'classification':'Rule-based relevance selection across model, demand, supply and manufacturing topics. Story signals and scenario paths are proposed analysis, not verified causality.','relationCount':len(rels),'newsEdges':1,'companyCount':len(nodes)})
print(json.dumps({'stories':len(index),'matched':sum(bool(s['beliefs']) for s in index),'beliefCounts':dict(counts),'graphEdges':len(edges),'nodes':len(nodes)}))
