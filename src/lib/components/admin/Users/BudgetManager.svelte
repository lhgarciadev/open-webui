<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getAllBudgets,
		setUserBudget,
		getUserSpending,
		type AllBudgetsItem,
		type SpendingTransaction
	} from '$lib/apis/budgets';

	const i18n = getContext('i18n');

	let budgets: AllBudgetsItem[] = [];
	let total = 0;
	let loading = true;

	let editingUserId: string | null = null;
	let editForm = {
		initial_budget: 5.0,
		hard_limit: true,
		reset_balance: false
	};

	let spendingUserId: string | null = null;
	let spendingTransactions: SpendingTransaction[] = [];
	let spendingTotal = 0;
	let spendingLoading = false;

	let newBudgetUserId = '';
	let showNewBudgetForm = false;

	const loadBudgets = async () => {
		loading = true;
		try {
			const result = await getAllBudgets(localStorage.token);
			if (result) {
				budgets = result.budgets;
				total = result.total;
			}
		} catch (err) {
			toast.error(`${err}`);
		}
		loading = false;
	};

	const handleSaveBudget = async (userId: string) => {
		try {
			await setUserBudget(localStorage.token, userId, editForm);
			toast.success($i18n.t('Budget updated'));
			editingUserId = null;
			await loadBudgets();
		} catch (err) {
			toast.error(`${err}`);
		}
	};

	const handleViewSpending = async (userId: string) => {
		spendingUserId = userId;
		spendingLoading = true;
		try {
			const result = await getUserSpending(localStorage.token, userId, { limit: 50 });
			if (result) {
				spendingTransactions = result.transactions;
				spendingTotal = result.count;
			}
		} catch (err) {
			toast.error(`${err}`);
		}
		spendingLoading = false;
	};

	const handleNewBudget = async () => {
		if (!newBudgetUserId.trim()) {
			toast.error($i18n.t('Please enter a user ID'));
			return;
		}
		try {
			await setUserBudget(localStorage.token, newBudgetUserId.trim(), editForm);
			toast.success($i18n.t('Budget created'));
			showNewBudgetForm = false;
			newBudgetUserId = '';
			await loadBudgets();
		} catch (err) {
			toast.error(`${err}`);
		}
	};

	onMount(() => {
		loadBudgets();
	});
</script>

<div class="flex flex-col gap-4">
	<div class="flex items-center justify-between">
		<h3 class="text-lg font-medium">{$i18n.t('Budget Management')}</h3>
		<button
			class="px-3 py-1.5 text-sm font-medium rounded-lg bg-black text-white hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100 transition"
			on:click={() => {
				showNewBudgetForm = !showNewBudgetForm;
				editForm = { initial_budget: 5.0, hard_limit: true, reset_balance: false };
			}}
		>
			{showNewBudgetForm ? $i18n.t('Cancel') : $i18n.t('Add Budget')}
		</button>
	</div>

	{#if showNewBudgetForm}
		<div class="border dark:border-gray-700 rounded-lg p-4 space-y-3">
			<div>
				<label class="block text-sm font-medium mb-1">{$i18n.t('User ID')}</label>
				<input
					type="text"
					bind:value={newBudgetUserId}
					class="w-full px-3 py-2 border dark:border-gray-600 rounded-lg bg-transparent"
					placeholder={$i18n.t('Enter user ID')}
				/>
			</div>
			<div>
				<label class="block text-sm font-medium mb-1">{$i18n.t('Initial Budget (USD)')}</label>
				<input
					type="number"
					step="0.01"
					min="0"
					bind:value={editForm.initial_budget}
					class="w-full px-3 py-2 border dark:border-gray-600 rounded-lg bg-transparent"
				/>
			</div>
			<div class="flex items-center gap-2">
				<input type="checkbox" bind:checked={editForm.hard_limit} id="new-hard-limit" />
				<label for="new-hard-limit" class="text-sm">{$i18n.t('Hard Limit (block when exhausted)')}</label>
			</div>
			<button
				class="px-3 py-1.5 text-sm font-medium rounded-lg bg-black text-white hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100 transition"
				on:click={handleNewBudget}
			>
				{$i18n.t('Create Budget')}
			</button>
		</div>
	{/if}

	{#if loading}
		<div class="text-center py-4 text-gray-500">{$i18n.t('Loading...')}</div>
	{:else if budgets.length === 0}
		<div class="text-center py-8 text-gray-500">{$i18n.t('No budgets configured')}</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b dark:border-gray-700 text-left">
						<th class="py-2 px-3 font-medium">{$i18n.t('User')}</th>
						<th class="py-2 px-3 font-medium">{$i18n.t('Email')}</th>
						<th class="py-2 px-3 font-medium text-right">{$i18n.t('Budget')}</th>
						<th class="py-2 px-3 font-medium text-right">{$i18n.t('Balance')}</th>
						<th class="py-2 px-3 font-medium text-right">{$i18n.t('Remaining')}</th>
						<th class="py-2 px-3 font-medium text-right">{$i18n.t('Spent')}</th>
						<th class="py-2 px-3 font-medium">{$i18n.t('Actions')}</th>
					</tr>
				</thead>
				<tbody>
					{#each budgets as budget}
						<tr class="border-b dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-800/50">
							<td class="py-2 px-3">{budget.user_name}</td>
							<td class="py-2 px-3 text-gray-500">{budget.user_email}</td>
							<td class="py-2 px-3 text-right">${budget.initial_budget.toFixed(2)}</td>
							<td class="py-2 px-3 text-right">
								<span
									class={budget.current_balance <= 0
										? 'text-red-500'
										: budget.percent_remaining <= 20
											? 'text-amber-500'
											: ''}
								>
									${budget.current_balance.toFixed(2)}
								</span>
							</td>
							<td class="py-2 px-3 text-right">{budget.percent_remaining.toFixed(1)}%</td>
							<td class="py-2 px-3 text-right">${budget.total_spent_usd.toFixed(4)}</td>
							<td class="py-2 px-3">
								<div class="flex gap-1">
									<button
										class="px-2 py-1 text-xs rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition"
										on:click={() => {
											if (editingUserId === budget.user_id) {
												editingUserId = null;
											} else {
												editingUserId = budget.user_id;
												editForm = {
													initial_budget: budget.initial_budget,
													hard_limit: budget.hard_limit,
													reset_balance: false
												};
											}
										}}
									>
										{$i18n.t('Edit')}
									</button>
									<button
										class="px-2 py-1 text-xs rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition"
										on:click={() => handleViewSpending(budget.user_id)}
									>
										{$i18n.t('Spending')}
									</button>
								</div>
							</td>
						</tr>

						{#if editingUserId === budget.user_id}
							<tr>
								<td colspan="7" class="py-3 px-3">
									<div class="border dark:border-gray-700 rounded-lg p-3 space-y-3">
										<div class="grid grid-cols-2 gap-3">
											<div>
												<label class="block text-xs font-medium mb-1"
													>{$i18n.t('Initial Budget (USD)')}</label
												>
												<input
													type="number"
													step="0.01"
													min="0"
													bind:value={editForm.initial_budget}
													class="w-full px-2 py-1.5 text-sm border dark:border-gray-600 rounded bg-transparent"
												/>
											</div>
											<div class="flex flex-col gap-2 justify-center">
												<div class="flex items-center gap-2">
													<input
														type="checkbox"
														bind:checked={editForm.hard_limit}
														id="edit-hard-limit-{budget.user_id}"
													/>
													<label
														for="edit-hard-limit-{budget.user_id}"
														class="text-xs">{$i18n.t('Hard Limit')}</label
													>
												</div>
												<div class="flex items-center gap-2">
													<input
														type="checkbox"
														bind:checked={editForm.reset_balance}
														id="edit-reset-{budget.user_id}"
													/>
													<label for="edit-reset-{budget.user_id}" class="text-xs"
														>{$i18n.t('Reset Balance')}</label
													>
												</div>
											</div>
										</div>
										<div class="flex gap-2">
											<button
												class="px-3 py-1 text-xs font-medium rounded bg-black text-white hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100 transition"
												on:click={() => handleSaveBudget(budget.user_id)}
											>
												{$i18n.t('Save')}
											</button>
											<button
												class="px-3 py-1 text-xs rounded border dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
												on:click={() => {
													editingUserId = null;
												}}
											>
												{$i18n.t('Cancel')}
											</button>
										</div>
									</div>
								</td>
							</tr>
						{/if}
					{/each}
				</tbody>
			</table>
		</div>
		<div class="text-xs text-gray-500 text-right">
			{$i18n.t('Total')}: {total}
		</div>
	{/if}

	{#if spendingUserId}
		<div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
			<div
				class="bg-white dark:bg-gray-900 rounded-xl shadow-xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col"
			>
				<div class="flex items-center justify-between p-4 border-b dark:border-gray-700">
					<h3 class="font-medium">{$i18n.t('Spending History')}</h3>
					<button
						class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition"
						on:click={() => {
							spendingUserId = null;
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
							class="size-5"
						>
							<path
								d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"
							/>
						</svg>
					</button>
				</div>
				<div class="overflow-auto p-4">
					{#if spendingLoading}
						<div class="text-center py-4 text-gray-500">{$i18n.t('Loading...')}</div>
					{:else if spendingTransactions.length === 0}
						<div class="text-center py-4 text-gray-500">{$i18n.t('No transactions')}</div>
					{:else}
						<table class="w-full text-xs">
							<thead>
								<tr class="border-b dark:border-gray-700 text-left">
									<th class="py-1.5 px-2 font-medium">{$i18n.t('Date')}</th>
									<th class="py-1.5 px-2 font-medium">{$i18n.t('Model')}</th>
									<th class="py-1.5 px-2 font-medium text-right">{$i18n.t('Input')}</th>
									<th class="py-1.5 px-2 font-medium text-right">{$i18n.t('Output')}</th>
									<th class="py-1.5 px-2 font-medium text-right">{$i18n.t('Cost')}</th>
								</tr>
							</thead>
							<tbody>
								{#each spendingTransactions as tx}
									<tr class="border-b dark:border-gray-700/50">
										<td class="py-1.5 px-2 text-gray-500">
											{new Date(tx.created_at * 1000).toLocaleString()}
										</td>
										<td class="py-1.5 px-2">{tx.model_id}</td>
										<td class="py-1.5 px-2 text-right">{tx.input_tokens.toLocaleString()}</td>
										<td class="py-1.5 px-2 text-right">{tx.output_tokens.toLocaleString()}</td>
										<td class="py-1.5 px-2 text-right">${tx.total_cost_usd.toFixed(6)}</td>
									</tr>
								{/each}
							</tbody>
						</table>
						<div class="text-xs text-gray-500 text-right mt-2">
							{spendingTotal}
							{$i18n.t('transactions')}
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>
