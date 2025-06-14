# Propagation_guidee
Modélisation mathématique de la propagation acoustique dans les réseaux d’eaux usées
👉 Lien de l'application: https://propagationguidee-kmznyeuaiavwerqw2xdpqv.streamlit.app/
# Simulateur acoustique dans les réseaux d’eaux usées

Ce projet permet de simuler la **propagation acoustique dans les conduites gravitaires ou enterrées**, typiques des réseaux d’eaux usées.  
L’application développée en **Streamlit** inclut :

✅ Simulation de la baisse du niveau sonore sur plusieurs kilomètres  
✅ Choix du matériau et du milieu de propagation (air, liquide, paroi)  
✅ Calibration automatique à partir de mesures terrain  
✅ Export PDF des résultats  

> 🎯 Objectif : comprendre comment le son se propage dans les réseaux souterrains et comment modéliser cela avec précision.

---

## 🧮 Modèle théorique utilisé

Le niveau sonore diminue progressivement à mesure que le son parcourt la conduite. Cette diminution suit une loi linéaire sur l’échelle logarithmique (en dB SPL) :

    L(d)=L0−(α*d+P)

(NB: Niveau sonore à la distance d = Niveau initial - (atténuation * distance + pertes supplémentaires))


où :
- **L(d)--Niveau sonore à la distance d** : niveau en dB SPL à un point donné,
- **L0--Niveau initial** : niveau sonore au départ (par exemple 100 dB SPL),
- **α--Atténuation** : coefficient d'atténuation linéique (en dB/m), dépendant du matériau et du milieu de propagation,
- **d--Distance** : longueur parcourue par le son (en mètres),
- **P--Pertes supplémentaires** : perte d'énergie liée aux jonctions, courbures, écoulement (en dB).

> ⚠️ Le niveau sonore ne peut pas descendre en dessous de 0 dB SPL.

---

## 🔤 Exemple concret

Si :
- Niveau initial L0 = 100 dB SPL
- Coefficient d’atténuation α = 0.01 dB/m
- Pertes supplémentaires P = 10 dB
- Distance d = 5000 mètres

Alors :
Niveau après 5 km = 100 - (0.01 * 5000 + 10) = 40 dB SPL


---

## 📊 Coefficient d'atténuation (α)

Le coefficient d’atténuation varie selon **le matériau de la conduite** et **le milieu dans lequel le son se propage**.

| Milieu   | Matériau | Atténuation typique (dB/m) |
|----------|----------|-----------------------------|
| Air      | Fonte    | 0.002 – 0.008               |
| Air      | PVC      | 0.008 – 0.015               |
| Air      | PEHD     | 0.01 – 0.025                |
| Liquide  | Eau usée | 0.02 – 0.05                 |
| Paroi    | Fonte    | 0.08 – 0.15                 |
| Paroi    | PVC      | 0.1 – 0.25                  |

> Plus ce coefficient est élevé, plus le son s’affaiblit rapidement.

---

## 💥 Pertes supplémentaires

En plus de l’atténuation naturelle, certaines structures du réseau causent des pertes additionnelles :

- Jonctions / bifurcations : environ 2.5 dB par branche
- Réflexions (coudes, changements de diamètre) : ~5 dB
- Interactions avec l’écoulement turbulent : ~3 dB

Exemple :  
Pour 8 branches + réflexions + écoulement → perte totale ≈ **28 dB**

---

## 🔧 Calibration automatique

Quand vous importez des mesures terrain (niveau sonore mesuré à différentes distances), l’application ajuste automatiquement le coefficient d’atténuation pour faire correspondre le modèle aux données réelles.

Elle cherche la valeur du coefficient qui donne la meilleure prédiction possible du niveau sonore.

---

## 📌 Résumé des paramètres utilisés

| Paramètre           | Description                      | Unité     |
|---------------------|----------------------------------|-----------|
| Niveau initial      | Niveau sonore au départ          | dB SPL    |
| Atténuation         | Perte par mètre due au matériau   | dB/m      |
| Distance            | Longueur de propagation          | m         |
| Pertes supplémentaires | Dues aux raccords, écoulement  | dB        |
| Niveau final        | Niveau sonore après la distance  | dB SPL    |
| Erreur résiduelle   | Différence entre modèle et mesure| dB        |

---

## 📘 Documentation technique

👉 [📄 Télécharger le PDF complet](lien_vers_fichier.pdf)  

---

## 📁 À propos du projet

Ce simulateur a été développé pour étudier la propagation acoustique dans les réseaux d’assainissement, utile notamment pour :
- La surveillance passive des réseaux,
- Le diagnostic acoustique (fuites, obstructions),
- L’étude de la transmission sonore dans différents matériaux.

---

## 🚀 Installation rapide

```bash
pip install streamlit matplotlib numpy pandas scipy reportlab
streamlit run acoustic_simulator.py
