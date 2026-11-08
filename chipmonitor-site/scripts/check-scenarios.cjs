const fs=require('node:fs'),assert=require('node:assert/strict'),ts=require('typescript'),path=require('node:path');
const cache={};
function load(name){const file=path.resolve('lib',name+'.ts');if(cache[file])return cache[file].exports;const mod={exports:{}};cache[file]=mod;const code=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;new Function('require','module','exports',code)(p=>load(p.replace('./','')),mod,mod.exports);return mod.exports;}
const {storyScenarios}=load('management');
const data=JSON.parse(fs.readFileSync('public/data/index.json','utf8'));
const find=fragment=>{const s=data.find(s=>s.title.includes(fragment));assert(s,fragment);return s;};
const oracle=find('Microsoft Scales Back Rented');assert.equal(storyScenarios(oracle,[]).length,3);assert.equal(storyScenarios(oracle,[])[1].name,'Credit → connected projects');
const kimi=find('SGLang Speeds Kimi');assert.equal(kimi.primaryLens,'release');assert.equal(kimi.modelAccess.status,'not_established');assert(storyScenarios(kimi,[])[0].bridge.includes('NVIDIA'));assert(storyScenarios(kimi,[])[0].bridge.includes('TSMC'));assert(!storyScenarios(kimi,[]).some(b=>/stronger open models/i.test(b.inference)));
const nano=find("Nano Banana 2.1 Takes");assert(!nano.beliefs.some(b=>b.id==='C1'));assert.equal(nano.primaryLens,'release');assert.equal(nano.modelAccess.status,'not_established');assert(storyScenarios(nano,[]).every(b=>!/stronger open models/.test(b.inference)));assert(storyScenarios(nano,[]).some(b=>b.name==='Image-price pressure'));
const open=find('Moonshot AI Releases Weights');assert.equal(open.modelAccess.status,'open_reported');assert(storyScenarios(open,[])[0].bridge.includes('NVIDIA'));
const gemini=find('Gemini 4 Carbon Matches');assert.equal(gemini.primaryLens,'release');const prior=(gemini.historySlugs||[]).map(id=>data.find(s=>s.slug===id));assert(prior.length);assert(storyScenarios(gemini,prior)[0].check.includes(prior[0].title));assert(storyScenarios(gemini,prior)[0].bridge.includes('Google'));
const packaging=find('TSMC Plans Up to 20%');assert.equal(packaging.primaryLens,'packaging');assert.deepEqual(storyScenarios(packaging,[]).map(b=>b.direction),['up','down']);
const memory=find('SK Hynix Defers');assert.equal(memory.primaryLens,'memory');
for(const s of data){for(const id of s.historySlugs||[]){const old=data.find(o=>o.slug===id);assert(old&&old.publishedAt<s.publishedAt,'History must be earlier than root');}if(s.beliefs.length)assert(storyScenarios(s,[]).length>=2);}
const dashboard=fs.readFileSync('components/chipmonitor/dashboard.tsx','utf8');assert(!dashboard.includes('className="belief-statement"'));assert(!dashboard.includes('className="analysis-kicker"'));assert(!dashboard.includes('className="branch-selector"'));
console.log('PASS: Oracle has three distinct paths; open-model path names NVIDIA/TSMC and reported GPU; Gemini uses earlier coverage; packaging has opposing branches; all history predates its story; old framing removed.');

const tinker=find('Tinker Slashes');assert.equal(tinker.outlook,'mixed');const paths=storyScenarios(tinker,[]);assert.equal(paths.length,3);assert.deepEqual(paths.map(b=>b.direction),['up','mixed','down']);assert(paths[0].bridge.includes('NVIDIA'));assert(paths[2].check.includes('Flash versus base-model'));assert(paths[2].inference.includes('does not establish lower GLM publisher revenue'));console.log('PASS: service efficiency pricing separates adoption, compute savings and conditional service-provider margins.');
