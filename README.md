# Évaluation du Clustering d'Entités Nommées en Environnement OCR Bruité (Projet M2 TAL)

## 🎓 Contexte et Origine du Projet
Ce projet est le travail final de l'UE **"Paradigmes d'évaluation du TAL"** du **Master 2 Langue et Informatique** à **Sorbonne Université** (2025-2026), dirigé par **M. Gaël LEJEUNE**.

### 🎯 Objectif du Projet
Ce projet vise à évaluer l'impact de la **« pollution des entités »** générée par la Reconnaissance Optique de Caractères (**OCR**) sur la qualité du clustering des entités nommées.

* **Corpus** : Analyse de 14 œuvres littéraires du corpus **ELTeC** (en français et en anglais).
* **Méthodologie** : Comparaison des performances de **9 algorithmes de clustering** appliqués à différentes chaînes de traitement OCR (Kraken, Tesseract, etc.).

> **La problématique centrale :** > Comment évaluer la capacité des algorithmes de clustering à regrouper les variantes d'entités nommées (principalement des toponymes) dans des textes affectés par les erreurs OCR, **en l'absence d'un « standard d'or » complet** ?


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
