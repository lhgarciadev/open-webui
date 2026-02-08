<script lang="ts">
	import { toast } from 'svelte-sonner';
	// @ts-ignore
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import { onMount, getContext, tick } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	const i18n = getContext('i18n');

	import { WEBUI_NAME, config, prompts, tools as _tools, user } from '$lib/stores';
	import { APP_NAME } from '$lib/constants';

	import { goto } from '$app/navigation';
	import {
		createNewTool,
		loadToolByUrl,
		deleteToolById,
		exportTools,
		getToolById,
		getToolList,
		getTools
	} from '$lib/apis/tools';
	import { capitalizeFirstLetter } from '$lib/utils';

	import Tooltip from '../common/Tooltip.svelte';
	import ConfirmDialog from '../common/ConfirmDialog.svelte';
	import ToolMenu from './Tools/ToolMenu.svelte';
	import EllipsisHorizontal from '../icons/EllipsisHorizontal.svelte';
	import ValvesModal from './common/ValvesModal.svelte';
	import ManifestModal from './common/ManifestModal.svelte';
	import Heart from '../icons/Heart.svelte';
	import DeleteConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import GarbageBin from '../icons/GarbageBin.svelte';
	import Search from '../icons/Search.svelte';
	import Plus from '../icons/Plus.svelte';
	import ChevronRight from '../icons/ChevronRight.svelte';
	import Spinner from '../common/Spinner.svelte';
	import XMark from '../icons/XMark.svelte';
	import AddToolMenu from './Tools/AddToolMenu.svelte';
	import ImportModal from '../ImportModal.svelte';
	import ViewSelector from './common/ViewSelector.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Sparkles from '$lib/components/icons/Sparkles.svelte';
	import PuzzlePiece from '$lib/components/icons/PuzzlePiece.svelte';
	import CubeTransparent from '$lib/components/icons/CubeTransparent.svelte';

	let shiftKey = false;
	let loaded = false;

	let toolsImportInputElement: HTMLInputElement;
	let importFiles;

	let showConfirm = false;
	let query = '';

	let showManifestModal = false;
	let showValvesModal = false;
	let selectedTool = null;

	let showDeleteConfirm = false;

	let tools = [];
	let filteredItems = [];

	let tagsContainerElement: HTMLDivElement;
	let viewOption = '';

	let showImportModal = false;

	$: if (tools && query !== undefined && viewOption !== undefined) {
		setFilteredItems();
	}

	const setFilteredItems = () => {
		filteredItems = tools.filter((t) => {
			if (query === '' && viewOption === '') return true;
			const lowerQuery = query.toLowerCase();
			return (
				((t.name || '').toLowerCase().includes(lowerQuery) ||
					(t.id || '').toLowerCase().includes(lowerQuery) ||
					(t.user?.name || '').toLowerCase().includes(lowerQuery) || // Search by user name
					(t.user?.email || '').toLowerCase().includes(lowerQuery)) && // Search by user email
				(viewOption === '' ||
					(viewOption === 'created' && t.user_id === $user?.id) ||
					(viewOption === 'shared' && t.user_id !== $user?.id))
			);
		});
	};

	const shareHandler = async (tool) => {
		const item = await getToolById(localStorage.token, tool.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		toast.success($i18n.t('Redirecting you to {{APP_NAME}} Community', { APP_NAME }));

		const url = 'https://openwebui.com';

		const tab = await window.open(`${url}/tools/create`, '_blank');

		const messageHandler = (event) => {
			if (event.origin !== url) return;
			if (event.data === 'loaded') {
				tab.postMessage(JSON.stringify(item), '*');
				window.removeEventListener('message', messageHandler);
			}
		};

		window.addEventListener('message', messageHandler, false);
		console.log(item);
	};

	const cloneHandler = async (tool) => {
		const _tool = await getToolById(localStorage.token, tool.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (_tool) {
			sessionStorage.tool = JSON.stringify({
				..._tool,
				id: `${_tool.id}_clone`,
				name: `${_tool.name} (Clone)`
			});
			goto('/workspace/tools/create');
		}
	};

	const exportHandler = async (tool) => {
		const _tool = await getToolById(localStorage.token, tool.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (_tool) {
			let blob = new Blob([JSON.stringify([_tool])], {
				type: 'application/json'
			});
			saveAs(blob, `tool-${_tool.id}-export-${Date.now()}.json`);
		}
	};

	const deleteHandler = async (tool) => {
		const res = await deleteToolById(localStorage.token, tool.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Tool deleted successfully'));
			await init();
		}
	};

	const init = async () => {
		tools = await getToolList(localStorage.token);
		_tools.set(await getTools(localStorage.token));
	};

	onMount(async () => {
		viewOption = localStorage?.workspaceViewOption || '';
		await init();
		loaded = true;

		const onKeyDown = (event) => {
			if (event.key === 'Shift') {
				shiftKey = true;
			}
		};

		const onKeyUp = (event) => {
			if (event.key === 'Shift') {
				shiftKey = false;
			}
		};

		const onBlur = () => {
			shiftKey = false;
		};

		window.addEventListener('keydown', onKeyDown);
		window.addEventListener('keyup', onKeyUp);
		window.addEventListener('blur-sm', onBlur);

		return () => {
			window.removeEventListener('keydown', onKeyDown);
			window.removeEventListener('keyup', onKeyUp);
			window.removeEventListener('blur-sm', onBlur);
		};
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Neural Extensions')} • {$WEBUI_NAME}
	</title>
</svelte:head>

<ImportModal
	bind:show={showImportModal}
	onImport={(tool) => {
		sessionStorage.tool = JSON.stringify({
			...tool
		});
		goto('/workspace/tools/create');
	}}
	loadUrlHandler={async (url) => {
		return await loadToolByUrl(localStorage.token, url);
	}}
	successMessage={$i18n.t('Tool imported successfully')}
/>

<!-- Hidden Import Input -->
<input
	id="documents-import-input"
	bind:this={toolsImportInputElement}
	bind:files={importFiles}
	type="file"
	accept=".json"
	hidden
	on:change={() => {
		console.log(importFiles);
		showConfirm = true;
	}}
/>

{#if loaded}
	<div class="flex flex-col gap-4 w-full h-full relative">
		<!-- HEADER: Neural Extensions Title -->
		<div
			class="relative flex flex-col md:flex-row justify-between items-end md:items-center px-4 pt-6 pb-2"
		>
			<div class="flex flex-col">
				<h1
					class="text-4xl font-secondary font-light tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-gray-100 to-gray-500"
					in:fly={{ y: -10, duration: 500 }}
				>
					Neural Extensions
				</h1>
				<p
					class="text-sm text-blue-400/80 font-mono tracking-wider mt-1"
					in:fly={{ y: -5, duration: 500, delay: 100 }}
				>
					System Modules: {filteredItems.length} Active
				</p>
			</div>
		</div>

		<!-- CONTROL BAR: Floating Glassmorphic Action Bar -->
		<div class="sticky top-0 z-30 px-4 py-2" in:fade={{ duration: 300 }}>
			<div
				class="flex flex-wrap md:flex-nowrap items-center gap-2 p-2 rounded-2xl bg-gray-900/60 border border-white/5 backdrop-blur-xl shadow-lg shadow-black/20"
			>
				<!-- SEARCH -->
				<div class="flex-1 min-w-[200px] relative group">
					<div
						class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-400 transition-colors"
					>
						<Search className="size-4" />
					</div>
					<input
						class="w-full bg-white/5 border border-white/5 rounded-xl py-2 pl-9 pr-8 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:bg-white/10 focus:border-blue-500/30 transition-all font-primary"
						bind:value={query}
						placeholder={$i18n.t('Search system modules...')}
					/>
					{#if query}
						<button
							class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-white rounded-full hover:bg-white/10 transition"
							on:click={() => {
								query = '';
							}}
						>
							<XMark className="size-3" strokeWidth="2" />
						</button>
					{/if}
				</div>

				<!-- ACTIONS -->
				<div class="flex items-center gap-2 shrink-0">
					{#if $user?.role === 'admin' || $user?.permissions?.workspace?.tools_import}
						<Tooltip content={$i18n.t('Import from File')}>
							<button
								class="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/5 transition-all"
								on:click={() => {
									toolsImportInputElement.click();
								}}
							>
								<!-- Simple Import Icon -->
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke-width="1.5"
									stroke="currentColor"
									class="size-4"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
									/>
								</svg>
							</button>
						</Tooltip>
					{/if}

					{#if $user?.role === 'admin'}
						<AddToolMenu
							createHandler={() => {
								goto('/workspace/tools/create');
							}}
							importFromLinkHandler={() => {
								showImportModal = true;
							}}
						>
							<button
								class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-500/20 transition-all active:scale-95"
							>
								<Plus className="size-4" strokeWidth="2.5" />
								<span class="hidden md:inline">{$i18n.t('New Extension')}</span>
							</button>
						</AddToolMenu>
					{:else}
						<a
							class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-500/20 transition-all active:scale-95"
							href="/workspace/tools/create"
						>
							<Plus className="size-4" strokeWidth="2.5" />
							<span class="hidden md:inline">{$i18n.t('New Extension')}</span>
						</a>
					{/if}
				</div>
			</div>
		</div>

		<!-- CONTENT: Grid or Empty State -->
		<div class="px-4 pb-20 flex-1 overflow-y-auto overflow-x-hidden">
			{#if (filteredItems ?? []).length !== 0}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 pb-12">
					{#each filteredItems as tool (tool.id)}
						<div
							in:fly={{ y: 20, duration: 400 }}
							class="group relative flex flex-col justify-between h-48 p-5 bg-gray-900/40 border border-white/5 rounded-2xl hover:bg-gray-800/60 hover:border-blue-500/30 hover:shadow-[0_0_30px_rgba(59,130,246,0.1)] hover:-translate-y-1 transition-all duration-300 backdrop-blur-sm overflow-hidden"
						>
							<!-- Decorative Glow -->
							<div
								class="absolute -right-10 -top-10 w-32 h-32 bg-blue-500/5 rounded-full blur-3xl group-hover:bg-blue-500/10 transition-colors duration-500"
							></div>

							<!-- Top Section -->
							<div class="flex justify-between items-start z-10 w-full">
								<div class="flex items-center gap-3 overflow-hidden">
									<!-- Generated Avatar / Icon Placeholder -->
									<div
										class="shrink-0 size-10 rounded-lg bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/5 flex items-center justify-center text-blue-400"
									>
										{#if tool?.meta?.manifest?.icon}
											<img src={tool.meta.manifest.icon} class="size-6 object-contain" alt="icon" />
										{:else}
											<PuzzlePiece className="size-6" />
										{/if}
									</div>

									<div class="flex flex-col overflow-hidden">
										<div
											class="text-sm font-semibold text-gray-100 line-clamp-1 group-hover:text-blue-300 transition-colors"
										>
											{tool.name}
										</div>
										<div class="text-[10px] text-gray-500 uppercase tracking-widest font-mono">
											v{tool?.meta?.manifest?.version ?? '1.0.0'}
										</div>
									</div>
								</div>

								<!-- Action Menu -->
								{#if tool.write_access}
									<ToolMenu
										editHandler={() => {
											goto(`/workspace/tools/edit?id=${encodeURIComponent(tool.id)}`);
										}}
										shareHandler={() => {
											shareHandler(tool);
										}}
										cloneHandler={() => {
											cloneHandler(tool);
										}}
										exportHandler={() => {
											exportHandler(tool);
										}}
										deleteHandler={async () => {
											selectedTool = tool;
											showDeleteConfirm = true;
										}}
										onClose={() => {}}
									>
										<button
											class="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition"
										>
											<EllipsisHorizontal className="size-5" />
										</button>
									</ToolMenu>
								{/if}
							</div>

							<!-- Description -->
							<div class="mt-3 text-xs text-gray-400 line-clamp-2 z-10 font-light leading-relaxed">
								{tool?.meta?.description ?? tool?.id}
							</div>

							<!-- Bottom Section -->
							<div
								class="flex items-center justify-between mt-auto pt-4 z-10 border-t border-white/5"
							>
								<div class="flex items-center gap-2">
									{#if tool.write_access}
										<Tooltip content={$i18n.t('Valves')}>
											<button
												class="text-gray-500 hover:text-blue-400 transition"
												on:click={() => {
													selectedTool = tool;
													showValvesModal = true;
												}}
											>
												<svg
													xmlns="http://www.w3.org/2000/svg"
													fill="none"
													viewBox="0 0 24 24"
													stroke-width="1.5"
													stroke="currentColor"
													class="size-4"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z"
													/>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
													/>
												</svg>
											</button>
										</Tooltip>
									{:else}
										<Badge type="muted" content={$i18n.t('Read Only')} />
									{/if}
								</div>

								<div class="text-[10px] text-gray-600 dark:text-gray-500 font-mono">
									{tool?.user?.name ?? 'System'}
								</div>
							</div>
						</div>
					{/each}

					<!-- Discovery Hub Card -->
					{#if $config?.features.enable_community_sharing}
						<a
							href="https://openwebui.com/tools"
							target="_blank"
							class="group relative flex flex-col justify-center items-center h-48 p-5 bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-blue-500/20 rounded-2xl hover:border-blue-400/50 hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] hover:-translate-y-1 transition-all duration-300 backdrop-blur-sm"
						>
							<div
								class="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition duration-500"
							></div>
							<div
								class="size-12 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400 mb-3 group-hover:scale-110 transition-transform"
							>
								<CubeTransparent className="size-6" />
							</div>
							<div class="text-sm font-semibold text-blue-200">Discovery Hub</div>
							<div class="text-xs text-blue-300/60 mt-1 text-center">
								Find new neural extensions from the community
							</div>
						</a>
					{/if}
				</div>
			{:else}
				<!-- EMPTY STATE: System Scan Visualization -->
				<div class="w-full h-[60vh] flex flex-col justify-center items-center">
					<div class="relative size-32 mb-8">
						<!-- Scanning Animation Rings -->
						<div
							class="absolute inset-0 border-2 border-blue-500/30 rounded-full animate-[ping_3s_ease-in-out_infinite]"
						></div>
						<div
							class="absolute inset-4 border border-blue-500/20 rounded-full animate-[spin_10s_linear_infinite]"
						></div>
						<div class="absolute inset-0 flex items-center justify-center text-blue-500/50">
							<Search className="size-10" />
						</div>
					</div>

					<div class="max-w-md text-center space-y-2">
						<div class="text-xl font-secondary font-light text-gray-200">System Scan Complete</div>
						<div class="text-sm text-gray-500 font-mono">
							No active neural extensions found matching your query.
						</div>
						<div class="pt-6">
							<button
								class="text-xs text-blue-400 hover:text-blue-300 underline underline-offset-4"
								on:click={() => {
									query = '';
								}}
							>
								Clear Search Parameters
							</button>
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>

	<DeleteConfirmDialog
		bind:show={showDeleteConfirm}
		title={$i18n.t('Delete extension?')}
		on:confirm={() => {
			deleteHandler(selectedTool);
		}}
	>
		<div class=" text-sm text-gray-500 truncate">
			{$i18n.t('This will permanently decouple')}
			<span class="font-medium text-red-400">{selectedTool.name}</span>
			{$i18n.t('from the neural network.')}
		</div>
	</DeleteConfirmDialog>

	<ValvesModal bind:show={showValvesModal} type="tool" id={selectedTool?.id ?? null} />
	<ManifestModal bind:show={showManifestModal} manifest={selectedTool?.meta?.manifest ?? {}} />

	<ConfirmDialog
		bind:show={showConfirm}
		on:confirm={() => {
			const reader = new FileReader();
			reader.onload = async (event) => {
				const _tools = JSON.parse(event.target.result);
				console.log(_tools);

				for (const tool of _tools) {
					const res = await createNewTool(localStorage.token, tool).catch((error) => {
						toast.error(`${error}`);
						return null;
					});
				}

				toast.success($i18n.t('Tool imported successfully'));
				tools.set(await getTools(localStorage.token));
			};

			reader.readAsText(importFiles[0]);
		}}
	>
		<div class="text-sm text-gray-500">
			<div class=" bg-yellow-500/20 text-yellow-700 dark:text-yellow-200 rounded-lg px-4 py-3">
				<div>{$i18n.t('Please carefully review the following warnings:')}</div>

				<ul class=" mt-1 list-disc pl-4 text-xs">
					<li>
						{$i18n.t('Tools have a function calling system that allows arbitrary code execution.')}.
					</li>
					<li>{$i18n.t('Do not install tools from sources you do not fully trust.')}</li>
				</ul>
			</div>

			<div class="my-3">
				{$i18n.t(
					'I acknowledge that I have read and I understand the implications of my action. I am aware of the risks associated with executing arbitrary code and I have verified the trustworthiness of the source.'
				)}
			</div>
		</div>
	</ConfirmDialog>
{:else}
	<div class="w-full h-full flex justify-center items-center">
		<Spinner className="size-5" />
	</div>
{/if}
