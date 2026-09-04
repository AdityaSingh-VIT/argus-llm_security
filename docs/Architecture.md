# Argus AI — System Architecture

Argus AI is an autonomous AI Application Security Posture Management (AI-SPM) platform designed to assess, trace, and defend enterprise LLM applications.

## High-Level Architecture

```
                  Enterprise Target AI
         +------------------------------------+
         |         Enterprise Chatbot         |
         |    (LangChain / Semantic Kernel)   |
         +-----------------+------------------+
                           |
          +----------------+----------------+
          |                |                |
      Vector DB        Email API        Database
```

Argus assesses this through five coordinated subsystems:

1. **Digital Twin (Neo4j)**: Maps actors, prompts, assistants, tools, vector indices, and relational databases as a knowledge graph.
2. **AI Red Team Agent (LangGraph)**:
   - **Planner**: Determines reachability of sensitive sinks and selects OWASP attack paths.
   - **Generator**: Uses Jinja2 templates and mutation strategies to generate context-specific jailbreaks and injection payloads.
   - **Executor**: Dispatches requests across multi-provider adapters (OpenAI, Claude, Gemini, Ollama, direct HTTP).
   - **Evaluator**: Evaluates responses using canary detectors, regex, and LLM-as-a-judge.
   - **Risk Scorer**: Computes severity scores (CVSS/OWASP aligned).
3. **Backend API Gateway (FastAPI)**: Coordinates scan orchestration, historical logging, user authentication, and PDF report generation.
4. **Live Network Inspector**: Real-time packet sniffer built with Scapy that tracks LLM API calls and exfiltration attempts.
5. **SOC Dashboard (React 18 + Vite)**: Enterprise management interface showing topology graphs, attack timelines, and posture metrics.
