<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { marked } from 'marked';

	import { onMount, getContext, tick, createEventDispatcher } from 'svelte';
	import { blur, fade, fly } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	import { getChatList } from '$lib/apis/chats';
	import { updateFolderById } from '$lib/apis/folders';

	import {
		config,
		user,
		models as _models,
		temporaryChatEnabled,
		selectedFolder,
		chats,
		currentChatPage
	} from '$lib/stores';
	import { sanitizeResponseContent, extractCurlyBraceWords } from '$lib/utils';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';
	import { APP_NAME } from '$lib/constants/identity';

	import Suggestions from './Suggestions.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import MessageInput from './MessageInput.svelte';
	import FolderPlaceholder from './Placeholder/FolderPlaceholder.svelte';
	import FolderTitle from './Placeholder/FolderTitle.svelte';
	import Bolt from '$lib/components/icons/Bolt.svelte';
	import Sparkles from '$lib/components/icons/Sparkles.svelte';

	const i18n = getContext('i18n');

	export let createMessagePair: Function;
	export let stopResponse: Function;

	export let autoScroll = false;

	export let atSelectedModel: Model | undefined;
	export let selectedModels: [''];

	export let history;

	export let prompt = '';
	export let files = [];
	export let messageInput = null;

	export let selectedToolIds = [];
	export let selectedFilterIds = [];

	export let showCommands = false;

	export let imageGenerationEnabled = false;
	export let codeInterpreterEnabled = false;
	export let webSearchEnabled = false;

	export let onUpload: Function = (e) => {};
	export let onSelect = (e) => {};
	export let onChange = (e) => {};

	export let toolServers = [];

	let models = [];
	let selectedModelIdx = 0;

	$: if (selectedModels.length > 0) {
		selectedModelIdx = models.length - 1;
	}

	$: models = selectedModels.map((id) => $_models.find((m) => m.id === id));

	// Get suggestions for the grid
	$: suggestions =
		atSelectedModel?.info?.meta?.suggestion_prompts ??
		models[selectedModelIdx]?.info?.meta?.suggestion_prompts ??
		$config?.default_prompt_suggestions ??
		[];
</script>

<div
	class="m-auto w-full max-w-6xl px-2 @2xl:px-20 py-10 relative min-h-full flex flex-col justify-center items-center"
>
	{#if $selectedFolder}
		<div class="w-full flex flex-col justify-center items-center mb-8">
			<FolderTitle
				folder={$selectedFolder}
				onUpdate={async (folder) => {
					await chats.set(await getChatList(localStorage.token, $currentChatPage));
					currentChatPage.set(1);
				}}
				onDelete={async () => {
					await chats.set(await getChatList(localStorage.token, $currentChatPage));
					currentChatPage.set(1);

					selectedFolder.set(null);
				}}
			/>
		</div>
	{:else}
		<!-- AGENTIC COMMAND CENTER HEADER -->
		<div
			class="flex flex-col items-center justify-center mb-8 space-y-4 z-10"
			in:fade={{ duration: 800 }}
		>
			<div
				class="flex items-center gap-3 px-4 py-1.5 rounded-full border border-blue-500/20 bg-blue-500/5 backdrop-blur-md shadow-[0_0_15px_rgba(59,130,246,0.1)]"
			>
				<div class="relative flex h-2 w-2">
					<span
						class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"
					></span>
					<span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
				</div>
				<span class="text-[0.65rem] font-bold text-blue-400 tracking-[0.2em] font-primary"
					>SYSTEM ONLINE</span
				>
			</div>

			<div class="text-center relative">
				<h1
					class="text-6xl md:text-7xl font-secondary font-light tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-gray-100 to-gray-500/80 pb-2"
				>
					{APP_NAME}
				</h1>
				<div
					class="absolute -inset-10 bg-blue-500/5 blur-3xl -z-10 rounded-full opacity-0 animate-pulse"
				></div>
			</div>

			<p class="text-gray-500/80 font-light text-lg tracking-wide max-w-md text-center">
				{#if models[selectedModelIdx]?.name}
					Using <span class="text-gray-300 font-medium">{models[selectedModelIdx]?.name}</span> neural
					core.
				{:else}
					Neural Interaction Interface Ready.
				{/if}
			</p>
		</div>

		<!-- Neural Core Visualization (Background Glow) -->
		<div
			class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 opacity-20 pointer-events-none"
		>
			<div class="w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-[120px] animate-pulse"></div>
		</div>
	{/if}

	<!-- Message Input -->
	<div class="text-base font-normal @md:max-w-3xl w-full py-4 z-20 {atSelectedModel ? 'mt-2' : ''}">
		<MessageInput
			bind:this={messageInput}
			{history}
			{selectedModels}
			bind:files
			bind:prompt
			bind:autoScroll
			bind:selectedToolIds
			bind:selectedFilterIds
			bind:imageGenerationEnabled
			bind:codeInterpreterEnabled
			bind:webSearchEnabled
			bind:atSelectedModel
			bind:showCommands
			{toolServers}
			{stopResponse}
			{createMessagePair}
			placeholder={$i18n.t('How can I help you today?')}
			{onChange}
			{onUpload}
			on:submit={(e) => {
				dispatch('submit', e.detail);
			}}
		/>
	</div>

	<!-- Quick Actions Grid (Only if not in a folder) -->
	{#if !$selectedFolder && suggestions.length > 0}
		<div
			class="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5 z-10 mt-8"
			in:fly={{ y: 30, duration: 1000, delay: 200 }}
		>
			{#each suggestions as prompt, idx}
				<button
					class="group flex flex-col text-left p-5 rounded-2xl border border-white/5 bg-white/5 hover:bg-white/10 hover:border-white/10 hover:scale-[1.02] transition-all duration-300 backdrop-blur-xl shadow-lg hover:shadow-blue-500/10 relative overflow-hidden"
					on:click={() => onSelect({ type: 'prompt', data: prompt.content })}
				>
					<div
						class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition duration-500"
					></div>

					<div
						class="mb-3 p-2 w-fit rounded-lg bg-white/5 text-gray-400 group-hover:text-blue-400 group-hover:bg-blue-500/10 transition"
					>
						<Sparkles className="size-5" />
					</div>
					<div class="font-medium text-gray-200 group-hover:text-white transition line-clamp-1">
						{prompt.title?.[0] || prompt.content}
					</div>
					<div class="text-xs text-gray-500 mt-1 line-clamp-2 group-hover:text-gray-400">
						{prompt.title?.[1] || prompt.content}
					</div>
				</button>
			{/each}
		</div>
	{:else if $selectedFolder}
		<!-- Folder Placeholder content -->
		<div
			class="mx-auto px-4 md:max-w-3xl md:px-6 font-primary min-h-62"
			in:fade={{ duration: 200, delay: 200 }}
		>
			<FolderPlaceholder folder={$selectedFolder} />
		</div>
	{/if}

	<!-- Temporary Chat Warning -->
	{#if $temporaryChatEnabled}
		<div
			class="mt-8 flex items-center gap-2 text-gray-600 text-sm px-4 py-2 rounded-full bg-white/5 border border-white/5"
			in:fade={{ delay: 500 }}
		>
			<EyeSlash strokeWidth="2.5" className="size-4" />
			<span>Temporary Mode Active</span>
		</div>
	{/if}
</div>
