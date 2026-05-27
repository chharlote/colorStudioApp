# Architecture Logicielle

Cette section détaille l'organisation interne du code source de **ColorStudio**, ses dépendances techniques et les principes de conception qui garantissent sa maintenabilité.

## Patron de conception : MVC (Modèle-Vue-Contrôleur)

Pour assurer une séparation claire entre l'interface utilisateur, la logique métier (le compositing) et les interactions, ColorStudio repose sur le patron de conception **MVC (Modèle-Vue-Contrôleur)**. 

* **Modèle** : Gère les données (images, configurations des lumières) et les calculs mathématiques (additivité de la lumière).
* **Vue** : Gère l'affichage (fenêtres, boutons, zone de rendu, visualisation 3D).
* **Contrôleur** : Fait le lien. Il écoute les actions de l'utilisateur sur la Vue, met à jour le Modèle, et demande à la Vue de se rafraîchir.

## Arborescence du projet

Voici la structure générale du répertoire de l'application :

```text
ColorStudio/
├── assets/              # Ressources graphiques (splash screen, icônes, images de test)
├── data/                # Fichiers de données (ex: fichiers JSON de configuration de scènes) et dossiers de sortie
├── docs/                # Documentation du projet (fichiers Markdown)
├── scripts/             # Scripts utilitaires externes (ex: colorstudio_exporter.py)
└── src/                 # Code source principal de l'application
    ├── controllers/     # Logique de contrôle
    ├── models/          # Logique métier et données
    ├── utils/           # Fonctions utilitaires transversales
    ├── views/           # Interface graphique et widgets
    └── colorStudioApp.py # Point d'entrée principal
```

## Détail du code source (`src/`)

L'intégralité du code exécutable métier se trouve dans le dossier `src/`. Voici le détail et le rôle de chaque fichier :

### Point d'entrée
* **`src/colorStudioApp.py`** : C'est le script principal à lancer pour démarrer l'application. Il initialise la boucle d'événements de l'interface graphique (PyQt6), instancie le modèle, la vue, le contrôleur, et assemble ces trois composants avant d'afficher la fenêtre principale.

### Modèles (`src/models/`)
* **`colorStudioModel.py`** : C'est le cœur mathématique et structurel du projet. Il charge les séries d'images en mémoire, stocke l'état actuel de chaque lampe (position sur la trajectoire, couleur, exposition temporelle) et effectue les opérations de calcul matriciel (addition des calques) pour produire l'image compositée finale sans toucher à l'interface.

### Vues (`src/views/`)
* **`colorStudioUIBuilder.py`** : Responsable de la construction de l'interface principale. Il place les différents panneaux (zone de rendu au centre, panneau de contrôle à gauche, visualisation à droite) et gère le comportement de la fenêtre (redimensionnement automatique, plein écran).
* **`colorStudioWidget.py`** : Contient les composants visuels personnalisés. On y trouve notamment les contrôleurs individuels de lampes (curseurs, boutons de couleur), la roue chromatique interactive, et l'intégration de la zone de dessin OpenGL (ModernGL) pour le nuage de points 3D.

### Contrôleurs (`src/controllers/`)
* **`colorStudioController.py`** : Agit comme un chef d'orchestre. Lorsqu'un utilisateur modifie l'exposition d'une lampe via un widget (Vue), le contrôleur intercepte ce signal, demande au `colorStudioModel` de mettre à jour ses données et de recalculer l'image finale, puis renvoie cette nouvelle image à la Vue pour affichage.

### Utilitaires (`src/utils/`)
* **`colorStudioUtils.py`** : Regroupe des fonctions pures qui n'ont pas besoin de connaître l'état de l'application. Cela inclut le traitement spécifique des images, les algorithmes d'exposition automatique, ou encore les conversions complexes entre différents espaces colorimétriques (RGB, HSV, linéaire, etc.).

## Technologies et Dépendances

Le bon fonctionnement de cette architecture repose sur un écosystème Python moderne :
- **Python 3.12+** : Langage d'exécution.
- **PyQt6** : Bibliothèque utilisée pour créer toute l'interface graphique (menus, fenêtres, signaux/slots).
- **NumPy** : Indispensable pour la manipulation ultra-rapide des images sous forme de matrices (NDArrays) lors du compositing.
- **ModernGL** : Utilisé dans les widgets pour le rendu 3D matériel interactif (visualisation des couleurs).
- **scikit-image / imageio** : Bibliothèques spécialisées pour la lecture, l'écriture et le traitement des fichiers images.
