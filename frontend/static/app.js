import {buildRequest, normalizeResponse, searchCourses} from './api.mjs';
import {mockSearch} from './mock.mjs';
const $ = id => document.getElementById(id);
const form = $('search-form');
$('try-demo').addEventListener('click', () => {
  if ($('submit').disabled) return;
  if (!$('interests').value.trim()) $('interests').value = 'Interpretable machine learning and responsible AI';
  $('mock-mode').checked = true;
  $('scenario').value = 'success';
  form.requestSubmit();
});
function element(tag, text, className) {const node=document.createElement(tag); node.textContent=text; if(className) node.className=className; return node;}
function renderCard(course, mock) {
  const card=element('article','','course-card');
  const meta=element('div','','course-meta'); meta.append(element('span',course.course_id),element('span',course.term || 'Term not provided')); card.append(meta,element('h3',course.title));
  if(course.description) card.append(element('p',course.description));
  card.append(element('div','SUPPORTING CONTEXT','card-label'),element('blockquote',course.context || 'Supporting context was not provided by the search service.'));
  const sources=element('div','','sources');
  course.source_urls.forEach((url,i)=>{const link=element('a',mock ? `Sample link ${i+1} ↗` : `Source ${i+1} ↗`); link.href=url;link.target='_blank';link.rel='noopener noreferrer'; sources.append(link);});
  if(!course.source_urls.length) sources.append(element('p','Source link not provided.'));
  card.append(sources,element('p',`Retrieved: ${course.retrieved_at || 'Date not provided'}`,'hint'));
  if(course.missing_or_uncertain_fields.length) card.append(element('p',`Missing or uncertain: ${course.missing_or_uncertain_fields.join('; ')}`,'uncertainty'));
  return card;
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  if($('submit').disabled) return;
  $('error').hidden=true; $('results').replaceChildren(); $('provenance').textContent='';
  let payload;
  try {payload=buildRequest(Object.fromEntries(new FormData(form)));}
  catch(error){$('error').textContent=error.message;$('error').hidden=false;$('status').textContent='Update your interests to continue.';$('interests').focus();return;}
  const mock=$('mock-mode').checked, scenario=$('scenario').value;
  $('mode-label').textContent=mock ? 'Synthetic preview' : 'Live search';
  $('status').textContent=mock ? 'Loading synthetic sample results…' : 'Searching for courses…';
  $('results').setAttribute('aria-busy','true'); $('submit').disabled=true; $('try-demo').disabled=true;
  try {
    const data=mock ? normalizeResponse(await mockSearch(scenario)) : await searchCourses(payload);
    $('status').textContent=data.results.length ? `${data.results.length} ${mock ? 'synthetic sample results' : 'courses returned'}. Explore the supporting context below.` : 'No matches found. Try broader interests or different keywords.';
    $('provenance').textContent=`Dataset: ${data.dataset_version || 'Version not provided'}${mock ? ' · Interface preview only; not real retrieval.' : ''}`;
    for(const course of data.results) $('results').append(renderCard(course,mock));
    if (window.matchMedia('(max-width: 700px)').matches) $('results-title').scrollIntoView({behavior:'smooth',block:'start'});
  } catch(error){$('status').textContent='Search could not be completed.';$('error').textContent=error.message;$('error').hidden=false;}
  finally {$('results').setAttribute('aria-busy','false');$('submit').disabled=false;$('try-demo').disabled=false;}
});
