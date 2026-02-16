import { describe, it, expect } from 'vitest';
import { categorizeModel } from './modelUtils';

describe('modelUtils', () => {
	it('treats cognitia models as local', () => {
		const result = categorizeModel({ id: 'cognitia_llm_zerogpu.phi3' });
		expect(result.categories).toContain('local');
	});

	it('flags audio models as specials', () => {
		const result = categorizeModel({ id: 'gpt-audio-mini' });
		expect(result.categories).toContain('specials');
	});
});
