const fs=require('node:fs'),assert=require('node:assert/strict'),ts=require('typescript'),path=require('node:path');
const cache={};function load(name){const file=path.resolve('lib',name+'.ts');if(cache[file])return cache[file].exports;const mod={exports:{}};cache[file]=mod;new Function('require','module','exports',ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText)(p=>load(p.replace('./','')),mod,mod.exports);return mod.exports;}
const {storyScenarios}=load('management'),index=JSON.parse(fs.readFileSync('public/data/index.json','utf8'));
const matched=index.filter(s=>s.beliefs.length),picks=matched.filter(s=>s.review.shortlisted);
assert.equal(index.length,1587);assert.equal(picks.length,8);
assert(matched.some(s=>s.outlook==='up'));assert(matched.some(s=>s.outlook==='down'));
const find=x=>matched.find(s=>s.slug.startsWith(x));
assert.equal(find('revolut-cuts-ai-token').review.profile,'self_host');assert(storyScenarios(find('revolut-cuts-ai-token'),[])[0].bridge.includes('B200'));
assert.equal(find('amazon-offloads-8b').review.profile,'leaseback');assert.equal(find('meta-runs-production-inference').review.profile,'asic');assert.equal(find('transformer-lead-times').review.profile,'infrastructure');
assert.equal(find('chatandbuild-launches-shared-memory').review.profile,'software_memory');assert.equal(find('anthropic-rewrites-messages').review.profile,'cpu_efficiency');assert.equal(find('nvidia-vr200-rack').review.profile,'system_delay');
assert.equal(find('taiwan-september-exports').review.profile,'macro_exports');assert.equal(find('thinking-machines-inkling').modelAccess.status,'not_established');
let md='# ChipMonitor archive review\n\nReviewed locally on November 8, 2026 (Taipei).\n\n## Method and limits\n\nAll 1,587 archived records were screened using revised subject, economic-actor and source-aware rules. '+matched.length+' are retained as candidates; '+(index.length-matched.length)+' remain outside the current scope. This is a reproducible rules-based audit plus close reading of the eight shortlisted records, not an independent fact-check or a manual analyst review of every post. Original posts can be mistaken, promotional or incomplete. Standard scenario patterns remain where no story-specific mechanism was identified. Story direction uses the earlier preliminary positive/negative/mixed rules; branch colors show conditional scenarios. Neither is a verified outcome.\n\nSeven topic tags are independent of impact direction. Each candidate has one primary and at most one secondary category. A compute tag covers CPU/GPU/ASIC and cloud capacity. Source counts are provider-selected entries, not independent confirmations. Figures below reproduce reported claims, not verified financial data.\n\n## Analyst picks\n\n';
for(const s of picks)md+='- ['+s.title+'](http://127.0.0.1:5173/?story='+s.slug+') — '+s.categories.join(' / ')+'\n';
md+='\n## Candidate-by-candidate review\n\n';
for(const s of matched){const detail=JSON.parse(fs.readFileSync('public/data/stories/'+s.slug+'.json','utf8')),history=(s.historySlugs||[]).map(slug=>index.find(x=>x.slug===slug)),branches=storyScenarios(s,history);assert(branches.length>=2);assert(s.review);assert(s.categories.length>=1&&s.categories.length<=2);assert(['up','down','mixed'].includes(s.outlook));for(const b of branches)for(const k of ['check','inference','impact','counter'])assert(b[k]);
md+='### '+s.title+'\n\n[Open local story](http://127.0.0.1:5173/?story='+s.slug+') · '+s.publishedAt+'\n\nCategories: '+s.categories.join(' → ')+'\n\nReview mechanism: '+s.review.profile+'. '+s.review.reason+'\n\nReported summary: '+detail.summary+'\n\n';
for(const c of s.review.caveats)md+='- '+c+'\n';
md+='\nReturned post evidence / viewpoints (attributed, not verified):\n\n';
for(const t of detail.selectedTweets){const q=t.displayQuote.split(/\s+/).slice(0,22).join(' ');md+='- [@'+t.authorHandle+']('+t.url+') ('+t.role+'): “'+q+'”'+(q!==t.displayQuote?' [excerpt]':'')+'\n';}
for(const b of branches)md+='\n**'+b.name+' — conditional '+b.direction+'**\n\nCheck: '+b.check+'\n\nChain: '+b.inference+'\n\nHardware/company route: '+b.bridge+'\n\nTSMC: '+b.impact+'\n\nCountermechanism: '+b.counter+'\n';
md+='\n';}
md+='## Remaining archive: preliminary exclusions\n\nThese entries were screened out by the current rules; relevance can be revisited.\n\n';
for(const s of index.filter(s=>!s.beliefs.length))md+='- '+s.title+' — '+s.review.reason+'\n';
fs.writeFileSync('../docs/ChipMonitor_Archive_Review.md',md);
console.log('PASS: all '+index.length+' records screened; '+matched.length+' candidate chains validated; eight picks; specific regressions cover self-hosting, leaseback, TPU, power, CPU savings, software memory, rack delays, exports and comparator leakage.');
