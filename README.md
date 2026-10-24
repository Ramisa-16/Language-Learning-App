<h1 align="center">🗣️ Language Learning App</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT-412991?style=for-the-badge&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/TTS%20%2F%20STT-Audio%20AI-00b39e?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

<p align="center">
  An AI-powered language learning app with <strong>text-to-text</strong> and <strong>audio-to-audio</strong> conversation modes,
  real-time grammar correction, mistake tracking, and tiered free/premium plans.
</p>

---

## ✨ Features

### 🆓 Free Plan
| Feature | Description |
|---|---|
| 💬 Text-to-Text Chat | Practice writing by chatting with the AI tutor |
| 🎙️ Audio-to-Audio | Speak with the AI — full conversation shown as text |
| 🎯 Goal Tracking | Set daily learning time goal and track progress |
| ⏱️ Usage Limit | 25 messages per 24 hours |

### 💎 Premium Plan
| Feature | Description |
|---|---|
| ✅ Real-time Grammar Correction | Sentence structure feedback while chatting |
| 🔴🟢 Mistake Tracking | Errors in **red**, corrections in **green** |
| 📊 Full Review | Complete corrected conversation after each session |
| 🎓 Level Selection | Beginner / Intermediate / Advanced |
| ⏰ Flexible Goals | 15 / 30 / 45 / 60 min daily targets |

---

## 🏗️ Architecture

```
User Input (text or audio)
        │
        ▼
┌─────────────────┐
│  Speech-to-Text │  ← audio mode only
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│  LLM (OpenAI GPT)        │  ← language tutor persona
│  + conversation memory   │
└────────┬─────────────────┘
         │
         ├──────────────────────────┐
         ▼                          ▼
┌─────────────────┐     ┌───────────────────────┐
│  Text Response  │     │  Grammar Analysis      │
│  (free + prem)  │     │  (premium only)        │
└─────────────────┘     └───────────────────────┘
         │
         ▼
┌─────────────────┐
│  Text-to-Speech │  ← audio mode only
└─────────────────┘
```

---

## 📁 Project Structure

```
Language-Learning-App/
├── main.py           # Entry point
├── audion.py         # Audio-to-audio conversation engine
├── tfree.py          # Free tier text conversation
├── tnew.py           # Premium text with grammar correction
├── vfree.py          # Free tier voice conversation
└── requirements.txt
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/Ramisa-16/Language-Learning-App.git
cd Language-Learning-App
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
python tfree.py          # text mode
python audion.py         # audio mode
```

---

## 🛠️ Tech Stack

- **Python 3.10+** · **OpenAI GPT** · **TTS/STT** · **PyAudio**

---

## 👩‍💻 Author

**Ramisa Sharar Nidhi** — AI Developer @ Betopia Group
[![LinkedIn](https://img.shields.io/badge/LinkedIn-ramisashararnidhi-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/ramisashararnidhi)
[![GitHub](https://img.shields.io/badge/GitHub-Ramisa--16-181717?style=flat&logo=github)](https://github.com/Ramisa-16)
