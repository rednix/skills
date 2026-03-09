#!/usr/bin/env node

const apiKey = process.argv[2] ?? '';
const runId = process.argv[3];
const baseUrl = (process.argv[4] ?? 'https://gateway-api.binaryworks.app').replace(/\/+$/, '');

if (!apiKey) {
  console.error('usage: node poll.mjs <api_key> <run_id> [base_url]');
  process.exit(1);
}

if (!runId) {
  console.error('usage: node poll.mjs <api_key> <run_id> [base_url]');
  process.exit(1);
}

const response = await fetch(`${baseUrl}/skill/runs/${encodeURIComponent(runId)}`, {
  method: 'GET',
  headers: {
    'X-API-Key': apiKey
  }
});

const body = await response.text();
console.log(body);

if (!response.ok) {
  process.exit(1);
}
