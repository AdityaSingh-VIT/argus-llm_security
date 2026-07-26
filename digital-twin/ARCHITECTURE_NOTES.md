# Architecture Notes

## What changed, and why

| Gap | Fix |
|---|---|
| No generic `File` node — only `PDF` | Added `File` node with `File -[:IS_A]-> PDF`, and `Chatbot -[:READS]-> File` |
| Prompt Injection detected by risk engine but never a real graph node | Added `PromptInjection` node: `Attacker -[:USES]-> PromptInjection -[:AFFECTS]-> Chatbot` |
| Attack chain to "CEO" had no recipient node — path ended at `Email` | Added `Person` node: `Email -[:SENDS_TO]-> Person` |
| No "Tool Access" risk category (spec asked for 30 pts) | Added `Tool` node + `Chatbot -[:ACCESSES]-> Tool`; risk engine scores it separately from "Sensitive Data" |
| No `POST` endpoint for automatic graph updates | Added `POST /build-graph`, validated with a Pydantic model |
| `GET /graph` returned `{"connections": []}` | Now returns `{"nodes": [...], "edges": [...]}` — the shape React Flow actually wants |
| Risk engine used hardcoded string checks (`if "Prompt Injection" in target`) that could never match real graph data | Risk engine now runs a single Cypher query against the live graph and derives each factor from real relationships |
| Labels/relationship types typed as raw strings in 3+ files | Centralized in `graph/schema.py` as enums — a typo now fails at import, not silently at query time |
| No connection lifecycle management | `main.py` opens the driver once at startup (`verify_connectivity()` fails fast if Neo4j is unreachable) and closes it once at shutdown |
| No CORS | Added, since the React frontend is a different origin in dev |

## Answers to your review questions

**Does Digital Twin own risk scoring, or does another security team own it?**
Reasonable default: Digital Twin owns the *mechanical* scoring (the graph traversal that says "yes, this chatbot has prompt-injection exposure right now"), but the *weights* (why prompt injection = 20, sensitive data = 40) should be config a security/GRC team can tune without touching your code. Consider moving `WEIGHTS` in `risk_engine.py` into an env var or a small config table if that team wants a say. Worth confirming who's accountable for the *numbers*, since that's usually a policy decision, not an engineering one.

**Should chatbot send metadata/events into Digital Twin through API?**
Yes — that's what `POST /build-graph` is for now. Push, not pull: the chatbot (or a message bus sitting in front of it) calls this endpoint after each relevant action (file read, DB call, email sent) rather than the twin polling for changes.

**Is Neo4j the correct ownership boundary?**
For "graph of the system + traversal queries," yes, that's squarely in your lane. Where it gets blurry: if another team already owns a CMDB or asset inventory, you don't want two independent sources of truth for "what components exist." Cleanest split is usually: they own asset/inventory facts, you own the *relationships and traversal* built from those facts.

**Should Prompt Injection detection happen before Digital Twin or inside it?**
Detection (the ML/pattern-matching that decides "this looks like an injection attempt") should happen upstream, close to the chatbot/guardrail layer — that's a different skill set and a different latency budget than graph work. Digital Twin's job is to *record* that a detection happened and wire it into the graph so it's visible in attack-path and risk queries, not to do the detecting itself.

**Should vulnerability scanning results become graph nodes?**
Likely yes, as a `Vulnerability` node type with something like `AFFECTS`/`EXISTS_ON` relationships to the component it applies to — this is exactly the same pattern as `PromptInjection`. Worth confirming with whoever owns scanning whether they want push (their scanner calls `POST /build-graph`-style) or you pull from their API on a schedule.

**Does another component already create attack paths?**
Not something this codebase can answer on its own — but if another team has an existing attack-path/graph tool, you want to agree on canonical node/relationship naming *before* both systems diverge (this is exactly the schema-drift problem `graph/schema.py` fixes internally — same idea applies across teams).

## Still open / not addressed in this pass
- Multi-tenant scoping (`/risk` takes an optional `chatbot` param now, but there's no auth/tenant isolation yet).
- No audit trail of *when* an edge was created — if "detect drift over time" matters, add a `created_at` property on relationships.
- `find_attack_paths` traverses up to 6 hops by default; on a large graph this can get expensive — add an index on `Attacker.name`, `Person.name`, `Email.address` if this becomes slow (`CREATE INDEX ... FOR (n:Attacker) ON (n.name)`).
