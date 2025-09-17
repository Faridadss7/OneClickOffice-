# mini_ia.py
from templates import TABLEAU_TEMPLATES

def check_missing_columns(template_name, user_columns):
    """
    Retourne la liste des colonnes manquantes par rapport au template.
    """
    required = set(TABLEAU_TEMPLATES.get(template_name, []))
    given = set(user_columns)
    missing = list(required - given)
    return missing

def find_empty_cells(df):
    """
    Retourne un résumé simple des colonnes qui contiennent des valeurs vides.
    """
    empties = {col: int(df[col].isna().sum() + (df[col] == "").sum()) for col in df.columns}
    empties = {k: v for k, v in empties.items() if v > 0}
    return empties

def suggest_columns_from_phrase(phrase):
    """
    Petite heuristique : retourne une liste de colonnes suggérées selon mots-clés trouvés dans phrase.
    """
    phrase = (phrase or "").lower()
    suggestions = []
    if any(w in phrase for w in ["vente", "produit", "client", "prix", "quantité"]):
        suggestions = ["Produit", "Quantité", "Prix_unitaire", "Total"]
    elif any(w in phrase for w in ["santé", "patient", "diagnostic", "traitement"]):
        suggestions = ["Patient", "Date", "Diagnostic", "Traitement"]
    elif any(w in phrase for w in ["emploi", "horaire", "cours", "heure"]):
        suggestions = ["Jour", "Heure_debut", "Heure_fin", "Activité"]
    return suggestions