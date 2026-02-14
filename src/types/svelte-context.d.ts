import type { I18nStore } from '$lib/i18n';

declare module 'svelte' {
	function getContext(key: 'i18n'): I18nStore;
}
