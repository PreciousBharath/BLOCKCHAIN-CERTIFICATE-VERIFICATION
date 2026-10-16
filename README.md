<div align="center">

# ⛓️ CertChain — Blockchain Certificate Verification

**Issue academic certificates on a proof-of-work blockchain and verify them instantly — any tampering is exposed.**

![Python-3.10%2B](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Streamlit-App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) ![Plotly-Charts](https://img.shields.io/badge/Plotly-Charts-3F4F75?style=for-the-badge&logo=plotly&logoColor=white) ![Blockchain-SHA--256](https://img.shields.io/badge/Blockchain-SHA--256-121D33?style=for-the-badge&logo=ethereum&logoColor=white) ![Crypto-Merkle%20Tree](https://img.shields.io/badge/Crypto-Merkle%20Tree-6C47FF?style=for-the-badge&logo=bitcoin&logoColor=white)

`Blockchain · Cryptography`

</div>

---

![BLOCKCHAIN-CERTIFICATE-VERIFICATION](assets/screenshot.png)

## 📌 Problem Statement

Fake degree certificates are a growing problem for employers and universities. Manual verification is slow and email-based.

## ✨ Key Features

- Blockchain built **from scratch**: SHA-256, Merkle root, proof-of-work mining with adjustable difficulty
- **Issue** certificates → deterministic certificate ID (hash of canonical JSON)
- **Verify** by certificate ID or by re-entering details
- **Tamper demo**: edit a grade and watch the integrity check fail
- Block explorer cards, certificate ledger and PoW effort chart
- Export / import the chain as JSON

## 🏗️ Architecture

```mermaid
flowchart LR
    A[Certificate Details] --> B[SHA-256 cert_id]
    B --> C[Merkle Root]
    C --> D[Block Header]
    D --> E[Proof-of-Work Mining]
    E --> F[(Blockchain)]
    V[Verifier] --> F
    F --> G{Hashes valid?}
```

## ⚙️ How It Works

1. Each certificate is hashed into a `cert_id`; a block stores certificates plus their **Merkle root**.
2. Mining increments a nonce until the block hash starts with *difficulty* zeros.
3. Every block stores the previous block's hash — changing any byte breaks the Merkle root, the block hash and all following links.
4. Validation re-computes all hashes and reports the exact block and reason for failure.

## 🖼️ More Screenshots

### Tamper detection
![Tamper detection](assets/tamper.png)

## 🧰 Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.10+ |
| ML / Logic | pandas |
| UI & Visualisation | Streamlit, Plotly |

## 📁 Project Structure

```
BLOCKCHAIN-CERTIFICATE-VERIFICATION/
├── app.py             # Streamlit UI — explorer, issue, verify, tamper demo
├── blockchain.py      # Block, Blockchain, Merkle tree, PoW, validation, JSON persistence
├── assets/              # screenshots
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

```bash
git clone https://github.com/PreciousBharath/BLOCKCHAIN-CERTIFICATE-VERIFICATION.git
cd BLOCKCHAIN-CERTIFICATE-VERIFICATION
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

> The project ships with a realistic built-in demo dataset, so it runs out of the box with no downloads or API keys.

## 🗺️ Roadmap

- [ ] Deploy as an Ethereum / Polygon smart contract
- [ ] QR code on certificates for mobile verification
- [ ] Digital signatures (ECDSA) for issuers

## 👨‍💻 Author

**Bharath** — Software Developer · Project Engineer · Technical Trainer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-connectbharath-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/connectbharath)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)](https://itsbharathportfolio.netlify.app)
[![GitHub](https://img.shields.io/badge/GitHub-PreciousBharath-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/PreciousBharath)

⭐ If this project helped you, please give it a star!

## 📄 License

Released under the [MIT License](LICENSE).
