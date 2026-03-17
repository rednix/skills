# nexus-orchestrator

**Orchestrator Agent** — Chain multiple AI services into automated workflows - describe a goal and the orchestrator plans, executes, and summarizes

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-orchestrator
```

Or manually copy the `SKILL.md` to your OpenClaw skills directory:

```bash
cp SKILL.md ~/.openclaw/skills/nexus-orchestrator/SKILL.md
```

## Usage

This skill is automatically invoked by your OpenClaw agent when a matching task is detected.

### Direct API Usage

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/orchestrator \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"input": "your query here"}'
```

## Pricing

- **$1.00** per request (paid in ADA via Masumi Protocol)
- **Free sandbox** available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- Discovery: [https://ai-service-hub-15.emergent.host/api/discover](https://ai-service-hub-15.emergent.host/api/discover)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
- A2A Agent Card: [https://ai-service-hub-15.emergent.host/.well-known/agent.json](https://ai-service-hub-15.emergent.host/.well-known/agent.json)

## License

Provided by NEXUS Platform. Usage subject to service terms.
