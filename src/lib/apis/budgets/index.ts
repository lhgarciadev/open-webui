import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface UserBudget {
	user_id: string;
	initial_budget: number;
	current_balance: number;
	hard_limit: boolean;
	percent_remaining: number;
	created_at: number;
	updated_at: number;
}

export interface SetBudgetForm {
	initial_budget: number;
	hard_limit?: boolean;
	reset_balance?: boolean;
}

export interface SpendingTransaction {
	id: string;
	user_id: string;
	chat_id: string;
	message_id: string;
	model_id: string;
	input_tokens: number;
	output_tokens: number;
	input_cost_usd: number;
	output_cost_usd: number;
	total_cost_usd: number;
	created_at: number;
}

export interface SpendingResponse {
	transactions: SpendingTransaction[];
	total_spent_usd: number;
	count: number;
}

export interface AllBudgetsItem {
	user_id: string;
	user_name: string;
	user_email: string;
	initial_budget: number;
	current_balance: number;
	hard_limit: boolean;
	percent_remaining: number;
	total_spent_usd: number;
	created_at: number;
	updated_at: number;
}

export interface AllBudgetsResponse {
	budgets: AllBudgetsItem[];
	total: number;
}

export interface SpendingQueryParams {
	skip?: number;
	limit?: number;
	start_date?: number;
	end_date?: number;
}

export interface PaginationParams {
	skip?: number;
	limit?: number;
}

export const getUserBudget = async (token: string): Promise<UserBudget | null> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/budgets/me/budget`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (res.status === 404) {
				return null;
			}
			if (!res.ok) {
				throw await res.json();
			}
			return res.json();
		})
		.catch((err) => {
			if (err && err.detail) {
				error = err.detail;
			}
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserBudgetAdmin = async (
	token: string,
	userId: string
): Promise<UserBudget | null> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/budgets/${userId}/budget`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (res.status === 404) {
				return null;
			}
			if (!res.ok) {
				throw await res.json();
			}
			return res.json();
		})
		.catch((err) => {
			if (err && err.detail) {
				error = err.detail;
			}
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const setUserBudget = async (
	token: string,
	userId: string,
	form: SetBudgetForm
): Promise<UserBudget> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/budgets/${userId}/budget`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(form)
	})
		.then(async (res) => {
			if (!res.ok) {
				throw await res.json();
			}
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserSpending = async (
	token: string,
	userId: string,
	params?: SpendingQueryParams
): Promise<SpendingResponse> => {
	let error = null;

	const searchParams = new URLSearchParams();
	if (params?.skip) {
		searchParams.append('skip', params.skip.toString());
	}
	if (params?.limit) {
		searchParams.append('limit', params.limit.toString());
	}
	if (params?.start_date) {
		searchParams.append('start_date', params.start_date.toString());
	}
	if (params?.end_date) {
		searchParams.append('end_date', params.end_date.toString());
	}

	const res = await fetch(
		`${WEBUI_API_BASE_URL}/budgets/${userId}/spending?${searchParams.toString()}`,
		{
			method: 'GET',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
				authorization: `Bearer ${token}`
			}
		}
	)
		.then(async (res) => {
			if (!res.ok) {
				throw await res.json();
			}
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getAllBudgets = async (
	token: string,
	params?: PaginationParams
): Promise<AllBudgetsResponse> => {
	let error = null;

	const searchParams = new URLSearchParams();
	if (params?.skip) {
		searchParams.append('skip', params.skip.toString());
	}
	if (params?.limit) {
		searchParams.append('limit', params.limit.toString());
	}

	const res = await fetch(
		`${WEBUI_API_BASE_URL}/budgets/admin/budgets?${searchParams.toString()}`,
		{
			method: 'GET',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
				authorization: `Bearer ${token}`
			}
		}
	)
		.then(async (res) => {
			if (!res.ok) {
				throw await res.json();
			}
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
