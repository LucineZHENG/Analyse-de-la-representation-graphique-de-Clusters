import json
from pathlib import Path
import pandas as pd


def get_top_entities(directory="."):
    base_path = Path(directory)
    # Recherche de tous les fichiers de clustering de référence (REF)
    ref_files = list(base_path.rglob("*REF*_clusters.json"))

    if not ref_files:
        print("❌ Erreur : aucun fichier de clustering REF trouvé dans le répertoire courant ou ses sous-dossiers.")
        return

    # Sélection du premier fichier REF pour une analyse approfondie
    target_file = ref_files[0]
    print(f"🔍 Analyse du fichier de référence : {target_file.name}\n")

    with open(target_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entity_list = []

    for cluster_id, words in data.items():
        # Filtrage des mots d’un seul caractère et des valeurs numériques
        # (bruit OCR fréquent)
        valid_words = [w for w in words if len(str(w)) > 2 and not str(w).isdigit()]
        if not valid_words:
            continue

        # Logique d’analyse :
        # La taille du cluster reflète la diversité des variantes OCR de l’entité
        # Le mot le plus court est choisi comme forme représentative,
        # car il correspond le plus souvent à l’orthographe canonique
        representative = min(valid_words, key=len)

        entity_list.append({
            "Entité (terme de recherche suggéré)": representative,
            "Taille du cluster (nombre de variantes)": len(words),
            "Exemples (trois premières variantes)": words[:3]
        })

    # Tri par nombre de variantes :
    # plus un cluster est grand, plus son comportement est informatif
    # pour l’évaluation des métriques
    df = pd.DataFrame(entity_list).sort_values(
        by="Taille du cluster (nombre de variantes)",
        ascending=False
    )

    # Affichage des résultats
    print("📋 --- Liste des entités recommandées pour les tests (Top 15) ---")
    print(df.head(15).to_string(index=False))

    # Recommandations spécifiques au texte d’AINSWORTH
    print("\n💡 --- Recommandations clés pour le Sujet 3 ---")
    print("1. Référence de stabilité : 'London', 'Park' (présents dans presque tous les flux)")
    print("2. Test du bruit sur les noms propres : 'Auriol', 'Rougemont' (clé pour le score Silhouette)")
    print("3. Test des déformations de caractères : 'Thorneycroft', 'Elizabeth' (mots longs, précision réduite)")
    print("4. Test de perte d’entité : 'Millbank', 'Ebba' (observation d’un score AOS nul)")


if __name__ == "__main__":
    get_top_entities()
