import { describe, it, expect } from 'vitest';

import { getPricingModels, refreshPricingModels } from './index';

describe('pricing api client', () => {
	it('exports getPricingModels', () => {
		expect(typeof getPricingModels).toBe('function');
	});

	it('exports refreshPricingModels', () => {
		expect(typeof refreshPricingModels).toBe('function');
	});
});
