---
tags:
  - memory/ai
---

# AI Interpretation

This is an entry point; no AI provider or implementation exists yet.
The presentation contract is described in [[09_REPORT_DESIGN]].

```text
CALCULATION LAYER
        ↓
VERIFIED UNIFIED JSON
        ↓
INTERPRETATION LAYER
        ↓
STRUCTURED REPORT JSON
```

AI never recalculates results. Send only data needed to interpret verified JSON: name, surname and
full birthplace should not be sent when they are unnecessary. Future provider abstraction may support
Gemini or OpenAI, but neither is accepted or implemented. No detailed
`interpretation-architecture.md` exists yet; create it only when an interpretation architecture is
actually decided.
