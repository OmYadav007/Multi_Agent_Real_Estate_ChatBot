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
2. Router sends a *mini* classification request to GPT‑4o‑mini. The request processes the given user input with the image and responds with which function to use 
3. GPT is being used as an agent to make the function call based on classfication result , so it calls either the issue_detection_agent or the tenancy_faq_agent
   


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
## 5. Local Setup — Step‑by‑Step
_Estimated time: ~10 minutes on a clean machine_

> The guide assumes **Windows / macOS / Linux** and a fresh **Miniconda** install.

### 5.1 Install Miniconda (if you don’t already have it)
1. Download the latest installer for your OS from <https://docs.conda.io/en/latest/miniconda.html>.
2. Run the installer → **keep default options** (adds `conda` to your PATH).
3. Open a new terminal / PowerShell window so `conda` is available.

### 5.2 Create & activate the project environment
```bash
# 1  Create env with Python 3.11
conda create -n realestate-chatbot python=3.11 -y

# 2  Activate it (run this every time you work on the project)
conda activate realestate-chatbot
```

### 5.3 Grab the code
```bash
# Clone or download the repo
git clone https://github.com/OmYadav007/Multi_Agent_Real_Estate_ChatBot.git
cd Multi_Agent_Real_Estate_ChatBot
```
### 5.4 Install Python dependencies
```bash
pip install -r requirements.txt
```
_`requirements.txt` already matches the libraries listed in section 1._

### 5.5 Add your Azure OpenAI credentials

2. Open `.env` in a text editor and fill in:
   ```dotenv
   AZURE_SUBSCRIPTION_KEY="your‑azure‑key‑here"
   ```
3. **Save** the file — `python‑dotenv` will load these at runtime.

### 5.6 Run the app
```bash
streamlit run app.py
```
* Your default browser opens to <http://localhost:8501>
* Chat with the bot, optionally upload images.

### 5.7 Troubleshooting
| Symptom | Quick fix |
|---------|-----------|
| **“Module X not found”** | Re‑check `pip install -r requirements.txt` ran inside the active conda env. |
| **“.env not found”** | Ensure the file exists in the project root and is named exactly `.env`. |
| **API quota exceeded** | You’re on Azure free tier—wait or raise limits in the portal. |

