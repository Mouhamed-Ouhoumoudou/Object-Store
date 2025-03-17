class Config:
    """
    Global configuration for the application.
    """

    BASE_PATH = "data"  # Chemin de base pour stocker les objets
    MAX_GLOBAL_VERSIONS = 5  # Nombre maximal de versions globales
    MIN_FREE_SPACE_MB = 500  # Espace libre minimal en Mo avant nettoyage automatique

    # Politiques spécifiques aux objets
    OBJECT_POLICIES = {
        # Exemple : "plan-etat-de-l-art": 3
    }
