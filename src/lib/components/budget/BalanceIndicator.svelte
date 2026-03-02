<script lang="ts">
	import { getContext } from 'svelte';
	import { userBudget } from '$lib/stores';

	const i18n = getContext('i18n');

	$: budget = $userBudget;
	$: percentRemaining = budget ? budget.percent_remaining : 100;
	$: isWarning = budget && percentRemaining <= 20 && percentRemaining > 0;
	$: isExhausted = budget && budget.current_balance <= 0;
</script>

{#if budget}
	<div
		class="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
			{isExhausted
			? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
			: isWarning
				? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
				: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}"
	>
		{#if isExhausted}
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="size-3">
				<path
					fill-rule="evenodd"
					d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14ZM8 4a.75.75 0 0 1 .75.75v3a.75.75 0 0 1-1.5 0v-3A.75.75 0 0 1 8 4Zm0 8a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"
					clip-rule="evenodd"
				/>
			</svg>
			<span>{$i18n.t('Budget exhausted')}</span>
		{:else if isWarning}
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="size-3">
				<path
					fill-rule="evenodd"
					d="M6.701 2.25c.577-1 2.02-1 2.598 0l5.196 9a1.5 1.5 0 0 1-1.299 2.25H2.804a1.5 1.5 0 0 1-1.3-2.25l5.197-9ZM8 5a.75.75 0 0 1 .75.75v2a.75.75 0 0 1-1.5 0v-2A.75.75 0 0 1 8 5Zm0 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"
					clip-rule="evenodd"
				/>
			</svg>
			<span>${budget.current_balance.toFixed(2)} {$i18n.t('left')}</span>
		{:else}
			<span>${budget.current_balance.toFixed(2)} {$i18n.t('left')}</span>
		{/if}
	</div>
{/if}
