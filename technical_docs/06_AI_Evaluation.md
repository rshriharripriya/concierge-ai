# Part 6: AI Evaluation & Metrics

## Overview
We don't "guess" if the AI is good. We measure it. We use **RAGAS (Retrieval Augmented Generation Assessment)**, an industry-standard framework for evaluating RAG pipelines.

## The Metrics
We track 5 key signals (`evaluation/ragas_evaluator.py`):

1.  **Faithfulness** (The "Liar" Detector)
    *   Measures: Is the answer derived *solely* from the retrieved context?
    *   Goal: > 0.90. Prevents the AI from making up tax laws not found in our docs.

2.  **Answer Relevancy**
    *   Measures: Does the answer actually address the user's question?
    *   Goal: > 0.85.

3.  **Context Precision**
    *   Measures: Is the *most* relevant document ranked first?
    *   Importance: LLMs pay more attention to the top of the context window.

4.  **Context Recall**
    *   Measures: Did we retrieve *all* the necessary information to answer the question?

## Automated Evaluation Pipeline
We have a local CLI tool (`evaluation/run_evaluation.py`) that:
1.  Runs a "Golden Dataset" of questions/answers.
2.  Uses **LLM-as-a-Judge** (specifically `gemini-2.5-flash-lite` via LiteLLM) to score the system's outputs.
3.  Generates a pass/fail report based on our strict thresholds.

## Continuous Monitoring
In production, we can run a "Faithfulness Check" in the background (using FastAPI `BackgroundTasks`) for every user query. This allows us to flag potentially hallucinated answers *after* they are sent, alerting admins to review the conversation.
