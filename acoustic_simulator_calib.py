import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit

# Configuration page
st.set_page_config(page_title="Simulateur acoustique", layout="centered")
st.title("🔊 Simulateur de la propagation acoustique dans les conduites")
st.markdown("Comparez la propagation du son selon les matériaux, testez alpha ou calibrez-le à partir de vos mesures terrain.")

# Paramètres utilisateur
col1, col2 = st.columns(2)

with col1:
    L0 = st.slider("Niveau initial (dB SPL)", 50, 140, 100)
    f0 = st.slider("Fréquence du son (Hz)", 20, 2000, 50)

with col2:
    pertes_jonctions = st.slider("Pertes aux jonctions (dB)", 0, 50, 20)
    pertes_reflexions = st.slider("Pertes par réflexions (dB)", 0, 20, 5)
    pertes_ecoulement = st.slider("Pertes liées à l’écoulement (dB)", 0, 10, 3)

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

# Calcul des pertes totales fixes
pertes_totales_fixes = pertes_jonctions + pertes_reflexions + pertes_ecoulement

# Vecteur distance
distances = np.linspace(0, 10_000, 500)

# Fonction de calcul du niveau sonore
def compute_levels(alpha):
    return [max(L0 - (alpha * d + pertes_totales_fixes), 0) for d in distances]

# Modèle théorique pour la calibration
def modele_attenuation(d, alpha):
    return L0 - (alpha * d + pertes_totales_fixes)

# Graphique
fig, ax = plt.subplots(figsize=(10, 6))

# Courbe pour le coefficient alpha personnalisé
levels_custom = compute_levels(alpha)
ax.plot(distances / 1000, levels_custom, label=f"Alpha personnalisé (α={alpha:.3f} dB/m)", color='black', linewidth=2)

# Courbes pour les matériaux sélectionnés
for material in selected_materials:
    alpha_mat = materials[material]
    levels = compute_levels(alpha_mat)
    ax.plot(distances / 1000, levels, label=f"{material} (α={alpha_mat:.3f} dB/m)", linestyle="--")

ax.set_title(f"Atténuation acoustique – {f0} Hz, {L0} dB à l'origine", fontsize=14)
ax.set_xlabel("Distance (km)", fontsize=12)
ax.set_ylabel("Niveau sonore (dB SPL)", fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax.legend()
plt.tight_layout()

st.pyplot(fig)

# Upload de mesures terrain
st.markdown("---")
st.subheader("📊 Import de mesures terrain")
uploaded_file = st.file_uploader("Téléchargez un fichier CSV avec colonnes 'distance_m' et 'niveau_dB'", type="csv")

if uploaded_file is not None:
    df_mesures = pd.read_csv(uploaded_file)

    # Conversion en array numpy
    X_mesures = df_mesures['distance_m'].values
    Y_mesures = df_mesures['niveau_dB'].values

    # Ajustement du modèle
    try:
        popt, pcov = curve_fit(modele_attenuation, X_mesures, Y_mesures, p0=[alpha])
        alpha_calibre = popt[0]
        erreur = np.mean(np.abs(modele_attenuation(X_mesures, alpha_calibre) - Y_mesures))
        
        st.success(f"✅ Meilleure valeur d'alpha trouvée : **{alpha_calibre:.4f} dB/m**")
        st.info(f"📉 Erreur moyenne résiduelle : ±{erreur:.2f} dB")

        # Recalcul avec alpha calibré
        def compute_levels_calibrated(alpha_calibre):
            return [max(L0 - (alpha_calibre * d + pertes_totales_fixes), 0) for d in distances]

        levels_calibrated = compute_levels_calibrated(alpha_calibre)

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
