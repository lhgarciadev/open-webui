module.exports = {
	root: true,
	extends: [
		'eslint:recommended',
		'plugin:@typescript-eslint/recommended',
		'plugin:svelte/recommended',
		'plugin:cypress/recommended',
		'prettier'
	],
	parser: '@typescript-eslint/parser',
	plugins: ['@typescript-eslint'],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2020,
		extraFileExtensions: ['.svelte']
	},
	env: {
		browser: true,
		es2017: true,
		node: true
	},
	rules: {
		'no-constant-condition': 'off',
		'no-undef': 'off',
		'no-empty': 'off',
		'no-unused-expressions': 'off',
		'no-unsafe-optional-chaining': 'off',
		'no-ex-assign': 'off',
		'no-async-promise-executor': 'off',
		'no-control-regex': 'off',
		'no-useless-escape': 'off',
		'prefer-const': 'off',
		'no-prototype-builtins': 'off',
		'@typescript-eslint/no-explicit-any': 'off',
		'@typescript-eslint/no-unused-vars': 'off',
		'@typescript-eslint/no-unused-expressions': 'off',
		'@typescript-eslint/no-unsafe-function-type': 'off',
		'@typescript-eslint/no-empty-object-type': 'off',
		'@typescript-eslint/ban-ts-comment': 'off',
		'svelte/no-at-html-tags': 'off',
		'svelte/no-unused-svelte-ignore': 'off',
		'svelte/valid-compile': 'off',
		'svelte/no-inner-declarations': 'off'
	},
	overrides: [
		{
			files: ['*.svelte'],
			parser: 'svelte-eslint-parser',
			parserOptions: {
				parser: '@typescript-eslint/parser'
			}
		}
	]
};
