# 🧙‍♂️ MERLIN-CLI (Tier-3 Sovereign Agent)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tier](https://img.shields.io/badge/Intelligence-Tier--3_Sovereign-gold.svg)](#)
[![Mode](https://img.shields.io/badge/Logic-Gray_Hat_%26_Ihsan-grey.svg)](#)

**MERLIN-CLI** adalah framework agen otonom tingkat tinggi (Tier-3) yang dirancang untuk asisten coding, audit keamanan, dan orkestrasi sistem. Dibangun dengan arsitektur modular yang terinspirasi dari `hermes-agent`, Merlin mampu melakukan operasi bedah pada codebase, delegasi tugas ke sub-agent, dan eksekusi deployment secara mandiri.

---

## 🚀 Fitur Utama (Tier-3 Powers)

- **Surgical Precision**: Mengedit file menggunakan tool `replace` (hanya baris yang perlu), bukan menulis ulang seluruh file.
- **Advanced Toolbelt**: Dilengkapi dengan 20+ tool taktis (Grep, Glob, Docker, SSH, Web Search, dll).
- **Skill System**: Dukungan dinamis untuk `SKILL.md`. Merlin bisa belajar "pakar" baru (Security, DevOps, OSINT) secara instan.
- **Autonomous Execution (FIT)**: Loop *File-modify, Inspect, Test* yang memungkinkan Merlin memperbaiki error-nya sendiri.
- **Gray Hat Alignment**: Terintegrasi dengan `MERLIN_MANIFESTO.md` untuk menjaga integritas dan etika kerja.
- **Rich UI**: Tampilan terminal yang intuitif dengan progress tracking, panel tugas, dan format markdown.

---

## 🛠 Instalasi

### 1. Prasyarat
Pastikan kamu sudah menginstal **Python 3.10+** dan **pip**.

### 2. Clone Repository
```bash
git clone https://github.com/june-arthov/Merlin.git
cd Merlin
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

---

## 🔑 Konfigurasi API

Merlin menggunakan **OpenRouter** sebagai otak utamanya (kompatibel dengan DeepSeek, Claude, GPT-4, dll).

**Linux/WSL/macOS:**
```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**
```bash
$env:OPENROUTER_API_KEY="your_api_key_here"
```

---

## 📖 Cara Penggunaan

### 1. Mode Interaktif
Jalankan tanpa argumen untuk masuk ke prompt Merlin:
```bash
python main.py
```

### 2. Tugas Langsung (Direct Task)
Berikan tugas spesifik lewat argumen:
```bash
python main.py "Analisa struktur folder ini dan buat laporan di README_INTERNAL.md"
```

### 3. Menggunakan Model Spesifik
Default menggunakan `deepseek-coder-v2-lite`. Kamu bisa menggantinya:
```bash
python main.py "Fix bug di auth.py" -m anthropic/claude-3.5-sonnet
```

---

## 🧪 Contoh Skenario

### Debugging Sistematik
```bash
python main.py "Aktifkan skill systematic_debugging untuk mencari penyebab memory leak di server.py"
```

### Security Audit
```bash
python main.py "Gunakan skill security_audit pada folder src/ untuk mencari hardcoded credentials"
```

### Autonomous Deployment
```bash
python main.py "Build aplikasi ini ke Docker container dan deploy ke VPS merlin-prod"
```

---

## 🏗 Arsitektur Folder
- `merlin/core/`: Mesin utama (Engine, Prompts, Skill Loader).
- `merlin/tools/`: Koleksi tool taktis (File Ops, Search, Web, Deploy).
- `.merlin/skills/`: Kumpulan instruksi pakar (SKILL.md).
- `tests/`: Unit testing untuk kestabilan framework.

---

## ⚖ Lisensi
Didistribusikan di bawah **Apache License 2.0**. Lihat file `LICENSE` untuk informasi lebih lanjut.

---
**Crafted with Ihsan by [june-arthov](https://github.com/june-arthov)**
