import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit

# Configuration page
st.set_page_config(page_title="Simulateur acoustique", layout="centered")
st.title("🔊 Simulateur de propagation acoustique dans les conduites")
st.markdown("Comparez la propagation du son selon les matériaux, testez alpha ou calibrez-le à partir de mesures terrain.")

# Paramètres utilisateur
col1, col2 = st.columns(2)

with col1:
    L0 = st.slider("Niveau initial (dB SPL)", 50, 140, 100)
    f0 = st.slider("Fréquence du son (Hz)", 20, 2000, 50)

with col2:
    attenuation_silencieux = st.slider("Atténuation piège à son (dB)", 0, 50, 0)
    pertes_par_branche = st.slider("Perte par bifurcation (dB)", 1.0, 5.0, 2.5, step=0.5)
    intervalle_branches = st.slider("Distance entre bifurcations (m)", 100, 1000, 400, step=50)
    alpha_ecoulement = st.slider("Atténuation due à l'écoulement (dB/m)", 0.000, 0.010, 0.001, step=0.0001, format="%.4f")
    alpha_reflexions = st.slider("Atténuation due aux réflexions (dB/m)", 0.000, 0.010, 0.002, step=0.0001, format="%.4f")

# Coefficients d'atténuation typiques par matériau
materials = {
    "Fonte": 0.005,
    "Béton": 0.01,
    "PVC": 0.012,
    "PEHD": 0.02,
}

# Sélection des matériaux à afficher
selected_materials = st.multiselect("Sélectionnez les matériaux à comparer", list(materials.keys()), default=["Fonte", "PVC"])

# Slider personnalisé pour alpha
alpha = st.slider("Coefficient d’atténuation α (dB/m)", 0.002, 0.020, 0.010, step=0.001, key="alpha_slider")

# Calcul final de l'alpha global
alpha_total = alpha + alpha_ecoulement + alpha_reflexions

# Calcul des pertes sans jonction (base)
pertes_base = attenuation_silencieux

# Vecteur distance
distances = np.linspace(0, 10_000, 500)

# Fonction pour calculer les pertes liées aux jonctions
def compute_pertes_jonctions(distance, pertes_par_branche, intervalle_branches):
    if intervalle_branches == 0:
        return 0
    return (distance // intervalle_branches) * pertes_par_branche

# Fonction de calcul du niveau sonore
def compute_levels(alpha_total, d, pertes_base, pertes_par_branche, intervalle_branches):
    pertes_jonctions = compute_pertes_jonctions(d, pertes_par_branche, intervalle_branches)
    total_pertes = pertes_base + pertes_jonctions
    return max(L0 - (alpha_total * d + total_pertes), 0)

# Modèle théorique pour la calibration
def modele_attenuation(d, alpha_total):
    pertes_jonctions = compute_pertes_jonctions(d, pertes_par_branche, intervalle_branches)
    total_pertes = pertes_base + pertes_jonctions
    return max(L0 - (alpha_total * d + total_pertes), 0)

# Calcul des niveaux
levels_custom = [compute_levels(alpha_total, d, pertes_base, pertes_par_branche, intervalle_branches) for d in distances]

# Ajout champ libre
# Calcul avec seuil minimal à 0 dB SPL (évite les valeurs non physiques)
levels_open = np.array([
    max(L0 - 20 * np.log10(d), 0) if d > 0 
    else L0  # Pas d'atténuation si d = 0
    for d in distances
])

# Application de l'atténuation supplémentaire à partir de 10m (tout en gardant >= 0)
levels_open_mur = levels_open.copy()
levels_open_mur[distances >= 10] = np.maximum(levels_open_mur[distances >= 10] - 45, 0)  # Évite < 0 après atténuation

# Graphique
fig, ax = plt.subplots(figsize=(10, 6))

# Courbes principales
ax.plot(distances / 1000, levels_open, label="Champ libre", color='green', linewidth=1, linestyle="--")
ax.plot(distances / 1000, levels_open_mur, label="Champ libre + mur à 10m (-45dB)", color='gray', linewidth=1, linestyle="--")
ax.plot(distances / 1000, levels_custom, label=f"Alpha personnalisé (α={alpha:.4f} dB/m)", color='black', linewidth=2)

# Courbes pour les matériaux sélectionnés
for material in selected_materials:
    alpha_mat = materials[material]
    alpha_total_mat = alpha_mat + alpha_ecoulement + alpha_reflexions
    levels = [compute_levels(alpha_total_mat, d, pertes_base, pertes_par_branche, intervalle_branches) for d in distances]
    ax.plot(distances / 1000, levels, label=f"{material} (α={alpha_total_mat:.4f} dB/m)", linestyle="--")

# Mise en forme graphique
ax.set_title(f"Atténuation acoustique – {f0} Hz, {L0} dB à l'origine\n"
             f"{intervalle_branches} m entre jonctions, {pertes_par_branche} dB par branche", fontsize=12)
ax.set_xlabel("Distance (km)", fontsize=12)
ax.set_ylabel("Niveau sonore (dB SPL)", fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax.legend()
plt.tight_layout()

st.pyplot(fig)

# Affichage du niveau final à une distance donnée
distance_test = st.slider("Distance à tester (m)", 0, 10000, 5000, step=100)
level_final = compute_levels(alpha_total, distance_test, pertes_base, pertes_par_branche, intervalle_branches)
st.metric(label=f"Niveau après {distance_test//1000} km", value=f"{level_final:.1f} dB SPL")

# Upload de mesures terrain
st.markdown("---")
st.subheader("📊 Import de mesures terrain")
uploaded_file = st.file_uploader("Téléchargez un fichier CSV avec colonnes 'distance_m' et 'niveau_dB'", type="csv")

if uploaded_file is not None:
    df_mesures = pd.read_csv(uploaded_file)
    X_mesures = df_mesures['distance_m'].values
    Y_mesures = df_mesures['niveau_dB'].values

    try:
        popt, pcov = curve_fit(lambda x, a: modele_attenuation(x, a), X_mesures, Y_mesures, p0=[alpha_total])
        alpha_calibre = popt[0]
        erreur = np.mean(np.abs([modele_attenuation(X_mesures[i], alpha_calibre) - Y_mesures[i] for i in range(len(X_mesures))]))

        st.success(f"✅ Meilleure valeur d'alpha trouvée : **{alpha_calibre:.4f} dB/m**")
        st.info(f"📉 Erreur moyenne résiduelle : ±{erreur:.2f} dB")

        # Recalcul avec alpha calibré
        def compute_levels_calibrated(alpha_calibre, d):
            pertes_jonctions = compute_pertes_jonctions(d, pertes_par_branche, intervalle_branches)
            total_pertes = pertes_base + pertes_jonctions
            return max(L0 - (alpha_calibre * d + total_pertes), 0)

        levels_calibrated = [compute_levels_calibrated(alpha_calibre, d) for d in distances]

        # Tracer la comparaison
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(distances / 1000, levels_calibrated, label=f"Modèle calibré (α={alpha_calibre:.4f} dB/m)", color='green', linewidth=2)
        ax2.scatter(X_mesures / 1000, Y_mesures, color='red', label="Mesures terrain", zorder=5)
        ax2.set_title("Comparaison modèle calibré vs mesures terrain", fontsize=14)
        ax2.set_xlabel("Distance (km)")
        ax2.set_ylabel("Niveau sonore (dB SPL)")
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax2.legend()
        plt.tight_layout()
        st.pyplot(fig2)

    except RuntimeError:
        st.error("❌ Impossible de calibrer : les données ne permettent pas un ajustement correct.")
