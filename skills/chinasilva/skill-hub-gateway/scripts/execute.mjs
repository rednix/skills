#!/usr/bin/env node

const apiKey = process.argv[2] ?? '';
const capability = process.argv[3] ?? 'human_detect';
const inputJson = process.argv[4] ?? '{"image_url":"https://example.com/image.png"}';
const baseUrl = (process.argv[5] ?? 'https://gateway-api.binaryworks.app').replace(/\/+$/, '');

if (!apiKey) {
  console.error('usage: node execute.mjs <api_key> [capability] [input_json] [base_url]');
  process.exit(1);
}

let input;
try {
  input = JSON.parse(inputJson);
} catch {
  console.error('input must be valid JSON');
  process.exit(1);
}

const response = await fetch(`${baseUrl}/skill/execute`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey
  },
  body: JSON.stringify({ capability, input })
});

const body = await response.text();
console.log(body);

if (!response.ok) {
  process.exit(1);
}
