const fs=require('node:fs'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync('public/data/index.json','utf8'));
const allowed=['Open vs. Closed Models','AI Adoption & Workloads','AI Pricing & Profitability','Compute Supply & Demand','Custom Silicon & ASICs','Cloud Capex & Financial Health','Infrastructure Capacity & Constraints'];
for(const s of data){if(s.beliefs.length)assert(s.categories.length>=1&&s.categories.length<=2);else assert.equal(s.categories.length,0);assert.equal(new Set(s.categories).size,s.categories.length);assert(s.categories.every(c=>allowed.includes(c)));const detail=JSON.parse(fs.readFileSync('public/data/stories/'+s.slug+'.json','utf8'));assert.deepEqual(detail.categories,s.categories);}
for(const [fragment,expected] of [['Moonshot AI Releases Weights','Open vs. Closed Models'],['Tinker Slashes','AI Pricing & Profitability'],['Microsoft Scales Back Rented','Compute Supply & Demand']]){const s=data.find(s=>s.title.includes(fragment));assert.equal(s.categories[0],expected,fragment);}
console.log('PASS: seven permitted categories; one primary and at most one secondary on every relevant story; detail/index agreement; release, pricing and lease examples.');

const oracle=data.find(s=>s.title.includes('Microsoft Scales Back Rented'));assert(oracle.categories.includes('Compute Supply & Demand'));assert(oracle.categories.includes('Cloud Capex & Financial Health'));console.log('PASS: Oracle cloud capacity has both compute and financing tags.');
