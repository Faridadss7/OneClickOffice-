# templates.py
TABLEAU_TEMPLATES = {
    "Ventes": ["Produit", "Quantité", "Prix_unitaire", "Total"],
    "Comptabilité": ["Date", "Catégorie", "Montant", "Description"],
    "Suivi médical": ["Patient", "Date", "Diagnostic", "Traitement"],
    "Emploi du temps": ["Jour", "Heure_debut", "Heure_fin", "Activité"],
    "Secrétariat": ["Tâche", "Responsable", "Date limite", "Statut"]
}

FLYER_TEMPLATES = {
    "Anniversaire": {"background_color": "#FFE0B2", "font_color": "#000000", "header": "OneClickOffice"},
    "Événement": {"background_color": "#BBDEFB", "font_color": "#000000", "header": "OneClickOffice"},
    "Promo": {"background_color": "#C8E6C9", "font_color": "#000000", "header": "OneClickOffice"}
}