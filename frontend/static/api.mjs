export function buildRequest(profile) {
  const interests = String(profile.interests || '').trim();
  if (!interests) throw new Error('Tell us what you would like to explore.');
  const labels = {tech_ml: 'Tech / ML', quant_finance: 'Quant finance', phd_research: 'PhD / research'};
  const goal = labels[profile.goal] || labels.tech_ml;
  const background = String(profile.background || '').trim();
  const completed = String(profile.completed || '').split(',').map(x => x.trim()).filter(Boolean);
  return {query: [`Interests: ${interests}`, `Career goal: ${goal}`, background && `Background: ${background}`, completed.length && `Completed courses: ${completed.join(', ')}`].filter(Boolean).join('\n'), top_k: 5};
}

export function safeSourceUrl(value) {
  try { const url = new URL(value); return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password ? url.href : null; }
  catch { return null; }
}

export function normalizeResponse(data) {
  if (!data || !Array.isArray(data.results)) throw new Error('The search service returned an unexpected response. Please try again.');
  const text = value => typeof value === 'string' ? value : '';
  const results = data.results.map(row => {
    if (!row || typeof row.course_id !== 'string' || !row.course_id.trim() || typeof row.title !== 'string' || !row.title.trim()) throw new Error('A course result is missing its ID or title. Please try again.');
    return {course_id: row.course_id, title: row.title, term: text(row.term), context: text(row.context), description: text(row.description), retrieved_at: text(row.retrieved_at),
      source_urls: (Array.isArray(row.source_urls) ? row.source_urls : []).map(safeSourceUrl).filter(Boolean),
      missing_or_uncertain_fields: (Array.isArray(row.missing_or_uncertain_fields) ? row.missing_or_uncertain_fields : []).filter(x => typeof x === 'string')};
  });
  return {results, dataset_version: text(data.dataset_version)};
}

export async function searchCourses(payload, {fetchImpl = globalThis.fetch, timeoutMs = 15000} = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl('/search', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload), signal:controller.signal});
    if (!response.ok) {
      const problem = await response.json().catch(() => ({}));
      if (problem.code === 'SEARCH_NOT_CONFIGURED') throw new Error('Live course search is not connected yet. Use “Try a sample search” to explore the interface.');
      throw new Error(`Search is unavailable (HTTP ${response.status}). Please try again shortly.`);
    }
    return normalizeResponse(await response.json());
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Search took too long. Please try again.');
    if (error instanceof TypeError) throw new Error('Could not reach the search service. Check your connection and try again.');
    if (error instanceof SyntaxError) throw new Error('The search service returned unreadable data. Please try again.');
    throw error;
  } finally {clearTimeout(timeout);}
}
