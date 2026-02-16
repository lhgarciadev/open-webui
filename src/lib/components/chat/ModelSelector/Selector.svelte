<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { marked } from 'marked';
	import Fuse from 'fuse.js';

	import dayjs from '$lib/dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import Spinner from '$lib/components/common/Spinner.svelte';
	import { flyAndScale } from '$lib/utils/transitions';
	import { createEventDispatcher, onMount, getContext, tick } from 'svelte';
	import { goto } from '$app/navigation';

	import { deleteModel, getOllamaVersion, pullModel, unloadModel } from '$lib/apis/ollama';

	import {
		user,
		MODEL_DOWNLOAD_POOL,
		models,
		mobile,
		temporaryChatEnabled,
		settings,
		config,
		type Model
	} from '$lib/stores';
	import { toast } from 'svelte-sonner';
	import { capitalizeFirstLetter, sanitizeResponseContent, splitStream } from '$lib/utils';
	import { getModels } from '$lib/apis';
	import { getPricingModels, refreshPricingModels } from '$lib/apis/pricing';

	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Check from '$lib/components/icons/Check.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import ChatBubbleOval from '$lib/components/icons/ChatBubbleOval.svelte';

	import ModelItem from './ModelItem.svelte';

	// Model grouping imports
	import { MODEL_CATEGORIES, getCategoryById } from '$lib/constants/modelCategories';
	import { CURATED_MODELS_BY_CATEGORY } from '$lib/constants/modelCuration';
	import { groupModelsByCategory, categorizeModel } from '$lib/utils/modelUtils';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let id = '';
	export let value = '';
	export let placeholder = $i18n.t('Select a model');
	export let searchEnabled = true;
	export let searchPlaceholder = $i18n.t('Search a model');

	export let items: {
		label: string;
		value: string;
		model: Model;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		[key: string]: any;
	}[] = [];

	export let className = 'w-[32rem]';
	export let triggerClassName = 'text-lg';

	export let pinModelHandler: (modelId: string) => void = () => {};

	let show = false;

	let selectedModel = '';
	$: selectedModel = items.find((item) => item.value === value) ?? '';

	let searchValue = '';

	let selectedCategoryFilter = ''; // Category pill filter

	let showAllModels = false;
	let pricingLoading = false;
	let pricingMap: Record<string, { input_usd_per_million?: number; output_usd_per_million?: number }> = {};
	let lastRefreshAt = 0;

	const curatedModelIds = new Set<string>(Object.values(CURATED_MODELS_BY_CATEGORY).flat());

	const getItemId = (item: any): string => item?.value ?? item?.id ?? item?.model?.id ?? '';

	const isCognitiaLocalModelId = (modelId: string) => modelId.startsWith('cognitia_llm_');

	const isSpecialItem = (item: any) => {
		const model = item?.model ?? item;
		return categorizeModel(model).categories.includes('specials');
	};

	const loadPricing = async () => {
		if (pricingLoading) return;
		pricingLoading = true;
		try {
			const res = await getPricingModels(localStorage.token);
			const map: Record<string, { input_usd_per_million?: number; output_usd_per_million?: number }> =
				{};
			for (const row of res?.items ?? []) {
				if (row?.model_id) {
					map[row.model_id] = row;
				}
			}
			pricingMap = map;
		} catch (error) {
			console.debug('Failed to load pricing', error);
		} finally {
			pricingLoading = false;
		}
	};

	const refreshMissingPricing = async (modelIds: string[]) => {
		if (!modelIds.length) return;
		const now = Date.now();
		if (now - lastRefreshAt < 2000) return;
		lastRefreshAt = now;

		try {
			await refreshPricingModels(localStorage.token, modelIds);
			await loadPricing();
		} catch (error) {
			console.debug('Failed to refresh pricing', error);
		}
	};

	// Category grouping state
	let expandedCategories: Set<string> = new Set(['favorites', 'coding', 'fast']); // Default expanded
	let groupedView = true; // Toggle between grouped and flat view

	$: categoryPills = MODEL_CATEGORIES.filter(
		(c) => c.id !== 'favorites' && c.id !== 'general' && (showAllModels || c.id !== 'specials')
	);

	$: if (!showAllModels && selectedCategoryFilter === 'specials') {
		selectedCategoryFilter = '';
	}

	$: applyCuration = !showAllModels && !searchValue;

	let ollamaVersion = null;
	let selectedModelIdx = 0;

	// Get pinned models from settings
	$: pinnedModels = $settings?.pinnedModels ?? [];

	// Group filtered items by category when not searching
	$: groupedItems = !searchValue && groupedView
		? groupModelsByCategory(filteredItems, pinnedModels)
		: null;

	// Toggle category expansion
	function toggleCategory(categoryId: string) {
		if (expandedCategories.has(categoryId)) {
			expandedCategories.delete(categoryId);
		} else {
			expandedCategories.add(categoryId);
		}
		expandedCategories = expandedCategories; // Trigger reactivity

		// Save to localStorage
		try {
			localStorage.setItem('model-selector-expanded', JSON.stringify([...expandedCategories]));
		} catch (e) {
			// Ignore localStorage errors
		}
	}

	// Load expanded categories from localStorage
	function loadExpandedCategories() {
		try {
			const saved = localStorage.getItem('model-selector-expanded');
			if (saved) {
				expandedCategories = new Set(JSON.parse(saved));
			}
		} catch (e) {
			// Use defaults
		}
	}

	const fuse = new Fuse(
		items.map((item) => {
			const _item = {
				...item,
				modelName: item.model?.name,
				tags: (item.model?.tags ?? []).map((tag) => tag.name).join(' '),
				desc: item.model?.info?.meta?.description
			};
			return _item;
		}),
		{
			keys: ['value', 'tags', 'modelName'],
			threshold: 0.4
		}
	);

	const updateFuse = () => {
		if (fuse) {
			fuse.setCollection(
				items.map((item) => {
					const _item = {
						...item,
						modelName: item.model?.name,
						tags: (item.model?.tags ?? []).map((tag) => tag.name).join(' '),
						desc: item.model?.info?.meta?.description
					};
					return _item;
				})
			);
		}
	};

	$: if (items) {
		updateFuse();
	}

	// Category filter function - made reactive by referencing selectedCategoryFilter directly
	const filterByCategory = (item: any, categoryFilter: string, pinned: string[]) => {
		if (categoryFilter === '') return true;

		// Special case for favorites
		if (categoryFilter === 'favorites') {
			const modelValue = item.value ?? item.id;
			return pinned.includes(modelValue);
		}

		// Check model categories
		const cats = categorizeModel(item.model ?? item);
		return cats.categories.includes(categoryFilter);
	};

	$: filteredItems = (
		searchValue
			? fuse
					.search(searchValue)
					.map((e) => e.item)
			: items.filter((item) => filterByCategory(item, selectedCategoryFilter, pinnedModels))
	)
		.filter((item) => !(item.model?.info?.meta?.hidden ?? false))
		.filter((item) => {
			if (!applyCuration) return true;
			const itemId = getItemId(item);
			if (!curatedModelIds.has(itemId)) return false;
			if (isSpecialItem(item)) return false;
			return true;
		});

	$: if (show && filteredItems.length > 0) {
		const missing = filteredItems
			.map((item) => getItemId(item))
			.filter((id) => id && !pricingMap[id]);
		if (missing.length) {
			refreshMissingPricing(missing);
		}
	}

	$: if (selectedCategoryFilter) {
		resetView();
	}

	const resetView = async () => {
		await tick();

		const selectedInFiltered = filteredItems.findIndex((item) => item.value === value);

		if (selectedInFiltered >= 0) {
			// The selected model is visible in the current filter
			selectedModelIdx = selectedInFiltered;
		} else {
			// The selected model is not visible, default to first item in filtered list
			selectedModelIdx = 0;
		}

		// Set the virtual scroll position so the selected item is rendered and centered
		const targetScrollTop = Math.max(0, selectedModelIdx * ITEM_HEIGHT - 128 + ITEM_HEIGHT / 2);
		listScrollTop = targetScrollTop;

		await tick();

		if (listContainer) {
			listContainer.scrollTop = targetScrollTop;
		}

		await tick();
		const item = document.querySelector(`[data-arrow-selected="true"]`);
		item?.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
	};

	const pullModelHandler = async () => {
		const sanitizedModelTag = searchValue.trim().replace(/^ollama\s+(run|pull)\s+/, '');

		console.log($MODEL_DOWNLOAD_POOL);
		if ($MODEL_DOWNLOAD_POOL[sanitizedModelTag]) {
			toast.error(
				$i18n.t(`Model '{{modelTag}}' is already in queue for downloading.`, {
					modelTag: sanitizedModelTag
				})
			);
			return;
		}
		if (Object.keys($MODEL_DOWNLOAD_POOL).length === 3) {
			toast.error(
				$i18n.t('Maximum of 3 models can be downloaded simultaneously. Please try again later.')
			);
			return;
		}

		const [res, controller] = await pullModel(localStorage.token, sanitizedModelTag, '0').catch(
			(error) => {
				toast.error(`${error}`);
				return null;
			}
		);

		if (res) {
			const reader = res.body
				.pipeThrough(new TextDecoderStream())
				.pipeThrough(splitStream('\n'))
				.getReader();

			MODEL_DOWNLOAD_POOL.set({
				...$MODEL_DOWNLOAD_POOL,
				[sanitizedModelTag]: {
					...$MODEL_DOWNLOAD_POOL[sanitizedModelTag],
					abortController: controller,
					reader,
					done: false
				}
			});

			while (true) {
				try {
					const { value, done } = await reader.read();
					if (done) break;

					let lines = value.split('\n');

					for (const line of lines) {
						if (line !== '') {
							let data = JSON.parse(line);
							console.log(data);
							if (data.error) {
								throw data.error;
							}
							if (data.detail) {
								throw data.detail;
							}

							if (data.status) {
								if (data.digest) {
									let downloadProgress = 0;
									if (data.completed) {
										downloadProgress = Math.round((data.completed / data.total) * 1000) / 10;
									} else {
										downloadProgress = 100;
									}

									MODEL_DOWNLOAD_POOL.set({
										...$MODEL_DOWNLOAD_POOL,
										[sanitizedModelTag]: {
											...$MODEL_DOWNLOAD_POOL[sanitizedModelTag],
											pullProgress: downloadProgress,
											digest: data.digest
										}
									});
								} else {
									toast.success(data.status);

									MODEL_DOWNLOAD_POOL.set({
										...$MODEL_DOWNLOAD_POOL,
										[sanitizedModelTag]: {
											...$MODEL_DOWNLOAD_POOL[sanitizedModelTag],
											done: data.status === 'success'
										}
									});
								}
							}
						}
					}
				} catch (error) {
					console.log(error);
					if (typeof error !== 'string') {
						error = error.message;
					}

					toast.error(`${error}`);
					// opts.callback({ success: false, error, modelName: opts.modelName });
					break;
				}
			}

			if ($MODEL_DOWNLOAD_POOL[sanitizedModelTag].done) {
				toast.success(
					$i18n.t(`Model '{{modelName}}' has been successfully downloaded.`, {
						modelName: sanitizedModelTag
					})
				);

				models.set(
					await getModels(
						localStorage.token,
						$config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
					)
				);
			} else {
				toast.error($i18n.t('Download canceled'));
			}

			delete $MODEL_DOWNLOAD_POOL[sanitizedModelTag];

			MODEL_DOWNLOAD_POOL.set({
				...$MODEL_DOWNLOAD_POOL
			});
		}
	};

	const setOllamaVersion = async () => {
		ollamaVersion = await getOllamaVersion(localStorage.token).catch((error) => false);
	};

	onMount(async () => {
		// Load expanded categories from localStorage
		loadExpandedCategories();
	});

	$: if (show) {
		setOllamaVersion();
	}

	const cancelModelPullHandler = async (model: string) => {
		const { reader, abortController } = $MODEL_DOWNLOAD_POOL[model];
		if (abortController) {
			abortController.abort();
		}
		if (reader) {
			await reader.cancel();
			delete $MODEL_DOWNLOAD_POOL[model];
			MODEL_DOWNLOAD_POOL.set({
				...$MODEL_DOWNLOAD_POOL
			});
			await deleteModel(localStorage.token, model);
			toast.success($i18n.t('{{model}} download has been canceled', { model: model }));
		}
	};

	const unloadModelHandler = async (model: string) => {
		const res = await unloadModel(localStorage.token, model).catch((error) => {
			toast.error($i18n.t('Error unloading model: {{error}}', { error }));
		});

		if (res) {
			toast.success($i18n.t('Model unloaded successfully'));
			models.set(
				await getModels(
					localStorage.token,
					$config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
				)
			);
		}
	};

	const ITEM_HEIGHT = 42;
	const OVERSCAN = 10;

	let listScrollTop = 0;
	let listContainer;

	$: visibleStart = Math.max(0, Math.floor(listScrollTop / ITEM_HEIGHT) - OVERSCAN);
	$: visibleEnd = Math.min(
		filteredItems.length,
		Math.ceil((listScrollTop + 256) / ITEM_HEIGHT) + OVERSCAN
	);
</script>

<DropdownMenu.Root
	bind:open={show}
	onOpenChange={async () => {
		searchValue = '';
		listScrollTop = 0;
		window.setTimeout(() => document.getElementById('model-search-input')?.focus(), 0);

		resetView();
		if (show) {
			await loadPricing();
		}
	}}
	closeFocus={false}
>
	<DropdownMenu.Trigger
		class="relative w-full {($settings?.highContrastMode ?? false)
			? ''
			: 'outline-hidden focus:outline-hidden'}"
		aria-label={placeholder}
		id="model-selector-{id}-button"
	>
		<div
			class="flex w-full text-left px-3 py-1.5 rounded-full bg-gray-100/50 dark:bg-gray-900/30 hover:bg-gray-200/50 dark:hover:bg-gray-800/50 transition truncate {triggerClassName} justify-between {($settings?.highContrastMode ??
			false)
				? 'dark:placeholder-gray-100 placeholder-gray-800'
				: 'placeholder-gray-400'}"
			on:mouseenter={async () => {
				models.set(
					await getModels(
						localStorage.token,
						$config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
					)
				);
			}}
		>
			{#if selectedModel}
				{selectedModel.label}
			{:else}
				{placeholder}
			{/if}
			<ChevronDown className=" self-center ml-2 size-3" strokeWidth="2.5" />
		</div>
	</DropdownMenu.Trigger>

	<DropdownMenu.Content
		class=" z-40 {$mobile
			? `w-full`
			: `${className}`} max-w-[calc(100vw-1rem)] justify-start rounded-3xl  bg-white dark:bg-gray-850 dark:text-white shadow-xl outline-hidden border border-gray-100 dark:border-gray-800"
		transition={flyAndScale}
		side={$mobile ? 'bottom' : 'bottom-start'}
		sideOffset={2}
		alignOffset={-1}
	>
		<slot>
			{#if searchEnabled}
				<div class="flex items-center gap-2.5 px-4.5 mt-3.5 mb-1.5">
					<Search className="size-4" strokeWidth="2.5" />

					<input
						id="model-search-input"
						bind:value={searchValue}
						class="w-full text-sm bg-transparent outline-hidden"
						placeholder={searchPlaceholder}
						autocomplete="off"
						aria-label={$i18n.t('Search In Models')}
						on:keydown={(e) => {
							if (e.code === 'Enter' && filteredItems.length > 0) {
								value = filteredItems[selectedModelIdx].value;
								show = false;
								return; // dont need to scroll on selection
							} else if (e.code === 'ArrowDown') {
								e.stopPropagation();
								selectedModelIdx = Math.min(selectedModelIdx + 1, filteredItems.length - 1);
							} else if (e.code === 'ArrowUp') {
								e.stopPropagation();
								selectedModelIdx = Math.max(selectedModelIdx - 1, 0);
							} else {
								// if the user types something, reset to the top selection.
								selectedModelIdx = 0;
							}

							const item = document.querySelector(`[data-arrow-selected="true"]`);
							item?.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
						}}
					/>
				</div>
			{/if}

			<div class="px-4.5 text-[11px] text-gray-500 dark:text-gray-400">
				{$i18n.t('Pricing note')}
			</div>

			<!-- Category filter pills -->
			<div class="px-2">
				{#if items.filter((item) => !(item.model?.info?.meta?.hidden ?? false)).length > 0 && !searchValue}
					<div
						class="flex w-full bg-white dark:bg-gray-850 overflow-x-auto scrollbar-none font-[450] mb-1"
						on:wheel={(e) => {
							if (e.deltaY !== 0) {
								e.preventDefault();
								e.currentTarget.scrollLeft += e.deltaY;
							}
						}}
					>
						<div class="flex flex-wrap gap-1 w-full text-center text-xs rounded-full bg-transparent px-1.5">
							<button
								class="min-w-fit outline-none px-2 py-1 rounded-lg transition text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
								on:click={() => {
									showAllModels = !showAllModels;
								}}
							>
								{showAllModels ? $i18n.t('Show recommended') : $i18n.t('Show all')}
							</button>
							<!-- All button -->
							<button
								class="min-w-fit outline-none px-2 py-1 rounded-lg transition flex items-center gap-1 {selectedCategoryFilter === ''
									? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
									: 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}"
								aria-pressed={selectedCategoryFilter === ''}
								on:click={() => {
									selectedCategoryFilter = '';
								}}
							>
								{$i18n.t('All')}
								<span class="text-[10px] opacity-70">{items.filter((item) => !(item.model?.info?.meta?.hidden ?? false)).length}</span>
							</button>

							<!-- Favorites (if pinned models exist) -->
							{#if pinnedModels.length > 0}
								<button
									class="min-w-fit outline-none px-2 py-1 rounded-lg transition flex items-center gap-1 {selectedCategoryFilter === 'favorites'
										? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
										: 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}"
									aria-pressed={selectedCategoryFilter === 'favorites'}
									on:click={() => {
										selectedCategoryFilter = 'favorites';
									}}
								>
									⭐ {$i18n.t('Favorites')}
									<span class="text-[10px] opacity-70">{pinnedModels.length}</span>
								</button>
							{/if}

							<!-- Category pills -->
							{#each categoryPills as category}
								{@const categoryModels = items.filter(item => {
									const cats = categorizeModel(item.model ?? item);
									return cats.categories.includes(category.id);
								})}
								{#if categoryModels.length > 0}
									<Tooltip content={category.description}>
										<button
											class="min-w-fit outline-none px-2 py-1 rounded-lg transition flex items-center gap-1 {selectedCategoryFilter === category.id
												? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
												: 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}"
											aria-pressed={selectedCategoryFilter === category.id}
											on:click={() => {
												selectedCategoryFilter = category.id;
											}}
										>
											{category.emoji} {category.name.split(' ')[0]}
											<span class="text-[10px] opacity-70">{categoryModels.length}</span>
										</button>
									</Tooltip>
								{/if}
							{/each}
						</div>
					</div>
				{/if}
			</div>


			<div class="px-2.5 group relative">
				{#if filteredItems.length === 0}
					<div class="">
						<div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
							{$i18n.t('No results found')}
						</div>
					</div>
				{:else if groupedItems && !searchValue && selectedCategoryFilter === ''}
					<!-- Grouped view: Show categories with collapsible sections -->
					<div
						class="max-h-64 overflow-y-auto"
						bind:this={listContainer}
						on:scroll={() => {
							listScrollTop = listContainer.scrollTop;
						}}
					>
						{#each [...groupedItems.entries()] as [categoryId, categoryModels], catIdx}
							{@const category = getCategoryById(categoryId)}
							{#if category && categoryModels.length > 0}
								<!-- Category Header -->
								<button
									class="flex w-full items-center gap-2 px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
									on:click|stopPropagation={() => toggleCategory(categoryId)}
								>
									<span class="flex items-center gap-1.5">
										<span>{category.emoji}</span>
										<span class="uppercase tracking-wide">{category.name}</span>
									</span>
									<span class="text-gray-400 dark:text-gray-500">({categoryModels.length})</span>
									<span class="ml-auto transition-transform {expandedCategories.has(categoryId) ? 'rotate-180' : ''}">
										<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="size-3">
											<path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
										</svg>
									</span>
								</button>

								<!-- Category Models (collapsible) -->
								{#if expandedCategories.has(categoryId)}
									<div class="pl-1">
										{#each categoryModels as item, i (item.value)}
											{@const globalIndex = filteredItems.findIndex(fi => fi.value === item.value)}
											<ModelItem
												selectedModelIdx={selectedModelIdx}
												{item}
												index={globalIndex}
												{value}
												pricing={pricingMap[item.value]}
												{pinModelHandler}
												{unloadModelHandler}
												showBadges={true}
												onClick={() => {
													value = item.value;
													selectedModelIdx = globalIndex;
													show = false;
												}}
											/>
										{/each}
									</div>
								{/if}
							{/if}
						{/each}
					</div>
				{:else}
					<!-- Flat view: Virtual scrolling list (during search or category filter) -->
					<!-- svelte-ignore a11y-no-static-element-interactions -->
					<div
						class="max-h-64 overflow-y-auto"
						bind:this={listContainer}
						on:scroll={() => {
							listScrollTop = listContainer.scrollTop;
						}}
					>
						<div style="height: {visibleStart * ITEM_HEIGHT}px;" />
						{#each filteredItems.slice(visibleStart, visibleEnd) as item, i (item.value)}
							{@const index = visibleStart + i}
							<ModelItem
								{selectedModelIdx}
								{item}
								{index}
								{value}
								pricing={pricingMap[item.value]}
								{pinModelHandler}
								{unloadModelHandler}
								showBadges={true}
								onClick={() => {
									value = item.value;
									selectedModelIdx = index;

									show = false;
								}}
							/>
						{/each}
						<div style="height: {(filteredItems.length - visibleEnd) * ITEM_HEIGHT}px;" />
					</div>
				{/if}

				{#if !(searchValue.trim() in $MODEL_DOWNLOAD_POOL) && searchValue && ollamaVersion && $user?.role === 'admin'}
					<Tooltip
						content={$i18n.t(`Pull "{{searchValue}}" from Ollama.com`, {
							searchValue: searchValue
						})}
						placement="top-start"
					>
						<button
							class="flex w-full font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-hidden transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl cursor-pointer data-highlighted:bg-muted"
							on:click={() => {
								pullModelHandler();
							}}
						>
							<div class=" truncate">
								{$i18n.t(`Pull "{{searchValue}}" from Ollama.com`, { searchValue: searchValue })}
							</div>
						</button>
					</Tooltip>
				{/if}

				{#each Object.keys($MODEL_DOWNLOAD_POOL) as model}
					<div
						class="flex w-full justify-between font-medium select-none rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-hidden transition-all duration-75 rounded-xl cursor-pointer data-highlighted:bg-muted"
					>
						<div class="flex">
							<div class="mr-2.5 translate-y-0.5">
								<Spinner />
							</div>

							<div class="flex flex-col self-start">
								<div class="flex gap-1">
									<div class="line-clamp-1">
										Downloading "{model}"
									</div>

									<div class="shrink-0">
										{'pullProgress' in $MODEL_DOWNLOAD_POOL[model]
											? `(${$MODEL_DOWNLOAD_POOL[model].pullProgress}%)`
											: ''}
									</div>
								</div>

								{#if 'digest' in $MODEL_DOWNLOAD_POOL[model] && $MODEL_DOWNLOAD_POOL[model].digest}
									<div class="-mt-1 h-fit text-[0.7rem] dark:text-gray-500 line-clamp-1">
										{$MODEL_DOWNLOAD_POOL[model].digest}
									</div>
								{/if}
							</div>
						</div>

						<div class="mr-2 ml-1 translate-y-0.5">
							<Tooltip content={$i18n.t('Cancel')}>
								<button
									class="text-gray-800 dark:text-gray-100"
									on:click={() => {
										cancelModelPullHandler(model);
									}}
								>
									<svg
										class="w-4 h-4 text-gray-800 dark:text-white"
										aria-hidden="true"
										xmlns="http://www.w3.org/2000/svg"
										width="24"
										height="24"
										fill="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke="currentColor"
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M6 18 17.94 6M18 18 6.06 6"
										/>
									</svg>
								</button>
							</Tooltip>
						</div>
					</div>
				{/each}
			</div>

			<div class="mb-2.5"></div>

			<div class="hidden w-[42rem]" />
			<div class="hidden w-[32rem]" />
		</slot>
	</DropdownMenu.Content>
</DropdownMenu.Root>
