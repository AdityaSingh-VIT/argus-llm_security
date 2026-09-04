# Argus AI — API Specifications

## 1. Backend Gateway (Port 8000)
- `POST /auth/register`: Create user account and return JWT token.
- `POST /auth/login`: Authenticate and return JWT token.
- `POST /scan`: Enqueue a security assessment against a target chatbot.
- `GET /scan/{id}`: Poll status, findings, and logs for a scan.
- `GET /dashboard/stats`: Retrieve aggregate metrics (overall risk score, attack counts, top vulnerabilities).
- `GET /graph`: Fetch the current Digital Twin topology.
- `GET /network/live`: WebSocket stream for live packet capture.

## 2. Digital Twin Service (Port 7001)
- `POST /build-graph`: Push new components/edges into the Neo4j Digital Twin.
- `GET /graph`: Return the graph in React Flow format `{ nodes: [...], edges: [...] }`.
- `GET /risk`: Return calculated risk scores for all chatbot instances.
- `GET /attack-paths`: Return computed paths from attacker nodes to sensitive data sinks.
- `GET /critical-nodes`: Return nodes with the highest centrality/exposure score.

## 3. Attack Engine Service (Port 7002)
- `POST /generate`: Generate attack vectors from scenario context.
- `POST /execute`: Fire an attack payload against target and analyze output.
- `GET /health`: Health status check.

## 4. Target Chatbot (Port 7003)
- `POST /chat`: Main chat endpoint (`{ message: string, session_id?: string }`).
- `POST /upload-doc`: Upload document to knowledge base (for RAG poisoning tests).
- `POST /defense/{level}`: Toggle defense level (0=Vulnerable, 1=Prompt Guard, 2=Strict Filter).
