---
name: crypto-degen-toolkit
description: "On-chain research and DeFi operations toolkit for crypto traders. Check wallet balances, track token prices, analyze DEX liquidity, monitor gas fees, scan for new token launches, and execute basic DeFi operations. Use when: checking crypto prices, analyzing wallets, monitoring DeFi positions, researching new tokens, tracking gas fees, or getting on-chain data from EVM chains (Ethereum, Base, Arbitrum, BSC, etc.)."
version: 1.0.0
---

# Crypto Degen Toolkit 🔗

On-chain research and DeFi intelligence for crypto-native agents.

## Capabilities

### Price & Market Data
Use public APIs (no key needed):
```bash
# CoinGecko free API
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=ethereum,bitcoin,solana&vs_currencies=usd,cny"

# DexScreener (DEX prices, new pairs)
curl -s "https://api.dexscreener.com/latest/dex/tokens/{TOKEN_ADDRESS}"

# Search token by name
curl -s "https://api.dexscreener.com/latest/dex/search?q={QUERY}"
```

### Wallet Analysis
```bash
# ETH balance (replace RPC as needed)
curl -s -X POST https://eth.llamarpc.com -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["WALLET_ADDRESS","latest"],"id":1}'

# Token holdings via Debank (free tier)
curl -s "https://api.debank.com/user/token_list?id=WALLET_ADDRESS&chain_id=eth&is_all=false"
```

### Gas Tracker
```bash
# ETH gas prices
curl -s "https://api.etherscan.io/api?module=gastracker&action=gasoracle"

# Or via RPC
curl -s -X POST https://eth.llamarpc.com -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}'
```

### New Token Scanner
```bash
# Latest pairs on DexScreener
curl -s "https://api.dexscreener.com/latest/dex/pairs/{CHAIN_ID}/{PAIR_ADDRESS}"

# New pairs (last 24h)
curl -s "https://api.dexscreener.com/token-profiles/latest/v1"
```

### Chain RPCs (Free, No Key)
| Chain | RPC |
|-------|-----|
| Ethereum | https://eth.llamarpc.com |
| Base | https://base.llamarpc.com |
| Arbitrum | https://arb1.arbitrum.io/rpc |
| BSC | https://bsc-dataseed.binance.org |
| Polygon | https://polygon-rpc.com |
| Optimism | https://mainnet.optimism.io |
| Solana | https://api.mainnet-beta.solana.com |

## Safety Rules

⚠️ **CRITICAL: This skill is for RESEARCH and MONITORING only.**

- **NEVER** execute transactions without explicit user confirmation
- **NEVER** handle or request private keys or seed phrases
- **ALWAYS** flag high-risk tokens (honeypots, rug patterns)
- **ALWAYS** warn about smart contract risks before any interaction
- When analyzing tokens, check: liquidity lock, holder concentration, contract verification

## Red Flags to Auto-Detect
When analyzing a token, flag if:
- Top 10 holders own >50% of supply
- Liquidity is <$10k
- Contract is unverified
- No social links or website
- Created in last 24h with sudden pump
- Sell tax >5%
- Honeypot pattern detected

## Common Workflows

### "Check my wallet"
1. Query balance via RPC
2. Fetch token list via DeBank
3. Get current prices via CoinGecko
4. Calculate total portfolio value
5. Show P&L if historical data available

### "Find alpha / new tokens"
1. Scan DexScreener for new pairs
2. Filter by volume, liquidity, age
3. Check contract on Etherscan
4. Analyze holder distribution
5. Present findings with risk rating

### "Gas timing"
1. Check current gas price
2. Compare to 24h average
3. Suggest optimal time to transact
4. Monitor and alert when gas drops below threshold
