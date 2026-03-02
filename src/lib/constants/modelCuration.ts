export const CURATED_MODELS_BY_CATEGORY: Record<string, string[]> = {
	coding: [
		'gpt-5-codex',
		'gpt-5.1-codex',
		'gpt-4o',
		'anthropic/claude-sonnet-4',
		'anthropic/claude-3.5-sonnet',
		'google/gemini-2.5-pro-preview',
		'x-ai/grok-3',
		'cognitia_llm_zerogpu.mistral-7b'
	],
	creative: [
		'gpt-4o',
		'gpt-4.1',
		'anthropic/claude-opus-4',
		'anthropic/claude-3-opus',
		'anthropic/claude-sonnet-4',
		'google/gemini-2.5-pro-preview',
		'cognitia_llm_zerogpu.qwen2.5-7b'
	],
	analysis: [
		'o3',
		'o1',
		'gpt-5',
		'anthropic/claude-opus-4',
		'anthropic/claude-sonnet-4',
		'google/gemini-2.5-pro-preview',
		'x-ai/grok-3'
	],
	fast: [
		'gpt-4o-mini',
		'gpt-5-mini',
		'anthropic/claude-3.5-haiku',
		'anthropic/claude-haiku-4',
		'google/gemini-2.0-flash',
		'google/gemini-1.5-flash',
		'x-ai/grok-3-mini',
		'x-ai/grok-2-mini',
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
	vision: [
		'gpt-4o',
		'gpt-4o-mini',
		'anthropic/claude-sonnet-4',
		'anthropic/claude-3.5-sonnet',
		'google/gemini-2.0-flash',
		'google/gemini-2.5-pro-preview'
	],
	documents: [
		'gpt-4.1',
		'gpt-5',
		'anthropic/claude-opus-4',
		'anthropic/claude-sonnet-4',
		'google/gemini-1.5-pro',
		'google/gemini-2.5-pro-preview'
	],
	general: [
		'gpt-4o',
		'gpt-5-mini',
		'anthropic/claude-sonnet-4',
		'anthropic/claude-3.5-sonnet',
		'google/gemini-2.0-flash',
		'google/gemini-2.5-pro-preview',
		'x-ai/grok-3',
		'x-ai/grok-3-mini',
		'cognitia_llm_zerogpu.qwen2.5-7b'
	],
	specials: [
		'gpt-audio-mini',
		'gpt-realtime-mini',
		'gpt-image-1',
		'omni-moderation-latest',
		'gpt-4o-search-preview'
	]
};
