"""CertChain - Blockchain-based academic certificate issuing & verification.
Run:  streamlit run app.py
"""
import copy
import time

import pandas as pd
import plotly.express as px
import streamlit as st

from blockchain import Block, Blockchain, certificate_id

st.set_page_config(page_title="CertChain", page_icon="⛓️", layout="wide")

SAMPLES = [
    ("Ananya Krishnan", "B.E. Computer Science", "Demo Institute of Technology", "2025-06-12", "A+"),
    ("Rohit Menon", "Certified Data Analyst", "Pantech e-Learning", "2025-08-02", "Distinction"),
    ("Fathima Begum", "Blockchain Developer Bootcamp", "Pantech e-Learning", "2025-09-15", "A"),
    ("Vignesh R", "M.Tech AI & Data Science", "Sample University", "2025-07-20", "A+"),
    ("Divya Prakash", "Cybersecurity Essentials", "Pantech e-Learning", "2025-10-01", "Merit"),
]

if "bc" not in st.session_state:
    bc = Blockchain(difficulty=3)
    for i, (n, c, inst, d, g) in enumerate(SAMPLES):
        bc.add_certificate(name=n, course=c, institution=inst, issue_date=d, grade=g)
        if i % 2 == 1 or i == len(SAMPLES) - 1:
            bc.mine_pending()
    st.session_state.bc = bc
bc: Blockchain = st.session_state.bc

st.markdown("<h1 style='margin-bottom:0'>⛓️ CertChain — Tamper-proof Certificates</h1>"
            "<p style='color:#888'>SHA-256 · Merkle trees · Proof-of-Work — issue and instantly verify academic credentials (sample demo data)</p>",
            unsafe_allow_html=True)

valid = bc.validate()
m = st.columns(5)
m[0].metric("Blocks", len(bc.chain))
m[1].metric("Certificates", sum(len(b.certificates) for b in bc.chain[1:]))
m[2].metric("Difficulty", bc.difficulty)
m[3].metric("Pending", len(bc.pending))
m[4].metric("Chain integrity", "✅ Valid" if all(v[1] for v in valid) else "❌ Tampered")

tab_ex, tab_issue, tab_verify, tab_attack = st.tabs(["🔗 Explorer", "📝 Issue", "🔍 Verify", "🧨 Tamper demo"])

with tab_ex:
    cols = st.columns(min(len(bc.chain), 5))
    for col, b in zip(cols, bc.chain[-5:]):
        ok = valid[b.index][1]
        color = "#39D98A" if ok else "#FF416C"
        col.markdown(f"""
<div style="border:2px solid {color};border-radius:12px;padding:12px;background:#141826;font-size:13px">
<b style="color:{color}">Block #{b.index}</b><br>
<span style="color:#888">certs:</span> {len(b.certificates)} · <span style="color:#888">nonce:</span> {b.nonce:,}<br>
<span style="color:#888">hash</span><br><code style="font-size:11px">{b.hash[:20]}…</code><br>
<span style="color:#888">prev</span><br><code style="font-size:11px">{b.previous_hash[:20]}…</code><br>
<span style="color:#888">merkle</span><br><code style="font-size:11px">{b.merkle[:20]}…</code>
</div>""", unsafe_allow_html=True)
    rows = [{"block": b.index, **{k: v for k, v in c.items() if k != "cert_id"}, "cert_id": c["cert_id"][:16] + "…"}
            for b in bc.chain[1:] for c in b.certificates]
    st.subheader("📜 Certificate ledger")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        df = pd.DataFrame([{"block": b.index, "nonce": b.nonce, "seconds": b.mine_seconds} for b in bc.chain])
        fig = px.bar(df, x="block", y="nonce", color="seconds", color_continuous_scale="Plasma", title="Proof-of-work effort per block")
        fig.update_layout(height=280, margin=dict(t=40, b=10))
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.download_button("⬇️ Export chain (JSON)", bc.to_json(), "certchain.json", width="stretch")
        up = st.file_uploader("Import chain JSON", type="json")
        if up:
            st.session_state.bc = Blockchain.from_json(up.read().decode())
            st.rerun()

with tab_issue:
    with st.form("issue"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Student name")
        course = c2.text_input("Course / degree")
        inst = c1.text_input("Institution", "Pantech e-Learning")
        date = c2.date_input("Issue date")
        grade = c1.selectbox("Grade", ["A+", "A", "Distinction", "Merit", "Pass"])
        diff = c2.slider("Mining difficulty", 1, 5, bc.difficulty)
        if st.form_submit_button("⛏️ Issue & mine block") and name and course:
            bc.difficulty = diff
            cid = bc.add_certificate(name=name, course=course, institution=inst, issue_date=str(date), grade=grade)
            blk = bc.mine_pending()
            st.success(f"Certificate issued in block #{blk.index} (nonce {blk.nonce:,}, {blk.mine_seconds:.2f}s)")
            st.code(cid, language=None)

with tab_verify:
    mode = st.radio("Verify by", ["Certificate ID", "Certificate details"], horizontal=True)
    if mode == "Certificate ID":
        cid = st.text_input("Certificate ID (SHA-256)", bc.chain[1].certificates[0]["cert_id"])
    else:
        n, c, inst, d, g = SAMPLES[1]
        c1, c2 = st.columns(2)
        fields = dict(name=c1.text_input("Name", n), course=c2.text_input("Course", c),
                      institution=c1.text_input("Institution", inst), issue_date=c2.text_input("Issue date", d),
                      grade=c1.text_input("Grade", g))
        cid = certificate_id(fields)
    blk, cert = bc.find(cid.strip())
    if cert and valid[blk.index][1]:
        st.success(f"✅ AUTHENTIC — recorded in block #{blk.index}, chain verified.")
        st.json({k: v for k, v in cert.items()})
    elif cert:
        st.error(f"⚠️ Found in block #{blk.index}, but that block FAILED integrity checks.")
    else:
        st.error("❌ NOT FOUND — this certificate was never issued or its details were altered.")

with tab_attack:
    st.write("Simulate a forger editing a grade directly in the ledger — the hash chain exposes it instantly.")
    target = st.selectbox("Block to tamper", [b.index for b in bc.chain[1:]])
    if st.button("🧨 Change first grade in this block to 'A+ (forged)'"):
        bc.chain[target].certificates[0]["grade"] = "A+ (forged)"
        st.rerun()
    st.dataframe(pd.DataFrame([(i, "✅ Valid" if ok else "❌ Invalid", r) for i, ok, r in valid], columns=["block", "status", "reason"]), hide_index=True, width="stretch")
    if st.button("♻️ Reset demo chain"):
        del st.session_state["bc"]
        st.rerun()
