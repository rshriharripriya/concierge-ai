# Part 3: Multi-Agent Architecture

## Overview
Concierge AI is not a monolith. It operates as a federation of specialized agents (or "services") that collaborate to solve user problems. The Global Orchestrator (`chat.py`) delegates control to these agents based on the state of the conversation.

## Agent 1: The Supervisor (LLM Router)
Located in `services/llm_router.py`, this agent acts as the "Traffic Controller".
*   **Model**: Gemini 2.0 Flash (for speed/reasoning balance) or Llama 3.
*   **Task**: Analyze the query for *implied* intent, not just keywords.
*   **Output Schema**:
    ```json
    {
      "intent": "complex_tax",
      "technical_complexity": 5,
      "risk_exposure": 4,
      "urgency": 1,
      "route": "human"
    }
    ```
*   **Logic**: It detects nuances. "How do I amend?" is procedural (Complexity 2), whereas "I received a CP2000 notice" is high-risk (Complexity 5, Urgent).

## Agent 2: The Researcher (RAG Agent)
Located in `services/rag_service.py`.
*   **Task**: Autonomous information retrieval.
*   **Capabilities**: Contextualization, Self-correction (via Reranking), Source citation.
*   **Autonomy**: If it cannot find high-confidence documents (Confidence < 0.6), it signals the Router to escalate to a human, effectively "raising its hand" when it doesn't know the answer.

## Agent 3: The Matchmaker (Expert Matcher)
Located in `services/expert_matcher.py`.
*   **Task**: When `route="human"`, this agent finds the best human for the job.
*   **Algorithm**: Multi-Objective Optimization.
    *   `Score = (Specialty * 0.4) + (Availability * 0.3) + (Performance * 0.2) + (Semantic_Match * 0.1)`
*   **Semantic Matching**: It embeds the user's query and compares it to the *embedding of the expert's resume/bio*. This allows a query about "crypto staking" to match an expert who lists "DeFi Taxation" in their bio, even if the exact keyword "staking" isn't a tag.

## The Handover Protocol
The system implements a smooth protocol between agents:
1.  **Router** analyzes query -> decides `human`.
2.  **Matchmaker** selects Expert A.
3.  **System** generates a warm handover message: "I've analyzed your complex tax situation. I'm connecting you with Expert A, who specializes in International Tax..."
This creates a cohesive "Concierge" experience where AI and Humans work as one team.
