/**
 * Model Categories for Cognitia
 * Groups models by their primary use case for easier selection
 */

export interface ModelCategory {
	id: string;
	name: string;
	emoji: string;
	description: string;
	priority: number; // Lower = higher in the list
}

export interface ModelCapabilities {
	contextWindow?: number;
	supportsVision?: boolean;
	supportsTools?: boolean;
	supportsReasoning?: boolean;
	latencyTier?: 'fast' | 'medium' | 'slow';
	priceTier?: 'free' | 'cheap' | 'medium' | 'premium';
}

/**
 * Category definitions ordered by priority
 */
export const MODEL_CATEGORIES: ModelCategory[] = [
	{
		id: 'favorites',
		name: 'Favoritos',
		emoji: '⭐',
		description: 'Modelos favoritos y fijados',
		priority: 0
	},
	{
		id: 'coding',
		name: 'Coding & Desarrollo',
		emoji: '💻',
		description: 'Generación de código, debugging, code reviews',
		priority: 1
	},
	{
		id: 'creative',
		name: 'Creativo & Escritura',
		emoji: '🎨',
		description: 'Contenido, copywriting, storytelling',
		priority: 2
	},
	{
		id: 'analysis',
		name: 'Análisis & Razonamiento',
		emoji: '📊',
		description: 'Datos, investigación, decisiones complejas',
		priority: 3
	},
	{
		id: 'fast',
		name: 'Rápidos & Económicos',
		emoji: '⚡',
		description: 'Tareas simples, respuestas rápidas, alto volumen',
		priority: 4
	},
	{
		id: 'local',
		name: 'Locales',
		emoji: '🏠',
		description: 'Modelos Ollama, privacidad total, sin conexión',
		priority: 5
	},
	{
		id: 'vision',
		name: 'Visión & Multimodal',
		emoji: '👁️',
		description: 'Análisis de imágenes, OCR, documentos visuales',
		priority: 6
	},
	{
		id: 'documents',
		name: 'Documentos Largos',
		emoji: '📄',
		description: 'RAG, análisis de PDFs extensos, contexto largo',
		priority: 7
	},
	{
		id: 'specials',
		name: 'Especiales',
		emoji: '🧩',
		description: 'Audio, realtime, imagen, moderación, search',
		priority: 8
	},
	{
		id: 'general',
		name: 'General',
		emoji: '🤖',
		description: 'Modelos de propósito general',
		priority: 99
	}
];

/**
 * Heuristics for detecting model capabilities by name patterns
 */
export const MODEL_NAME_PATTERNS = {
	coding: [
		'coder',
		'code',
		'codex',
		'copilot',
		'deepseek-coder',
		'starcoder',
		'codellama',
		'phind',
		'wizardcoder',
		'magicoder',
		'codestral',
		// Add general-purpose models that are commonly used for coding
		'gpt-4',
		'gpt-4o',
		'claude-3-5-sonnet',
		'claude-sonnet',
		'gemini-pro',
		'gemini-2'
	],
	creative: [
		'opus',
		'creative',
		'writer',
		'story',
		'novel',
		'gpt-4',
		'claude-3-opus',
		'claude-opus'
	],
	analysis: [
		'o1',
		'o3',
		'reasoning',
		'think',
		'analyst',
		'research',
		'qwen-qwq',
		'qwq',
		'deepseek-r1'
	],
	fast: [
		'mini',
		'haiku',
		'flash',
		'instant',
		'turbo',
		'small',
		'tiny',
		'nano',
		'phi-3',
		'phi-4',
		'gemma',
		'llama-3.2:1b',
		'llama-3.2:3b'
	],
	vision: [
		'vision',
		'visual',
		'image',
		'multimodal',
		'llava',
		'bakllava',
		'gpt-4o',
		'claude-3',
		'gemini'
	],
	documents: ['long', '128k', '200k', '1m', 'gemini-pro', 'claude-3']
};

/**
 * Get category by ID
 */
export function getCategoryById(id: string): ModelCategory | undefined {
	return MODEL_CATEGORIES.find((cat) => cat.id === id);
}

/**
 * Get all category IDs
 */
export function getCategoryIds(): string[] {
	return MODEL_CATEGORIES.map((cat) => cat.id);
}

/**
 * Capability badge definitions
 */
export const CAPABILITY_BADGES = {
	contextWindow: {
		'1m': { label: '🧠 1M', description: '1 million token context' },
		'200k': { label: '🧠 200K', description: '200K token context' },
		'128k': { label: '🧠 128K', description: '128K token context' },
		'32k': { label: '🧠 32K', description: '32K token context' },
		'8k': { label: '🧠 8K', description: '8K token context' }
	},
	speed: {
		fast: { label: '⚡', description: 'Alta velocidad' },
		veryFast: { label: '⚡⚡', description: 'Muy rápido' },
		ultraFast: { label: '⚡⚡⚡', description: 'Ultra rápido' }
	},
	price: {
		free: { label: '💰💰💰', description: 'Gratis' },
		cheap: { label: '💰💰', description: 'Muy económico' },
		medium: { label: '💰', description: 'Económico' }
	},
	capabilities: {
		reasoning: { label: '🤔', description: 'Soporta modo razonamiento' },
		vision: { label: '👁️', description: 'Soporta imágenes' },
		tools: { label: '🔧', description: 'Soporta tool calling' },
		local: { label: '🔒', description: 'Solo local, máxima privacidad' }
	}
};
