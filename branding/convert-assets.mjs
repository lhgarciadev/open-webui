#!/usr/bin/env node
/**
 * Convert SVG assets to PNG for Cognitia branding
 * Uses sharp library for high-quality conversion
 */

import sharp from 'sharp';
import { readFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const sourceDir = join(__dirname, 'source');
const outputDir = join(__dirname, 'output');

// Ensure output directory exists
if (!existsSync(outputDir)) {
  mkdirSync(outputDir, { recursive: true });
}

// Asset conversion configurations
const conversions = [
  // Favicon variants
  { input: 'favicon.svg', output: 'favicon.png', width: 192, height: 192 },
  { input: 'favicon-dark.svg', output: 'favicon-dark.png', width: 192, height: 192 },
  { input: 'favicon.svg', output: 'favicon-96x96.png', width: 96, height: 96 },
  { input: 'favicon.svg', output: 'apple-touch-icon.png', width: 180, height: 180 },

  // PWA manifest icons
  { input: 'favicon.svg', output: 'web-app-manifest-192x192.png', width: 192, height: 192 },
  { input: 'favicon.svg', output: 'web-app-manifest-512x512.png', width: 512, height: 512 },

  // Logo
  { input: 'logo.svg', output: 'logo.png', width: 512, height: 512 },

  // Splash screens
  { input: 'splash.svg', output: 'splash.png', width: 512, height: 512 },
  { input: 'splash-dark.svg', output: 'splash-dark.png', width: 512, height: 512 },
];

async function convertSvgToPng(inputFile, outputFile, width, height) {
  const inputPath = join(sourceDir, inputFile);
  const outputPath = join(outputDir, outputFile);

  try {
    const svgBuffer = readFileSync(inputPath);

    await sharp(svgBuffer, { density: 300 })
      .resize(width, height, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toFile(outputPath);

    console.log(`✓ ${outputFile} (${width}x${height})`);
  } catch (error) {
    console.error(`✗ ${outputFile}: ${error.message}`);
  }
}

async function main() {
  console.log('Converting Cognitia brand assets...\n');

  for (const config of conversions) {
    await convertSvgToPng(config.input, config.output, config.width, config.height);
  }

  console.log('\n✓ Conversion complete! Output in:', outputDir);
}

main().catch(console.error);
