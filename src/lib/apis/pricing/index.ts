import { WEBUI_API_BASE_URL } from '$lib/constants';

export async function getPricingModels(token: string = '') {
	const res = await fetch(`${WEBUI_API_BASE_URL}/pricing/models`, {
		headers: token ? { Authorization: `Bearer ${token}` } : undefined
	});
	if (!res.ok) {
		throw new Error('Failed to fetch pricing');
	}
	return res.json();
}

export async function refreshPricingModels(token: string = '', model_ids: string[] = []) {
	const res = await fetch(`${WEBUI_API_BASE_URL}/pricing/refresh`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token ? { Authorization: `Bearer ${token}` } : {})
		},
		body: JSON.stringify({ model_ids })
	});
	if (!res.ok) {
		throw new Error('Failed to refresh pricing');
	}
	return res.json();
}
