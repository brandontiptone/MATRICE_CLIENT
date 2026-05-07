"""
Application Streamlit — Matrice des zones partagées entre clients
"""

import json
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Matrice Zones Clients",
    page_icon="🗺️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    h1, h2, h3 { color: #89b4fa; }
    .stButton > button {
        background-color: #89b4fa; color: #1e1e2e;
        font-weight: bold; border-radius: 8px; border: none;
        padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { background-color: #74c7ec; }
    label { color: #cdd6f4 !important; }
    .stTextInput input { background-color: #181825 !important; color: #cdd6f4 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

if "clients" not in st.session_state:
    st.session_state.clients = []

# ─────────────────────────────────────────────
# TITRE
# ─────────────────────────────────────────────

st.title("🗺️ Matrice des Zones Clients")
st.markdown("**Visualisation des départements partagés entre clients**")
st.divider()

# ─────────────────────────────────────────────
# AJOUTER UN CLIENT
# ─────────────────────────────────────────────

st.header("① Ajouter un client")

col1, col2, col3 = st.columns([2, 4, 1])
with col1:
    nouveau_nom = st.text_input("Nom du client", placeholder="Ex : Client_XX")
with col2:
    nouveaux_deps = st.text_input("Départements (séparés par des virgules)", placeholder="Ex : 75, 92, 93, 94")
with col3:
    st.write("")
    st.write("")
    ajouter = st.button("➕ Ajouter")

if ajouter:
    if not nouveau_nom.strip() or not nouveaux_deps.strip():
        st.error("❌ Remplis le nom et les départements.")
    elif nouveau_nom.strip() in [c["nom"] for c in st.session_state.clients]:
        st.error(f"❌ '{nouveau_nom}' existe déjà.")
    else:
        prefixes = [d.strip().zfill(2) for d in nouveaux_deps.split(",") if d.strip()]
        st.session_state.clients.append({"nom": nouveau_nom.strip(), "prefixes": prefixes})
        st.success(f"✅ {nouveau_nom} ajouté avec {len(prefixes)} département(s).")
        st.rerun()

st.divider()

# ─────────────────────────────────────────────
# LISTE DES CLIENTS
# ─────────────────────────────────────────────

st.header("② Clients configurés")

if not st.session_state.clients:
    st.info("Aucun client pour l'instant — ajoutez-en un ci-dessus.")
else:
    for i, client in enumerate(st.session_state.clients):
        col_a, col_b, col_c = st.columns([2, 6, 1])
        with col_a:
            st.markdown(f"**{client['nom']}** ({len(client['prefixes'])} dép.)")
        with col_b:
            st.markdown(f"`{', '.join(sorted(client['prefixes']))}`")
        with col_c:
            if st.button("🗑️", key=f"del_{i}", help=f"Supprimer {client['nom']}"):
                st.session_state.clients.pop(i)
                st.rerun()

st.divider()

# ─────────────────────────────────────────────
# MATRICE
# ─────────────────────────────────────────────

st.header("③ Matrice des zones partagées")

clients = st.session_state.clients

if len(clients) < 2:
    st.warning("⚠️ Ajoutez au moins 2 clients pour afficher la matrice.")
else:
    noms = [c["nom"] for c in clients]
    prefixes_par_client = {c["nom"]: set(c["prefixes"]) for c in clients}

    matrice = {}
    for c1 in noms:
        matrice[c1] = {}
        for c2 in noms:
            if c1 == c2:
                matrice[c1][c2] = "—"
            else:
                communs = sorted(prefixes_par_client[c1] & prefixes_par_client[c2])
                matrice[c1][c2] = ", ".join(communs) if communs else ""

    df_matrice = pd.DataFrame(matrice).T[noms]

    def colorier(val):
        if val == "—":
            return "background-color: #313244; color: #6c7086; text-align: center;"
        elif val == "":
            return "background-color: #1e1e2e;"
        else:
            return "background-color: #f38ba8; color: #1e1e2e; font-weight: bold; text-align: center;"

    try:
        styled = df_matrice.style.map(colorier)
    except AttributeError:
        styled = df_matrice.style.applymap(colorier)

    st.dataframe(styled, use_container_width=True)

    st.divider()

    # ─────────────────────────────────────────────
    # RÉCAPITULATIF
    # ─────────────────────────────────────────────

    st.header("④ Récapitulatif des zones partagées")

    prefix_clients = {}
    for client in clients:
        for prefix in client["prefixes"]:
            prefix_clients.setdefault(prefix, []).append(client["nom"])

    zones_partagees = {p: n for p, n in prefix_clients.items() if len(n) > 1}
    total_deps = len(set(p for c in clients for p in c["prefixes"]))

    col1, col2, col3 = st.columns(3)
    col1.metric("Clients", len(clients))
    col2.metric("Départements uniques", total_deps)
    col3.metric("Zones partagées", len(zones_partagees))

    if zones_partagees:
        rows = []
        for prefix, noms_c in sorted(zones_partagees.items()):
            rows.append({
                "Département": prefix,
                "Nb clients": len(noms_c),
                "Clients concernés": " / ".join(noms_c)
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.success("✅ Aucune zone partagée — chaque département est exclusif à un seul client !")

    st.divider()

    # Export config JSON
    st.subheader("Export configuration")
    config_export = json.dumps({"clients": clients}, indent=2, ensure_ascii=False)
    st.download_button(
        label="⬇️ Télécharger la config JSON",
        data=config_export.encode("utf-8"),
        file_name="clients_config.json",
        mime="application/json"
    )
    st.caption("Tu peux réimporter cette config dans l'app de traitement des leads.")
