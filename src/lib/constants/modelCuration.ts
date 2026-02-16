export const CURATED_MODELS_BY_CATEGORY: Record<string, string[]> = {
	coding: ['gpt-5-codex', 'gpt-5.1-codex', 'cognitia_llm_zerogpu.mistral-7b'],
	creative: ['gpt-4o', 'gpt-4.1', 'cognitia_llm_zerogpu.qwen2.5-7b'],
	analysis: ['o3', 'o1', 'gpt-5'],
	fast: [
		'gpt-4o-mini',
		'gpt-5-mini',
		'cognitia_llm_zerogpu.phi3',
		'cognitia_llm_zerogpu.smollm2-1.7b'
	],
	local: [
		'phi3:latest',
		'cognitia_llm_zerogpu.phi3',
		'cognitia_llm_zerogpu.qwen2.5-7b',
		'cognitia_llm_zerogpu.smollm2-1.7b',
		'cognitia_llm_zerogpu.mistral-7b'
	],
	vision: ['gpt-4o', 'gpt-4o-mini'],
	documents: ['gpt-4.1', 'gpt-5'],
	general: ['gpt-4o', 'gpt-5-mini', 'cognitia_llm_zerogpu.qwen2.5-7b'],
	specials: [
		'gpt-audio-mini',
		'gpt-realtime-mini',
		'gpt-image-1',
		'omni-moderation-latest',
		'gpt-4o-search-preview'
	]
};
