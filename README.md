# 🤖 Qurrat-AI — Personal AI Employee
> **Your autonomous FTE managing the vault while you sleep.**

---

## 🌟 What is Qurrat-AI?
Qurrat-AI is a specialized autonomous agent designed to manage a digital "AI Employee Vault." It functions as a tireless personal assistant, monitoring incoming data, orchestrating complex workflows, and providing executive-level briefings to ensure Syeda Qurrat's operations remain seamless and organized.

## 🚀 Features Built
*   **📂 File System Watcher:** A reactive service that monitors the `Inbox` in real-time, automatically routing new inputs to `Needs_Action` for processing.
*   **🧠 Orchestrator:** The master control unit that synchronizes vault operations and refreshes the `Dashboard.md` every 60 seconds for 100% visibility.
*   **📅 CEO Monday Briefing:** An automated reporting system that synthesizes weekly activity into a strategic briefing every Monday at 8:00 AM via cron.
*   **📜 GEMINI.md Agent Skills:** A core operational manual defining the AI's identity, behavioral mandates, and strict governance rules.
*   **⚖️ Human-in-the-Loop:** A robust safety protocol utilizing the `Pending_Approval` folder for sensitive actions requiring human oversight.

## 🛠️ Tech Stack
| Component | Technology |
| :--- | :--- |
| **AI Engine** | Gemini CLI (Advanced Orchestration) |
| **Logic Layer** | Python 3.x |
| **Monitoring** | Python Watchdog API |
| **Scheduling** | Linux Cron Jobs |
| **Interface** | Obsidian / VS Code |
| **Environment** | Ubuntu / WSL |

## 📁 Folder Structure
```text
AI_Employee_Vault/
├── Business_Goals.md       # Strategic objectives
├── Dashboard.md            # Real-time status report
├── GEMINI.md               # AI Identity & Rules
├── ceo_briefing.py         # Briefing generator script
├── file_watcher.py         # Inbox monitoring service
├── orchestrator.py         # Main controller script
├── Briefings/              # Generated executive reports
├── Inbox/                  # Entry point for new data
├── Needs_Action/           # Tasks awaiting AI processing
├── Pending_Approval/       # Sensitive tasks for human review
├── Done/                   # Successfully completed items
└── Logs/                   # Audit trails & activity history
```

## ⚡ How to Run
To initialize your AI Employee, execute these commands in your terminal:

1. **Start the Master Orchestrator:**
   ```bash
   python3 orchestrator.py
   ```
2. **Launch the File Watcher:**
   ```bash
   python3 file_watcher.py
   ```
3. **Initialize Scheduled Tasks:**
   ```bash
   crontab -l | { cat; echo "0 8 * * 1 /usr/bin/python3 $(pwd)/ceo_briefing.py"; } | crontab -
   ```

## 🏆 Hackathon Status
*   **🥉 Bronze Tier:** ✅ Complete
*   **🥈 Silver Tier:** 🏗️ In Progress
*   **🥇 Gold Tier:** 📅 Planned

## 📺 Demo
[Link to Video Demo Placeholder]

---
*Built with **Gemini CLI** — 100% of the code for this project was generated and orchestrated by AI.*
