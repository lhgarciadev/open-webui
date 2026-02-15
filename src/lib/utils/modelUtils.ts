/**
 * Model Utility Functions for Cognitia
 * Categorization, capability detection, and grouping utilities
 */

import {
	MODEL_CATEGORIES,
	MODEL_NAME_PATTERNS,
	type ModelCategory,
	type ModelCapabilities
} from '$lib/constants/modelCategories';

export interface CategorizedModel {
	categories: string[];
	capabilities: ModelCapabilities;
	primaryCategory: string;
}

/**
 * Categorize a model based on its properties and name heuristics
 */
export function categorizeModel(model: any): CategorizedModel {
	const categories: string[] = [];
	const capabilities: ModelCapabilities = {};
	const modelId = (model?.id ?? model?.value ?? '').toLowerCase();
	const modelName = (model?.name ?? model?.label ?? '').toLowerCase();
	const ownedBy = (model?.owned_by ?? '').toLowerCase();
	const connectionType = model?.connection_type ?? '';

	// Check if model is local (Ollama)
	if (ownedBy === 'ollama' || connectionType === 'local') {
		categories.push('local');
		capabilities.priceTier = 'free';
	}

	// Check model name patterns for categories
	for (const [categoryId, patterns] of Object.entries(MODEL_NAME_PATTERNS)) {
		for (const pattern of patterns) {
			if (modelId.includes(pattern) || modelName.includes(pattern)) {
				if (!categories.includes(categoryId)) {
					categories.push(categoryId);
				}
				break;
			}
		}
	}

	// Detect capabilities from model metadata
	const meta = model?.info?.meta ?? {};
	const params = model?.info?.params ?? {};

	// Context window detection
	capabilities.contextWindow = detectContextWindow(model);

	// Vision support
	if (
		meta.capabilities?.vision ||
		modelId.includes('vision') ||
		modelId.includes('gpt-4o') ||
		modelId.includes('claude-3') ||
		modelId.includes('gemini') ||
		modelId.includes('llava')
	) {
		capabilities.supportsVision = true;
		if (!categories.includes('vision')) {
			categories.push('vision');
		}
	}

	// Tools support
	if (
		meta.capabilities?.tools ||
		modelId.includes('gpt-4') ||
		modelId.includes('claude') ||
		modelId.includes('gemini')
	) {
		capabilities.supportsTools = true;
	}

	// Reasoning support
	if (
		meta.capabilities?.reasoning ||
		modelId.includes('o1') ||
		modelId.includes('o3') ||
		modelId.includes('qwq') ||
		modelId.includes('deepseek-r1')
	) {
		capabilities.supportsReasoning = true;
		if (!categories.includes('analysis')) {
			categories.push('analysis');
		}
	}

	// Speed tier detection
	capabilities.latencyTier = detectLatencyTier(model);

	// Price tier detection (for non-local models)
	if (!capabilities.priceTier) {
		capabilities.priceTier = detectPriceTier(model);
	}

	// Large context window implies documents category
	if (capabilities.contextWindow && capabilities.contextWindow >= 100000) {
		if (!categories.includes('documents')) {
			categories.push('documents');
		}
	}

	// Default to general if no categories matched
	if (categories.length === 0) {
		categories.push('general');
	}

	// Determine primary category (first non-general, non-local)
	const primaryCategory =
		categories.find((c) => c !== 'general' && c !== 'local') || categories[0] || 'general';

	return {
		categories,
		capabilities,
		primaryCategory
	};
}

/**
 * Detect context window size from model metadata or name
 */
function detectContextWindow(model: any): number | undefined {
	const meta = model?.info?.meta ?? {};
	const params = model?.info?.params ?? {};
	const modelId = (model?.id ?? '').toLowerCase();

	// Check explicit metadata
	if (meta.context_length) return meta.context_length;
	if (params.num_ctx) return params.num_ctx;

	// Infer from model name patterns
	if (modelId.includes('1m') || modelId.includes('gemini-1.5-pro')) return 1000000;
	if (modelId.includes('200k') || modelId.includes('claude-3')) return 200000;
	if (modelId.includes('128k') || modelId.includes('gpt-4')) return 128000;
	if (modelId.includes('32k')) return 32000;
	if (modelId.includes('16k')) return 16000;

	// Default Ollama context
	if (model?.owned_by === 'ollama') return 8192;

	return undefined;
}

/**
 * Detect latency tier based on model characteristics
 */
function detectLatencyTier(model: any): 'fast' | 'medium' | 'slow' {
	const modelId = (model?.id ?? '').toLowerCase();

	// Ultra-fast models
	if (
		modelId.includes('flash') ||
		modelId.includes('instant') ||
		modelId.includes('mini') ||
		modelId.includes('haiku') ||
		modelId.includes('nano')
	) {
		return 'fast';
	}

	// Slow models (large/reasoning)
	if (
		modelId.includes('opus') ||
		modelId.includes('o1') ||
		modelId.includes('o3') ||
		modelId.includes('pro')
	) {
		return 'slow';
	}

	return 'medium';
}

/**
 * Detect price tier based on model characteristics
 */
function detectPriceTier(model: any): 'free' | 'cheap' | 'medium' | 'premium' {
	const modelId = (model?.id ?? '').toLowerCase();

	// Free tier (local, open source, etc.)
	if (model?.owned_by === 'ollama' || model?.connection_type === 'local') {
		return 'free';
	}

	// Cheap tier
	if (
		modelId.includes('mini') ||
		modelId.includes('haiku') ||
		modelId.includes('flash') ||
		modelId.includes('instant')
	) {
		return 'cheap';
	}

	// Premium tier
	if (modelId.includes('opus') || modelId.includes('o1') || modelId.includes('o3')) {
		return 'premium';
	}

	return 'medium';
}

/**
 * Group models by their primary category
 */
export function groupModelsByCategory(
	models: any[],
	pinnedModels: string[] = []
): Map<string, any[]> {
	const groups = new Map<string, any[]>();

	// Initialize all categories
	for (const category of MODEL_CATEGORIES) {
		groups.set(category.id, []);
	}

	// Group models
	for (const model of models) {
		const { primaryCategory, categories } = categorizeModel(model.model ?? model);
		const modelValue = model.value ?? model.id;

		// Check if pinned (favorites)
		if (pinnedModels.includes(modelValue)) {
			const favorites = groups.get('favorites') ?? [];
			favorites.push({ ...model, _categories: categories, _isPinned: true });
			groups.set('favorites', favorites);
		}

		// Add to primary category
		const categoryModels = groups.get(primaryCategory) ?? [];
		categoryModels.push({ ...model, _categories: categories });
		groups.set(primaryCategory, categoryModels);
	}

	// Remove empty categories and sort by priority
	const sortedGroups = new Map<string, any[]>();
	const sortedCategories = MODEL_CATEGORIES.sort((a, b) => a.priority - b.priority);

	for (const category of sortedCategories) {
		const models = groups.get(category.id) ?? [];
		if (models.length > 0) {
			sortedGroups.set(category.id, models);
		}
	}

	return sortedGroups;
}

/**
 * Get capability badges for a model
 */
export function getModelBadges(model: any): string[] {
	const badges: string[] = [];
	const { capabilities } = categorizeModel(model);

	// Context window badge
	if (capabilities.contextWindow) {
		if (capabilities.contextWindow >= 1000000) {
			badges.push('🧠 1M');
		} else if (capabilities.contextWindow >= 200000) {
			badges.push('🧠 200K');
		} else if (capabilities.contextWindow >= 128000) {
			badges.push('🧠 128K');
		} else if (capabilities.contextWindow >= 32000) {
			badges.push('🧠 32K');
		}
	}

	// Speed badge
	if (capabilities.latencyTier === 'fast') {
		badges.push('⚡');
	}

	// Price badge
	if (capabilities.priceTier === 'free') {
		badges.push('💰💰💰');
	} else if (capabilities.priceTier === 'cheap') {
		badges.push('💰💰');
	}

	// Capability badges
	if (capabilities.supportsReasoning) {
		badges.push('🤔');
	}
	if (capabilities.supportsVision) {
		badges.push('👁️');
	}
	if (capabilities.supportsTools) {
		badges.push('🔧');
	}

	// Local badge
	const connectionType = model?.connection_type ?? model?.model?.connection_type;
	const ownedBy = model?.owned_by ?? model?.model?.owned_by;
	if (connectionType === 'local' || ownedBy === 'ollama') {
		badges.push('🔒');
	}

	return badges;
}

/**
 * Get formatted context window string
 */
export function formatContextWindow(contextWindow?: number): string {
	if (!contextWindow) return '';
	if (contextWindow >= 1000000) return `${(contextWindow / 1000000).toFixed(0)}M`;
	if (contextWindow >= 1000) return `${(contextWindow / 1000).toFixed(0)}K`;
	return `${contextWindow}`;
}
