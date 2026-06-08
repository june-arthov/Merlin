# 🧙‍♂️ MERLIN-CLI (Tier-3 Sovereign Agent)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tier](https://img.shields.io/badge/Intelligence-Tier--3_Sovereign-gold.svg)](#)
[![Mode](https://img.shields.io/badge/Logic-Gray_Hat_%26_Ihsan-grey.svg)](#)

[English](#english) | [Bahasa Indonesia](#bahasa-indonesia)

---

## English

**MERLIN-CLI** is a high-level (Tier-3) autonomous agent framework designed for coding assistance, security auditing, and system orchestration. Built with a modular architecture inspired by `hermes-agent`, Merlin is capable of performing surgical operations on codebases, delegating tasks to sub-agents, and executing autonomous deployments.

### 🚀 Key Features
- **Surgical Precision**: Edits files using the `replace` tool (precise line replacement) instead of rewriting entire files.
- **Advanced Toolbelt**: Equipped with 20+ tactical tools (Grep, Glob, Docker, SSH, Web Search, etc.).
- **Skill System**: Dynamic support for `SKILL.md`. Merlin can instantly learn new expertise (Security, DevOps, OSINT).
- **Autonomous Execution (FIT)**: A *File-modify, Inspect, Test* loop that allows Merlin to self-correct errors.
- **Gray Hat Alignment**: Integrated with `MERLIN_MANIFESTO.md` to maintain integrity and ethics.

### 🛠 Installation
1. **Clone Repository**: `git clone https://github.com/june-arthov/Merlin.git`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Set API Key**:
   - Windows: `$env:OPENROUTER_API_KEY="your_key"`
   - Linux/macOS: `export OPENROUTER_API_KEY="your_key"`

### 📖 Usage
- **Interactive Mode**: `python main.py`
- **Direct Task**: `python main.py "Analyze this folder structure"`
- **Specific Model**: `python main.py "Fix bug" -m anthropic/claude-3.5-sonnet`

---

## Bahasa Indonesia

**MERLIN-CLI** adalah framework agen otonom tingkat tinggi (Tier-3) yang dirancang untuk asisten coding, audit keamanan, dan orkestrasi sistem. Dibangun dengan arsitektur modular yang terinspirasi dari `hermes-agent`, Merlin mampu melakukan operasi bedah pada codebase, delegasi tugas ke sub-agent, dan eksekusi deployment secara mandiri.

### 🚀 Fitur Utama
- **Surgical Precision**: Mengedit file menggunakan tool `replace` (hanya baris yang perlu), bukan menulis ulang seluruh file.
- **Advanced Toolbelt**: Dilengkapi dengan 20+ tool taktis (Grep, Glob, Docker, SSH, Web Search, dll).
- **Skill System**: Dukungan dinamis untuk `SKILL.md`. Merlin bisa belajar "pakar" baru (Security, DevOps, OSINT) secara instan.
- **Autonomous Execution (FIT)**: Loop *File-modify, Inspect, Test* yang memungkinkan Merlin memperbaiki error-nya sendiri.
- **Gray Hat Alignment**: Terintegrasi dengan `MERLIN_MANIFESTO.md` untuk menjaga integritas dan etika kerja.

### 🛠 Instalasi
1. **Clone Repository**: `git clone https://github.com/june-arthov/Merlin.git`
2. **Instal Dependensi**: `pip install -r requirements.txt`
3. **Set API Key**:
   - Windows (PowerShell): `$env:OPENROUTER_API_KEY="your_key"`
   - Linux/macOS: `export OPENROUTER_API_KEY="your_key"`

### 📖 Cara Penggunaan
- **Mode Interaktif**: `python main.py`
- **Tugas Langsung**: `python main.py "Analisa struktur folder ini"`
- **Model Spesifik**: `python main.py "Fix bug" -m anthropic/claude-3.5-sonnet`

---

## 🧪 Scenarios / Skenario
- **Security Audit**: `python main.py "Use security_audit skill to find hardcoded keys"`
- **Debugging**: `python main.py "Activate systematic_debugging for memory leaks"`
- **DevOps**: `python main.py "Deploy this app to Docker"`

---
**Crafted with Ihsan by [june-arthov](https://github.com/june-arthov)**
