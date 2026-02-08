import typography from '@tailwindcss/typography';
import containerQueries from '@tailwindcss/container-queries';

/** @type {import('tailwindcss').Config} */
export default {
	darkMode: 'class',
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				gray: {
					50: 'var(--color-gray-50, #f9f9f9)',
					100: 'var(--color-gray-100, #ececec)',
					200: 'var(--color-gray-200, #e3e3e3)',
					300: 'var(--color-gray-300, #cdcdcd)',
					400: 'var(--color-gray-400, #b4b4b4)',
					500: 'var(--color-gray-500, #9b9b9b)',
					600: 'var(--color-gray-600, #676767)',
					700: 'var(--color-gray-700, #4e4e4e)',
					800: 'var(--color-gray-800, #333)',
					850: 'var(--color-gray-850, #262626)',
					900: 'var(--color-gray-900, #171717)',
					950: 'var(--color-gray-950, #0d0d0d)'
				},
				primary: {
					50: 'var(--color-primary-50, #eff6ff)',
					100: 'var(--color-primary-100, #dbeafe)',
					200: 'var(--color-primary-200, #bfdbfe)',
					300: 'var(--color-primary-300, #93c5fd)',
					400: 'var(--color-primary-400, #60a5fa)',
					DEFAULT: 'var(--app-color-primary, #3b82f6)',
					500: 'var(--color-primary-500, #3b82f6)',
					600: 'var(--color-primary-600, #2563eb)',
					700: 'var(--color-primary-700, #1d4ed8)',
					800: 'var(--color-primary-800, #1e40af)',
					900: 'var(--color-primary-900, #1e3a8a)',
					950: 'var(--color-primary-950, #172554)'
				}
			},
			typography: {
				DEFAULT: {
					css: {
						pre: false,
						code: false,
						'pre code': false,
						'code::before': false,
						'code::after': false
					}
				}
			},
			padding: {
				'safe-bottom': 'env(safe-area-inset-bottom)'
			},
			transitionProperty: {
				width: 'width'
			},
			fontFamily: {
				sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
				serif: ['InstrumentSerif', 'ui-serif', 'Georgia', 'Cambria', 'Times New Roman', 'Times', 'serif'],
				mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace']
			}
		}
	},
	plugins: [typography, containerQueries]
};
