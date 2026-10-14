import test from 'node:test';
import assert from 'node:assert/strict';
import {buildRequest, normalizeResponse, safeSourceUrl, searchCourses} from '../static/api.mjs';
test('profile is represented in the query',()=>{
  assert.deepEqual(buildRequest({interests:'  ML  ',background:'Python',completed:' AC209, , CS181 ',goal:'phd_research'}),{query:'Interests: ML\nCareer goal: PhD / research\nBackground: Python\nCompleted courses: AC209, CS181',top_k:5});
  assert.throws(()=>buildRequest({interests:'   '}),/explore/);
});
test('unsafe and credential-bearing source links are rejected',()=>{
  for(const url of ['javascript:alert(1)','data:text/html,x','/relative','https://user:secret@example.com']) assert.equal(safeSourceUrl(url),null);
  assert.equal(safeSourceUrl('https://example.com/course'),'https://example.com/course');
});
test('response keeps unknown metadata absent and filters unsafe sources',()=>{
  const result=normalizeResponse({results:[{course_id:'1',title:'Course',source_urls:['javascript:alert(1)','https://example.com'],missing_or_uncertain_fields:['term',3]}]});
  assert.equal(result.dataset_version,''); assert.equal(result.results[0].term,'');
  assert.deepEqual(result.results[0].source_urls,['https://example.com/']);
  assert.deepEqual(result.results[0].missing_or_uncertain_fields,['term']);
  assert.throws(()=>normalizeResponse({courses:[]}),/unexpected/);
  assert.throws(()=>normalizeResponse({results:[{title:'No ID'}]}),/missing/);
});
test('search posts the contract and accepts zero results',async()=>{
  const data=await searchCourses({query:'ML',top_k:5},{fetchImpl:async(url,options)=>{
    assert.equal(url,'/search');assert.equal(options.method,'POST');assert.equal(options.body,'{"query":"ML","top_k":5}');
    return {ok:true,json:async()=>({results:[]})};
  }});assert.deepEqual(data.results,[]);
});
test('HTTP, network, invalid JSON, and malformed results do not return mock data',async()=>{
  await assert.rejects(searchCourses({}, {fetchImpl:async()=>({ok:false,status:503,json:async()=>({})})}),/503/);
  await assert.rejects(searchCourses({}, {fetchImpl:async()=>{throw new TypeError('fetch failed');}}),/Could not reach/);
  await assert.rejects(searchCourses({}, {fetchImpl:async()=>({ok:true,json:async()=>{throw new SyntaxError();}})}),/unreadable/);
  await assert.rejects(searchCourses({}, {fetchImpl:async()=>({ok:true,json:async()=>({})})}),/unexpected/);
});
test('slow search times out',async()=>{
  await assert.rejects(searchCourses({}, {timeoutMs:5,fetchImpl:(_url,{signal})=>new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError'))))}),/too long/);
});
test('unconfigured hosted search explains how to preview without pretending it is live',async()=>{
  await assert.rejects(searchCourses({}, {fetchImpl:async()=>({ok:false,status:503,json:async()=>({code:'SEARCH_NOT_CONFIGURED'})})}),/not connected yet/);
  await assert.rejects(searchCourses({}, {fetchImpl:async()=>({ok:false,status:502,json:async()=>{throw new SyntaxError();}})}),/502/);
});
