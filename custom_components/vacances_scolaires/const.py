"""Constants for vacances_scolaires_fr integration."""

DOMAIN = "vacances_scolaires"
PLATFORMS = ["calendar", "sensor", "binary_sensor"]

CONF_ZONE = "zone"
CONF_ACADEMY = "academy"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_VERIFY_SSL = "verify_ssl"
CONF_CREATE_CALENDAR = "create_calendar"
CONF_TIMEZONE = "timezone"

DEFAULT_UPDATE_INTERVAL = 7  # days
DEFAULT_VERIFY_SSL = True
DEFAULT_CREATE_CALENDAR = True
DEFAULT_TIMEZONE = "Europe/Paris"

# Zones métropolitaines
ZONE_A = "A"
ZONE_B = "B"
ZONE_C = "C"
ZONES = [ZONE_A, ZONE_B, ZONE_C]

# Zones DOM-TOM
ZONE_GUADELOUPE = "Guadeloupe"
ZONE_MARTINIQUE = "Martinique"
ZONE_GUYANE = "Guyane"
ZONE_REUNION = "La Réunion"
ZONE_MAYOTTE = "Mayotte"
ZONE_NOUVELLE_CALEDONIE = "Nouvelle-Calédonie"
ZONE_POLYNESIE = "Polynésie française"
ZONE_WALLIS_FUTUNA = "Wallis-et-Futuna"
ZONE_SAINT_PIERRE_MIQUELON = "Saint-Pierre-et-Miquelon"

ZONES_DOMTOM = [
    ZONE_GUADELOUPE,
    ZONE_MARTINIQUE,
    ZONE_GUYANE,
    ZONE_REUNION,
    ZONE_MAYOTTE,
    ZONE_NOUVELLE_CALEDONIE,
    ZONE_POLYNESIE,
    ZONE_WALLIS_FUTUNA,
    ZONE_SAINT_PIERRE_MIQUELON,
]

ALL_ZONES = ZONES + ZONES_DOMTOM

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

# DOM-TOM Academies (pas de découpage en académies multiples)
DOMTOM_ACADEMIES = {
    ZONE_GUADELOUPE: {"Guadeloupe": "Guadeloupe"},
    ZONE_MARTINIQUE: {"Martinique": "Martinique"},
    ZONE_GUYANE: {"Guyane": "Guyane"},
    ZONE_REUNION: {"La Réunion": "La Réunion"},
    ZONE_MAYOTTE: {"Mayotte": "Mayotte"},
    ZONE_NOUVELLE_CALEDONIE: {"Nouvelle-Calédonie": "Nouvelle-Calédonie"},
    ZONE_POLYNESIE: {"Polynésie française": "Polynésie française"},
    ZONE_WALLIS_FUTUNA: {"Wallis-et-Futuna": "Wallis-et-Futuna"},
    ZONE_SAINT_PIERRE_MIQUELON: {"Saint-Pierre-et-Miquelon": "Saint-Pierre-et-Miquelon"},
}

# Fuseaux horaires par zone
ZONE_TIMEZONES = {
    ZONE_A: "Europe/Paris",
    ZONE_B: "Europe/Paris",
    ZONE_C: "Europe/Paris",
    ZONE_GUADELOUPE: "America/Guadeloupe",  # UTC-4
    ZONE_MARTINIQUE: "America/Martinique",  # UTC-4
    ZONE_GUYANE: "America/Cayenne",  # UTC-3
    ZONE_REUNION: "Indian/Reunion",  # UTC+4
    ZONE_MAYOTTE: "Indian/Mayotte",  # UTC+3
    ZONE_NOUVELLE_CALEDONIE: "Pacific/Noumea",  # UTC+11
    ZONE_POLYNESIE: "Pacific/Tahiti",  # UTC-10
    ZONE_WALLIS_FUTUNA: "Pacific/Wallis",  # UTC+12
    ZONE_SAINT_PIERRE_MIQUELON: "America/Miquelon",  # UTC-3
}

ZONES_ACADEMIES = {
    ZONE_A: ZONE_A_ACADEMIES,
    ZONE_B: ZONE_B_ACADEMIES,
    ZONE_C: ZONE_C_ACADEMIES,
    **DOMTOM_ACADEMIES,
}

ATTR_VACANCES_NAME = "nom"
ATTR_VACANCES_START = "debut"
ATTR_VACANCES_END = "fin"
ATTR_VACANCES_ZONE = "zone"
ATTR_ACADEMY = "academie"
ATTR_DAYS_REMAINING = "jours_restants"
ATTR_DAYS_UNTIL = "jours_avant"
