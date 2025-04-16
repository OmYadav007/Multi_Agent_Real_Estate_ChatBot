# Multi‑Agent Real Estate Assistant Chatbot

LINK- https://multiagentrealestatechatbot.streamlit.app/

A Streamlit web app that combines **GPT‑4o‑mini** with lightweight agent routing to answer tenancy‑law FAQs _and_ diagnose property issues from images.

---
## 1. Tech & Tools Used
| Purpose | Tool / Library |
|---------|----------------|
| Web UI | **[Streamlit](https://streamlit.io/)** 1.39 |
| LLM back‑end | **Azure OpenAI** → *gpt‑4o‑mini* (function‑calling + vision) |
| Image handling | `base64` encode / decode (Python std‑lib) and gpt-40-mini vision for image analysis |
| Backend | `python` |


**Project tree (key files only)**
```text
├── app.py                # Streamlit front‑end & chat loop
├── router_manager.py     # Picks the right agent per turn
├── constants.py          # Prompts, function schemas, fallback prompt
├── utility.py            # Azure client, image helpers, message utils
└── agents/
    ├── tenancy_faq.py    # System prompt for tenancy‑law FAQ
    └── issue_detection.py# System prompt for image/text issue detection
```

---
## 2. Logic Behind Agent Switching
1. **User turn** → `app.py` passes latest text to `router_manager.agent_router()`.
2. Router sends a *mini* classification request to GPT‑4o‑mini with:
   * an *agent‑classification* system prompt, and
   * an OpenAI **function‑calling schema** exposing two fake funcs: `tenancy_faq_agent` and `issue_detection_agent`.
3. GPT replies with a `function_call` naming one of those funcs.
4. Router maps that name to the corresponding file in `agents/` and returns its system prompt.
5. `app.py` **drops any earlier system prompts** (prevents stacking) and injects the new one before the full chat is sent for the real answer.

> Result: one chat window that transparently swaps expertise—no if/else spaghetti.

---
## 3. How Image‑Based Issue Detection Works
1. Streamlit uploader accepts multiple JPG/PNG files.
2. Each file is base64‑encoded into the exact format Vision GPT expects:
   ```json
   {"type":"image_url",
    "image_url":{"url":"data:image/jpeg;base64, …"}}
   ```
3. Presence of any image (or defect‑related wording) nudges the classifier toward **`issue_detection_agent`**.
4. Inside that agent GPT‑4o‑mini can now *see* the images, identify visible problems, list concise fixes, and advise when to call a pro.
5. The UI decodes the same base64 so Streamlit can preview the pictures inline.

---
## 4. Example Use Cases
| Scenario | What the user does | Agent chosen | Typical reply |
|----------|-------------------|--------------|---------------|
| **Rent increase** | “Can my landlord raise rent midway through my lease?” | `tenancy_faq_agent` | Asks for location → explains local rules; mentions notice periods. |
| **Security‑deposit dispute** | “My landlord won’t return my deposit. Help!” | `tenancy_faq_agent` | Outlines formal request steps; suggests small‑claims court if needed. |
| **Mold on ceiling (image)** | Uploads photo of moldy wall + “What should I do?” | `issue_detection_agent` | Identifies mold, lists remediation steps, recommends pro if severe. |
| **Leaky faucet (text)** | “Bathroom faucet keeps dripping—any quick fix?” | `issue_detection_agent` | Guides through shutting water, replacing washer/cartridge, or calling plumber. |

---

