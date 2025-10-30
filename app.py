import streamlit as st
import pandas as pd
import uuid
import os

# Importer les fonctions de génération
from matplotlib_chart import create_daily_chart_matplotlib, create_radar_chart, create_triangle_chart
from hrv_pdf import generate_hrv_report

# ---------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------
st.set_page_config(
    page_title="Rapport HRV ASM Natation",
    page_icon="💓",
    layout="wide"
)

st.title("💓 Générateur de rapport HRV")

# 📂 Dossier temporaire
TEMP_DIR = "./temp_chart"
os.makedirs(TEMP_DIR, exist_ok=True)

# ---------------------------
# EN-TÊTE : date et ajout de lignes
# ---------------------------
st.subheader("📅 Informations générales")
selected_date = st.date_input("Sélectionnez la date du rapport", format="DD/MM/YYYY")

st.markdown("---")

# ---------------------------
# SECTION : Données des athlètes (responsive + clés stables)
# ---------------------------
st.subheader("👥 Données des athlètes")

# Initialisation
if "athletes" not in st.session_state:
    st.session_state["athletes"] = []

# ✅ Fonction d’ajout
def add_athlete():
    st.session_state["athletes"].append({
        "id": str(uuid.uuid4()),  # identifiant stable !
        "Nom": "",
        "% Régénération": 0.0,
        "% Capacité Effort": 0.0,
        "% Réserve": 0.0,
        "FC Couché": 0,
        "FC Debout": 0,
        "Menstruation": False,
        "Recommandations": "OK",
        "Commentaires": ""
    })

# ✅ Fonction de suppression différée
def request_delete(a_id: str):
    print(f"🗑️ Bouton suppression cliqué pour ID={a_id}")
    st.session_state["to_delete_id"] = a_id

# CSS
st.markdown("""
<style>
/* 🌟 Troncature automatique pour TOUS les labels Streamlit */
[data-testid="stWidgetLabel"] p {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
    max-width: 100%;
}

/* 🌟 Checkbox : label au-dessus de la case, centré et tronqué si trop long */
div[data-testid="stCheckbox"] label {
    display: flex !important;
    flex-direction: column-reverse !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.7rem !important;
    text-align: center !important;
}

/* 🌟 Centrer le bouton 🗑️ dans sa colonne */
div[data-testid="stButton"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 100% !important;         /* occupe toute la hauteur du conteneur */
}
</style>
""", unsafe_allow_html=True)

# Bouton ajout
if st.button("➕ Ajouter un athlète"):
    add_athlete()

# Aucun athlète
if len(st.session_state["athletes"]) == 0:
    st.info("Ajoutez un athlète pour commencer 👇")

# Colonnes
else:
    col_widths = [1.5,1,1,1,1,1,1,1,2,1]
    for athlete in st.session_state["athletes"]:
        a_id = athlete["id"]

        with st.container(border=True):
            (
                c_nom, c_regen, c_effort, c_reserve,
                c_fc_c, c_fc_d, c_mens, c_reco,
                c_comment, c_del
            ) = st.columns(col_widths)

            with c_nom:
                athlete["Nom"] = st.text_input("Nom", value=athlete["Nom"], key=f"nom_{a_id}")
            with c_regen:
                athlete["% Régénération"] = st.number_input("% Régénération", 0, 200,
                                                            int(athlete["% Régénération"]), step=1, key=f"regen_{a_id}")
            with c_effort:
                athlete["% Capacité Effort"] = st.number_input("% Capacité Effort", 0, 200, 
                                                               int(athlete["% Capacité Effort"]), step=1, key=f"effort_{a_id}")
            with c_reserve:
                athlete["% Réserve"] = st.number_input("% Réserve", 0, 200,
                                                       int(athlete["% Réserve"]), step=1, key=f"reserve_{a_id}")
            with c_fc_c:
                athlete["FC Couché"] = st.number_input("FC Couché", 0, 300,
                                                       int(athlete["FC Couché"]), key=f"fc_couche_{a_id}")
            with c_fc_d:
                athlete["FC Debout"] = st.number_input("FC Debout", 0, 300,
                                                       int(athlete["FC Debout"]), key=f"fc_debout_{a_id}")
            with c_mens:
                athlete["Menstruation"] = st.checkbox("Menstruation",
                                                      value=bool(athlete["Menstruation"]), key=f"mens_{a_id}")
            with c_reco:
                athlete["Recommandations"] = st.selectbox("Recommandations",
                                                          ["OK", "Vigilance", "Danger"],
                                                          index=["OK","Vigilance","Danger"].index(athlete["Recommandations"]),
                                                          key=f"reco_{a_id}")
            with c_comment:
                athlete["Commentaires"] = st.text_area("Commentaires",
                                                       value=athlete["Commentaires"], height=40, key=f"comment_{a_id}")
            with c_del:
                st.button("🗑️", key=f"delete_{a_id}", help="Supprimer cet athlète",
                          on_click=request_delete, args=(a_id,))

        st.markdown("")

# ✅ Suppression propre après le rendu
if "to_delete_id" in st.session_state:
    del_id = st.session_state.pop("to_delete_id")
    print(f"Index à supprimer (via ID): {del_id}")
    st.session_state["athletes"] = [a for a in st.session_state["athletes"] if a["id"] != del_id]
    print("Liste APRÈS suppression :", [a["Nom"] for a in st.session_state["athletes"]])
    st.rerun()

# DataFrame final
df_athletes = pd.DataFrame([{k: v for k, v in a.items() if k != "id"} for a in st.session_state["athletes"]])

# ---------------------------
# ACCORDÉON : Paramètres de référence
# ---------------------------
with st.expander("⚙️ Paramètres de référence", expanded=True):
    st.markdown("Ajustez les seuils pour chaque athlète 👇")

    # Liste des athlètes actuellement saisis
    athlete_names = [a["Nom"].strip() for a in st.session_state["athletes"] if a["Nom"].strip()]

    # Table de base (seuils communs)
    base_reference = pd.DataFrame({
        "Niveau": ["Moyenne", "DANGER", "VIGILANCE", "CORRECT", "OK"],
        "% Capacité Effort": [100, 40, 80, 120, 150],
        "% Réserve": [100, 40, 80, 120, 150],
        "% Régénération": [100, 40, 80, 120, 150],
        "FC Couché": [61, 40, 80, 120, 150],
        "FC Debout": [90, 40, 80, 120, 150],
    })

    # Seuils individuels connus
    default_fc = {
        "gaetane": {"FC Couché": 60, "FC Debout": 85},
        "marius": {"FC Couché": 56, "FC Debout": 105},
        "lili rose": {"FC Couché": 61, "FC Debout": 97},
        "alicia": {"FC Couché": 61, "FC Debout": 90},
    }

    if not athlete_names:
        st.info("Ajoutez d’abord des athlètes pour personnaliser les lignes Moyenne.")
        st.session_state["reference_table"] = base_reference.copy()
    else:
        # --- 1️⃣ Créer les lignes "Nom Moyenne" pour chaque athlète
        moyenne_rows = []
        for nom in athlete_names:
            nom_clean = nom.strip()
            nom_lower = nom_clean.lower()

            row = {
                "Niveau": f"{nom_clean} Moyenne",
                "% Capacité Effort": 100,
                "% Réserve": 100,
                "% Régénération": 100,
                "FC Couché": 61,
                "FC Debout": 90,
            }

            # Appliquer valeurs FC personnalisées connues
            if nom_lower in default_fc:
                row["FC Couché"] = default_fc[nom_lower]["FC Couché"]
                row["FC Debout"] = default_fc[nom_lower]["FC Debout"]

            moyenne_rows.append(row)

        df_moyennes = pd.DataFrame(moyenne_rows)

        # --- 2️⃣ Ajouter les lignes seuils globales une seule fois
        df_seuils = base_reference.loc[base_reference["Niveau"].isin(["DANGER", "VIGILANCE", "CORRECT", "OK"])]

        # --- 3️⃣ Fusion finale : toutes les moyennes en haut, seuils en bas
        full_ref = pd.concat([df_moyennes, df_seuils], ignore_index=True)

        # Sauvegarde dans la session
        st.session_state["reference_table"] = full_ref.copy()

    # --- 4️⃣ Affichage éditable
    edited_reference = st.data_editor(
        st.session_state["reference_table"],
        width="stretch",
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "Niveau": st.column_config.TextColumn("Niveau"),
        }
    )

    # --- 5️⃣ Mettre à jour la session
    st.session_state["reference_table"] = edited_reference

st.markdown("---")

# ---------------------------
# BOUTON GÉNÉRATION PDF
# ---------------------------

if st.button("📄 Générer le rapport PDF"):
    if len(st.session_state["athletes"]) == 0:
        st.warning("⚠️ Ajoutez au moins un athlète avant de générer le rapport.")
    else:
        with st.spinner("⏳ Génération du rapport en cours..."):
            # 1️⃣ Charger les données nécessaires
            report_date = selected_date
            df_ref = st.session_state["reference_table"].set_index("Niveau")

            # 2️⃣ Créer le graphique global (daily chart)
            daily_chart_path = create_daily_chart_matplotlib(
                df=df_athletes,
                save_path=f"{TEMP_DIR}/daily_chart_matplotlib.png"
            )

            # 3️⃣ Créer les graphiques individuels pour chaque athlète
            for athlete in st.session_state["athletes"]:
                nom_safe = athlete["Nom"].replace(" ", "_") or "athlete"
                radar_path = f"{TEMP_DIR}/radar_{nom_safe}.png"
                tri_path = f"{TEMP_DIR}/triangle_{nom_safe}.png"

                athlete["chart_left"] = create_radar_chart(
                    athlete_data=athlete,
                    reference_df=df_ref,
                    save_path=radar_path
                )
                athlete["chart_right"] = create_triangle_chart(
                    athlete_data=athlete,
                    reference_df=df_ref,
                    save_path=tri_path
                )

            # 4️⃣ Génération du PDF final
            pdf_path = f"{TEMP_DIR}/rapport_hrv_{report_date}.pdf"
            generate_hrv_report(
                output_pdf_path=pdf_path,
                report_date=report_date,
                athletes=st.session_state["athletes"],
                left_logo_path="./icons/Logo_ASM_Clermont_Auvergne_2019.png",
                right_logo_path="./icons/Elite-logo-dark.png",
                daily_chart_path=daily_chart_path,
                legend_icons={
                    "menstruation": "./icons/menstruation.png",
                    "ok": "./icons/ok.png",
                    "vigilance": "./icons/vigilance.png",
                    "danger": "./icons/danger.png",
                },
            )

        # 5️⃣ Proposer le téléchargement
        with open(pdf_path, "rb") as f:
            st.success("✅ Rapport généré avec succès !")
            st.download_button(
                label="📥 Télécharger le rapport HRV",
                data=f,
                file_name=f"Rapport_HRV_ASM_{report_date.strftime('%d-%m-%Y')}.pdf",
                mime="application/pdf"
            )