"""Constants for vacances_scolaires_fr integration."""

DOMAIN = "vacances_scolaires"
PLATFORMS = ["calendar", "sensor", "binary_sensor"]

CONF_ZONE = "zone"
CONF_ACADEMY = "academy"
ZONE_A = "A"
ZONE_B = "B"
ZONE_C = "C"
ZONES = [ZONE_A, ZONE_B, ZONE_C]

# Zone A Academies
ZONE_A_ACADEMIES = {
    "Besançon": "Besançon, Bourgogne-Franche-Comté",
    "Bordeaux": "Bordeaux, Aquitaine",
    "Clermont-Ferrand": "Clermont-Ferrand, Auvergne",
    "Dijon": "Dijon, Bourgogne",
    "Grenoble": "Grenoble, Rhône-Alpes",
    "Limoges": "Limoges, Limousin",
    "Lyon": "Lyon, Rhône-Alpes",
    "Poitiers": "Poitiers, Poitou-Charentes",
}

# Zone B Academies
ZONE_B_ACADEMIES = {
    "Aix-Marseille": "Aix-Marseille, Provence-Alpes-Côte d'Azur",
    "Amiens": "Amiens, Picardie",
    "Caen": "Caen, Normandie",
    "Lille": "Lille, Nord-Pas-de-Calais",
    "Nancy-Metz": "Nancy-Metz, Lorraine",
    "Nantes": "Nantes, Pays de la Loire",
    "Nice": "Nice, Côte d'Azur",
    "Orléans-Tours": "Orléans-Tours, Centre-Val de Loire",
    "Reims": "Reims, Champagne-Ardenne",
    "Rennes": "Rennes, Bretagne",
    "Rouen": "Rouen, Normandie",
    "Strasbourg": "Strasbourg, Alsace",
}

# Zone C Academies
ZONE_C_ACADEMIES = {
    "Créteil": "Créteil, Île-de-France",
    "Île-de-France": "Île-de-France (Paris, Versailles)",
    "Montpellier": "Montpellier, Languedoc-Roussillon",
    "Toulouse": "Toulouse, Midi-Pyrénées",
    "Corse": "Corse",
}

ZONES_ACADEMIES = {
    ZONE_A: ZONE_A_ACADEMIES,
    ZONE_B: ZONE_B_ACADEMIES,
    ZONE_C: ZONE_C_ACADEMIES,
}

ATTR_VACANCES_NAME = "nom"
ATTR_VACANCES_START = "debut"
ATTR_VACANCES_END = "fin"
ATTR_VACANCES_ZONE = "zone"
ATTR_ACADEMY = "academie"
ATTR_DAYS_REMAINING = "jours_restants"
ATTR_DAYS_UNTIL = "jours_avant"
