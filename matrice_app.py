"""
Application Streamlit — Matrice des zones partagées entre clients
Visualisation interactive des départements en commun
"""

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
        font-weight: bold; border-radius: 8px;
        border: none; padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { background-color: #74c7ec; }
    label { color: #cdd6f4 !important; }
    .stTextInput input { background-color: #181825 !important; color: #cdd6f4 !important; }
    .stNumberInput input { background-color: #181825 !important; color: #cdd6f4 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

if "clients" not in st.session_state:
    st.session_state.clients = [
        {"nom": "Client_HA2",       "prefixes": ["71","58","89","21","39","70","25","90"]},
        {"nom": "Client_RR",        "prefixes": ["28","61","53","35","44","49","72","37","86","79","85","36","18","41","45"]},
        {"nom": "Client_AI",        "prefixes": ["22","35","56","72","53"]},
        {"nom": "Client_AV3",       "prefixes": ["28","45","27","76","58","89","60","80","02","57","54","88","53","72"]},
        {"nom": "Client_ZZ7",       "prefixes": ["26","07","38","84","13"]},
        {"nom": "Client_ZZ8",       "prefixes": ["15","63","43","03"]},
        {"nom": "Client_SH",        "prefixes": ["54","55","57","88","51","52","10"]},
        {"nom": "Client_AV1",       "prefixes": ["67","68","88"]},
        {"nom": "Client_AV2",       "prefixes": ["57","54","70","88","90","67","68"]},
        {"nom": "Client_RN_GLOBAL", "prefixes": ["24","47","66","11","09","64","65","87","23","19"]},
        {"nom": "Client_RN2",       "prefixes": ["66","11","09"]}
    ]

# ─────────────────────────────────────────────
# TITRE
# ─────────────────────────────────────────────

st.title("🗺️ Matrice des Zones Clients")
st.markdown("**Visualisation des départements partagés entre clients**")
st.divider()

# ─────────────────────────────────────────────
# GESTION DES CLIENTS
# ─────────────────────────────────────────────

st.header("① Gérer les clients")

col_gauche, col_droite = st.columns([1, 2])

with col_gauche:
    st.subheader("Ajouter un client")
    nouveau_nom = st.text_input("Nom du client", placeholder="Ex : Client_XX", key="new_nom")
    nouveaux_deps = st.text_input(
        "Départements (séparés par des virgules)",
        placeholder="Ex : 75, 92, 93, 94",
        key="new_deps"
    )

    if st.button("➕ Ajouter"):
        if nouveau_nom.strip() and nouveaux_deps.strip():
            noms_existants = [c["nom"] for c in st.session_state.clients]
            if nouveau_nom.strip() in noms_existants:
                st.error(f"❌ '{nouveau_nom}' existe déjà.")
            else:
                prefixes = [d.strip().zfill(2) for d in nouveaux_deps.split(",") if d.strip()]
                st.session_state.clients.append({"nom": nouveau_nom.strip(), "prefixes": prefixes})
                st.success(f"✅ {nouveau_nom} ajouté avec {len(prefixes)} département(s).")
                st.rerun()
        else:
            st.warning("⚠️ Remplis le nom et les départements.")

    st.divider()
    st.subheader("Supprimer un client")
    noms = [c["nom"] for c in st.session_state.clients]
    client_a_supprimer = st.selectbox("Choisir un client", ["— Sélectionner —"] + noms)
    if st.button("🗑️ Supprimer") and client_a_supprimer != "— Sélectionner —":
        st.session_state.clients = [c for c in st.session_state.clients if c["nom"] != client_a_supprimer]
        st.success(f"✅ {client_a_supprimer} supprimé.")
        st.rerun()

    st.divider()
    st.subheader("Modifier un client")
    client_a_modifier = st.selectbox("Choisir un client à modifier", ["— Sélectionner —"] + noms, key="modif_select")
    if client_a_modifier != "— Sélectionner —":
        client_obj = next(c for c in st.session_state.clients if c["nom"] == client_a_modifier)
        deps_actuels = ", ".join(client_obj["prefixes"])
        nouveaux_deps_modif = st.text_input("Nouveaux départements", value=deps_actuels, key="modif_deps")
        if st.button("💾 Enregistrer"):
            prefixes = [d.strip().zfill(2) for d in nouveaux_deps_modif.split(",") if d.strip()]
            client_obj["prefixes"] = prefixes
            st.success(f"✅ {client_a_modifier} mis à jour.")
            st.rerun()

with col_droite:
    st.subheader("Clients configurés")
    for client in st.session_state.clients:
        deps_str = ", ".join(sorted(client["prefixes"]))
        st.markdown(f"**{client['nom']}** ({len(client['prefixes'])} dép.) → `{deps_str}`")

st.divider()

# ─────────────────────────────────────────────
# MATRICE
# ─────────────────────────────────────────────

st.header("② Matrice des zones partagées")

clients = st.session_state.clients
if len(clients) < 2:
    st.warning("⚠️ Ajoute au moins 2 clients pour afficher la matrice.")
else:
    noms = [c["nom"] for c in clients]
    prefixes_par_client = {c["nom"]: set(c["prefixes"]) for c in clients}

    # Construction matrice
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
            return "background-color: #1e1e2e; color: #1e1e2e;"
        else:
            return "background-color: #f38ba8; color: #1e1e2e; font-weight: bold; text-align: center;"

    try:
        styled = df_matrice.style.map(colorier)
    except AttributeError:
        styled = df_matrice.style.applymap(colorier)

    st.dataframe(styled, use_container_width=True)

    st.divider()

    # ─────────────────────────────────────────────
    # RÉCAPITULATIF ZONES PARTAGÉES
    # ─────────────────────────────────────────────

    st.header("③ Récapitulatif des zones partagées")

    prefix_clients = {}
    for client in clients:
        for prefix in client["prefixes"]:
            prefix_clients.setdefault(prefix, []).append(client["nom"])

    zones_partagees = {p: noms_c for p, noms_c in prefix_clients.items() if len(noms_c) > 1}

    if zones_partagees:
        col1, col2 = st.columns(2)
        col1.metric("Départements partagés", len(zones_partagees))
        col2.metric("Départements exclusifs", sum(len(c["prefixes"]) for c in clients) - len(zones_partagees) * 2)

        rows = []
        for prefix, noms_c in sorted(zones_partagees.items()):
            rows.append({
                "Département": prefix,
                "Nb clients": len(noms_c),
                "Clients concernés": " / ".join(noms_c)
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.divider()

        # Vue par client
        st.subheader("Vue par client")
        for client in clients:
            zones_client = [p for p in client["prefixes"] if p in zones_partagees]
            if zones_client:
                with st.expander(f"🔵 {client['nom']} — {len(zones_client)} zone(s) partagée(s)"):
                    for z in sorted(zones_client):
                        autres = [n for n in zones_partagees[z] if n != client["nom"]]
                        st.markdown(f"• Département **{z}** → partagé avec : **{', '.join(autres)}**")
    else:
        st.success("✅ Aucune zone partagée — chaque département est exclusif à un seul client !")
