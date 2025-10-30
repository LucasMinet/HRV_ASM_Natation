import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.cm import get_cmap
from matplotlib.patches import Polygon
import numpy as np

def create_daily_chart_matplotlib(
    df: pd.DataFrame,
    save_path: str = "./temp_chart/daily_chart_matplotlib.png",
    figsize=(8, 7)
):
    """
    Crée un graphique quotidien (régénération vs capacité d’effort)
    à partir d’un DataFrame déjà chargé en mémoire.

    Le DataFrame doit contenir :
        - 'Nageur'
        - '% régénération'
        - '% capacité d'effort'
        - '% réserve'
    """

    # --- Vérification des colonnes requises
    required_cols = ["Nom", "% Régénération", "% Capacité Effort", "% Réserve"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le DataFrame : {missing}")

    # --- Définir les nageurs et couleurs
    nageurs = df["Nom"].unique()
    cmap = get_cmap("Set1")
    colors = [cmap(i) for i in range(len(nageurs))]

    # --- Créer la figure
    fig, ax = plt.subplots(figsize=figsize)

    # === Couleurs de fond ===
    def add_rect(x0, x1, y0, y1, color, alpha=0.3):
        ax.add_patch(
            patches.Rectangle(
                (x0, y0), x1 - x0, y1 - y0,
                facecolor=color, alpha=alpha, linewidth=0
            )
        )

    # 🔴 Rouge (0-30%)
    add_rect(0, 30, 0, 30, "red", 0.3)

    # 🟠 Orange (zones vigilance)
    add_rect(30, 100, 0, 30, "orange", 0.3)
    add_rect(0, 30, 30, 100, "orange", 0.3)
    add_rect(30, 60, 30, 60, "orange", 0.3)

    # 🟡 Jaune (zones correctes)
    add_rect(0, 30, 100, 200, "yellow", 0.3)
    add_rect(30, 60, 60, 120, "yellow", 0.3)
    add_rect(60, 120, 30, 60, "yellow", 0.3)
    add_rect(100, 200, 0, 30, "yellow", 0.3)
    add_rect(60, 90, 60, 90, "yellow", 0.3)

    # 🟢 Vert (zones supérieures)
    add_rect(90, 200, 120, 200, "green", 0.1)
    add_rect(120, 200, 90, 200, "green", 0.1)

    # 🔵 Bleu (zones très hautes)
    add_rect(80, 120, 150, 200, "blue", 0.1)
    add_rect(150, 200, 80, 120, "blue", 0.1)

    # === Tracer les points par nageur ===
    for i, nageur in enumerate(nageurs):
        sub = df[df["Nom"] == nageur]
        ax.scatter(
            sub["% Capacité Effort"],
            sub["% Régénération"],
            s=400,              # taille fixe des marqueurs
            color=colors[i],
            edgecolors="black",
            linewidth=1,
            alpha=0.85,
            label=nageur
        )
        # Ajouter le texte du % réserve au centre du marker
        for _, row in sub.iterrows():
            ax.text(
                row["% Capacité Effort"], row["% Régénération"],
                str(int(row["% Réserve"])),
                ha="center", va="center", fontsize=7, fontweight="bold"
            )

    # # === Lignes centrales (50%) ===
    # ax.axvline(50, color="darkblue", linestyle="--", linewidth=1)
    # ax.axhline(50, color="darkblue", linestyle="--", linewidth=1)

    # === Mise en forme ===
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    ax.set_xlabel("% Capacité d’effort", fontsize=10)
    ax.set_ylabel("% Régénération", fontsize=10)
    ax.set_title("Évolution quotidienne : Régénération vs Capacité d’effort ASM Natation",
                 fontsize=12, fontweight="bold", pad=15)
    ax.grid(True, alpha=0.3)
    
    # === Légende propre en haut à droite (hors du graphique)
    # On crée la légende manuellement pour mieux contrôler les tailles
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(
        handles,
        labels,
        title="Nageurs",
        title_fontsize=11,
        fontsize=9,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        frameon=False,
        scatterpoints=1,
        markerscale=0.7,
        handleheight=1.5,
        handlelength=1.2,
        handletextpad=0.6,
        borderaxespad=0.2,
        labelspacing=0.6,   # 🔧 espace vertical entre lignes
    )
    
    # Supprime les marges inutiles
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"✅ Graphique sauvegardé : {save_path}")
    return save_path

# ================================
# 🔹 FONCTION 1 : Radar 5 axes
# ================================

def create_radar_chart(
    athlete_data: dict,
    reference_df: pd.DataFrame,
    save_path: str = "radar_chart.png",
    figsize=(6, 6)
):
    """
    Radar chart avec zones colorées dynamiques selon les seuils.
    Gère automatiquement la ligne '{Nom} Moyenne' si elle existe.
    """

    import numpy as np
    import matplotlib.pyplot as plt

    categories = ['% Capacité Effort', '% Réserve', '% Régénération', 'FC Couché', 'FC Debout']
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    nom = athlete_data.get("Nom", "Athlète")

    # ✅ Sélection de la bonne ligne moyenne (ex: "Marius Moyenne")
    mean_row = reference_df.loc[
        reference_df.index.str.contains(fr"^{nom}", case=False, na=False)
    ]
    if not mean_row.empty:
        mean_row = mean_row.iloc[0]
    else:
        # fallback : ligne "Moyenne" ou la première ligne moyenne dispo
        mean_candidates = reference_df[reference_df.index.str.contains("Moyenne", case=False, na=False)]
        mean_row = mean_candidates.iloc[0] if not mean_candidates.empty else reference_df.iloc[0]

    # === Données ===
    athlete_values = [athlete_data[c] for c in categories] + [athlete_data[categories[0]]]
    mean_values = mean_row[categories].tolist() + [mean_row[categories[0]]]

    # === Figure ===
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 200)
    ax.grid(False)
    ax.spines['polar'].set_visible(False)

    # === Zones colorées selon les seuils ===
    def vals(level): return reference_df.loc[level, categories].tolist() + [reference_df.loc[level, categories[0]]]

    try:
        danger_vals = vals("DANGER")
        vigil_vals  = vals("VIGILANCE")
        correct_vals= vals("CORRECT")
        ok_vals     = vals("OK")

        ax.fill(angles, danger_vals, color="red", alpha=0.2, label="Danger")
        ax.fill_between(angles, danger_vals, vigil_vals, color="orange", alpha=0.2)
        ax.fill_between(angles, vigil_vals, correct_vals, color="lightblue", alpha=0.2)
        ax.fill_between(angles, correct_vals, ok_vals, color="lightgreen", alpha=0.2)
        ax.fill_between(angles, ok_vals, [200]*len(ok_vals), color="green", alpha=0.15)
    except KeyError:
        print(f"⚠️ Seuils manquants dans la table de référence pour {nom}")

    # === Moyenne (gris pointillé)
    ax.plot(angles, mean_values, color="gray", linewidth=1.8, linestyle="dashed", label=f"{nom} Moyenne")
    ax.fill(angles, mean_values, color="gray", alpha=0.08)

    # === Athlète
    ax.plot(angles, athlete_values, color="#C40B71", linewidth=2.2, label=nom)
    ax.fill(angles, athlete_values, color="#C40B71", alpha=0.25)

    # === Esthétique
    plt.xticks(angles[:-1], categories, fontsize=9, weight="bold")
    ax.set_yticks(np.arange(0, 201, 25))
    ax.set_yticklabels([str(v) for v in range(0, 201, 25)], fontsize=7, color="gray")
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1), frameon=False, fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Radar chart sauvegardé : {save_path}")
    return save_path

# ================================
# 🔹 FONCTION 2 : Triangle 3 axes
# ================================

def create_triangle_chart(
    athlete_data: dict,
    reference_df: pd.DataFrame,
    save_path: str = "triangle_chart.png",
    figsize=(5, 4)
):
    """
    Triangle chart (radar 3 axes) comparant l'athlète et sa ligne '{Nom} Moyenne'.
    """

    import numpy as np
    import matplotlib.pyplot as plt

    categories = ['% Capacité Effort', '% Réserve', '% Régénération']
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    nom = athlete_data.get("Nom", "Athlète")

    # ✅ Sélection de la bonne ligne moyenne
    mean_row = reference_df.loc[
        reference_df.index.str.contains(fr"^{nom}", case=False, na=False)
    ]
    if not mean_row.empty:
        mean_row = mean_row.iloc[0]
    else:
        mean_candidates = reference_df[reference_df.index.str.contains("Moyenne", case=False, na=False)]
        mean_row = mean_candidates.iloc[0] if not mean_candidates.empty else reference_df.iloc[0]

    athlete_values = [athlete_data[c] for c in categories] + [athlete_data[categories[0]]]
    mean_values = mean_row[categories].tolist() + [mean_row[categories[0]]]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 200)
    ax.grid(False)
    ax.spines['polar'].set_visible(False)

    # --- Axes de fond
    for r in range(25, 201, 25):
        ax.plot(angles, [r] * (N + 1), color="gray", linewidth=0.3, alpha=0.5, linestyle='dotted')
    for angle in angles[:-1]:
        ax.plot([angle, angle], [0, 200], color="gray", linewidth=0.8, alpha=0.6)

    # --- Moyenne
    ax.plot(angles, mean_values, color="gray", linewidth=1.8, linestyle="dashed", label=f"{nom} Moyenne")
    ax.fill(angles, mean_values, color="gray", alpha=0.1)

    # --- Athlète
    ax.plot(angles, athlete_values, color="#C40B71", linewidth=2.2, label=nom)
    ax.fill(angles, athlete_values, color="#C40B71", alpha=0.25)

    plt.xticks(angles[:-1], categories, fontsize=9, weight="bold")
    ax.set_yticks(np.arange(0, 201, 25))
    ax.set_yticklabels([str(v) for v in range(0, 201, 25)], fontsize=7, color="gray")
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1), frameon=False, fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Triangle chart sauvegardé : {save_path}")
    return save_path

# === Exemple d’utilisation ===
if __name__ == "__main__":
    df_ref = pd.DataFrame({
        "Niveau": ["Moyenne", "DANGER", "VIGILANCE", "CORRECT", "OK"],
        "% Capacité Effort": [100, 40, 80, 120, 150],
        "% Réserve": [100, 40, 80, 120, 150],
        "% Régénération": [100, 40, 80, 120, 150],
        "FC Couché": [61, 40, 80, 120, 150],
        "FC Debout": [90, 40, 80, 120, 150]
    }).set_index("Niveau")

    athlete = {
        "Nom": "BOUCEIRO Gaëtane",
        "FC Couché": 60,
        "FC Debout": 86,
        "% Réserve": 74,
        "% Régénération": 90,
        "% Capacité Effort": 66
    }

    create_radar_chart(athlete, df_ref, "./temp_chart/radar_test.png")
    create_triangle_chart(athlete, df_ref, "./temp_chart/triangle_test.png")