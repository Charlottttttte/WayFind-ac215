// Deliberately synthetic: never presented as Harvard catalog data or retrieval evidence.
export async function mockSearch(scenario) {
  await new Promise(resolve => setTimeout(resolve, 650));
  if (scenario === 'error') throw new Error('Simulated service error. Select another preview scenario and try again.');
  return {dataset_version:'synthetic-ui-fixture-v1', results:scenario === 'empty' ? [] : [
    {course_id:'SAMPLE-101', title:'Example: Interpretable Machine Learning', term:'Sample term', description:'Synthetic course text for testing the results interface.', context:'This sample passage illustrates how supporting context from a course description will appear.', source_urls:['https://example.com/course-101'], retrieved_at:'', missing_or_uncertain_fields:['Synthetic record; not a real course.']},
    {course_id:'SAMPLE-202', title:'Example: Responsible Data Systems', term:'', description:'Synthetic course text for checking missing metadata and source display.', context:'This sample demonstrates a second result; its order does not represent retrieval relevance.', source_urls:[], retrieved_at:'', missing_or_uncertain_fields:['term','source_urls']}
  ]};
}
