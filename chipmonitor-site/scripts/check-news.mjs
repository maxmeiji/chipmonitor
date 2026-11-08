import fs from 'node:fs';
import assert from 'node:assert/strict';
const base=new URL('../public/data/',import.meta.url);
const read=name=>JSON.parse(fs.readFileSync(new URL(name,base),'utf8'));
const items=read('index.json'),graph=read('graph.json'),manifest=read('manifest.json');
assert.equal(items.length,1587);assert.equal(new Set(items.map(s=>s.slug)).size,items.length);
assert.equal(items.filter(s=>s.beliefs.length).length,manifest.matchedCount);
const ids=new Set(graph.nodes.map(n=>n.id));assert.equal(ids.size,28);assert.equal(graph.edges.length,54);
for(const e of graph.edges){assert(ids.has(e.from)&&ids.has(e.to));assert(e.events.length);for(const event of e.events)for(const s of event.sources)assert(/^https:\/\//.test(s.url));}
let sourceCount=0;
for(const item of items){const story=read('stories/'+item.slug+'.json');assert(story.summary);assert.equal(story.selectedTweets.length,item.sourceCount);sourceCount+=story.selectedTweets.length;for(const t of story.selectedTweets){assert(t.displayQuote.length);assert((t.text+'\n'+(t.quotedTweetText||'')).includes(t.displayQuote));assert(/^https:\/\//.test(t.url));}}
assert.equal(sourceCount,5880);
const oracle=graph.edges.find(e=>e.id==='msft-orcl-news');assert(oracle.origin.includes('not in CSV'));assert(oracle.events[0].sources.length>0);
assert(graph.edges.some(e=>e.from==='Oracle'&&e.to==='AMD'));assert(graph.edges.some(e=>e.from==='AMD'&&e.to==='TSMC'));
assert(!fs.existsSync(new URL('../.env',import.meta.url)));
console.log(`PASS: ${items.length} unique news records; ${manifest.matchedCount} belief candidates; ${sourceCount} literal source excerpts; 28 companies; 54 sourced graph links.`);
