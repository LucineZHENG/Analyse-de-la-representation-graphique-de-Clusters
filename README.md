# Évaluation du Clustering d'Entités Nommées en Environnement OCR Bruité (Projet M2 TAL)

Ce projet porte sur l'évaluation de l'impact de la « pollution des entités » générée par la Reconnaissance Optique de Caractères (OCR) sur la qualité du clustering d'entités nommées. À travers l'analyse de 14 œuvres littéraires du corpus **ELTeC** (français et anglais), nous comparons les performances de 9 algorithmes de clustering sous différentes chaînes de traitement OCR.

---

## 📁 Description des fichiers

### Programmes principaux et outils
* **`app.py`** : Interface d'analyse globale basée sur **Streamlit**, permettant la visualisation dynamique de 54 configurations expérimentales.
* **`app_validation.py`** : Interface de validation des métriques, comparant les annotations manuelles (œuvre d'AIMARD) aux indicateurs d'évaluation automatique.
* **`Les mots pour tester.ipynb` & `.txt`** : Scripts de filtrage des entités, utilisant la fréquence et les règles de capitalisation pour extraire les toponymes pivots.
* **`explore_entities.py`** : Outil d'exploration des entités dans le corpus.
* **`graph_0.html` à `graph_5.html`** : Graphiques exportés correspondant aux six chaînes de traitement OCR (Kraken/Tesseract et leurs versions optimisées).

### Algorithmes de clustering (Fournis par l'enseignant)
* Fichiers commençant par **`Cluster...py`** : Implémentations incluant **Affinity Propagation** (plusieurs variantes), **DBSCAN**, **K-Means**, **HDBSCAN**, **OPTICS**, etc.

### Documentation
* **`Rapport.pdf`** : Rapport technique détaillé présentant la méthodologie et l'analyse des trois métriques clés : **Purity** (Pureté), **Indice AOS** (Taux de couverture) et **Silhouette** (Cohésion).

---

## 🚀 Reproduction de l'expérience

En raison de la taille du **corpus ELTeC** (environ 72 Mo compressé), dépassant la limite de téléchargement direct via l'interface web de GitHub, veuillez configurer les données localement selon les étapes suivantes :

### 1. Préparation du corpus
Les dossiers `corpus_en/` et `corpus_fr/` ne sont pas inclus dans ce dépôt. Veuillez extraire vos données localement selon la structure suivante :
* `/corpus_en/` : Contient les œuvres de AINSWORTH, BRONTE, GASKELL, etc.
* `/corpus_fr/` : Contient 11 œuvres dont BALZAC, FLAUBERT, MAUPASSANT, etc.
* **Note** : Chaque dossier d'auteur doit impérativement contenir les sous-répertoires `REF` (référence) et `OCR` (données expérimentales).

### 2. Configuration de l'environnement
Assurez-vous d'installer les bibliothèques Python nécessaires :
```bash
pip install streamlit pandas scikit-learn matplotlib jellyfish
