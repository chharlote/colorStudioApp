# Interface Utilisateur

Cette section décrit les différents éléments visuels de **ColorStudio**, leur agencement et comment les utiliser pour contrôler l'éclairage de votre scène.

## Organisation générale

L'interface de ColorStudio est organisée selon une disposition en trois zones verticales, complétées par une barre d'outils en haut et une barre de statut en bas :

* **Panneau de contrôle** (à gauche) : paramètres des lumières et post-processing
* **Zone de rendu** (au centre) : visualisation du résultat composité
* **Panneau de visualisation 3D** (à droite) : représentation tridimensionnelle de la chromaticité

Cette séparation favorise une utilisation fluide : modifier les paramètres à gauche produit un retour immédiat au centre, tandis que le panneau droit offre une analyse chromatiométrique.

## Écran d'accueil

Au lancement de l'application, un **écran de bienvenue** s'affiche avant le chargement de toute scène. Il propose un bouton unique :

* **"Ouvrir un fichier JSON"** : ouvre un dialogue de sélection de fichier

Cet écran offre aussi un lien direct vers le chargement. Une fois qu'un fichier JSON est chargé avec succès, les trois panneaux remplacent cet écran.

## Barre d'outils

Située en haut du centre d'affichage, la barre d'outils regroupe les actions rapides :

| Contrôle | Raccourci | Fonction |
|----------|-----------|----------|
| **< Panel** | Ctrl+1 | Afficher ou masquer le panneau de contrôle (gauche) |
| **Load JSON** | Ctrl+O | Charger un nouveau fichier de configuration |
| **Save** | Ctrl+S | Exporter le rendu actuel en image PNG |
| **Light/Dark** | Ctrl+T | Basculer entre les thèmes clair et sombre |
| **Panel >** | Ctrl+2 | Afficher ou masquer la visualisation 3D (droite) |

## Panneau de contrôle (Gauche)

Une fois un fichier JSON chargé, le panneau gauche contient deux catégories de contrôles.

### Sections des lumières

Chaque source lumineuse présente dans la scène s'affiche sous forme d'une **section repliable** portant le nom de la lumière. Cliquez sur le titre pour agrandir ou réduire la section.

Chaque section lumineuse contient trois types de contrôles :

* **Position X, Y, Z** : trois curseurs pour déplacer la lumière dans l'espace 3D (plages typiquement entre -5 et +5)
* **Exposition** : un curseur pour régler l'intensité lumineuse (plage : 0 à 10+)
* **Couleur** : un bouton coloré qui ouvre le sélecteur de couleur lors d'un clic

### Post-Processing

La section **Post-Processing** regroupe les traitements globaux appliqués après la composition des lumières. Deux sous-sections la composent :

#### Auto Exposure

* **Y Target** : luminosité moyenne cible (plage 0.0 à 1.0 ; 0.5 = exposition neutre)
* **Exposition** : ajustement additif de l'exposition globale

#### Saturation

* **Linear Saturation** : saturation directe dans l'espace RGB (0 = désaturé, 1 = normal)
* **Gamma Saturation** : saturation perceptuelle suivant la courbe gamma (plus naturelle)

## Zone de rendu (Centre)

La zone centrale affiche l'image composite résultant de l'addition de toutes les lumières pondérées par leurs paramètres respectifs et les traitements de post-processing.

* **Pas d'interaction directe** : c'est une zone de visualisation uniquement
* **Mise à jour en temps réel** : chaque modification dans le panneau gauche recalcule et rafraîchit cette zone
* **Résolution adaptée** : l'image s'ajuste à la taille disponible

## Visualisation 3D — Chromaticity (Droite)

Le panneau droit affiche un **cube de chromaticité tridimensionnel** interactif permettant d'analyser la distribution des couleurs du rendu.

### Principe

La chromaticité est représentée dans l'espace RGB tridimensionnel :

* Axe X : composante rouge
* Axe Y : composante verte
* Axe Z : composante bleue

Chaque pixel du rendu correspond à un point dans ce cube ; la densité des points indique la prédominance des couleurs.

### Contrôles

* **Rotation** : clic-gauche + déplacement de la souris
* **Zoom** : molette de la souris
* **Mise à jour** : le cube se met à jour en temps réel lors de modifications des lumières

### Interprétation

* **Concentration au centre** : prédominance de lumière neutre (blanc, gris)
* **Dispersion vers les coins** : large gamme chromatique avec lumières colorées
* **Absence de points dans certaines régions** : ces couleurs ne sont pas présentes dans le rendu

## Sélecteur de couleur

Quand vous cliquez sur le bouton de couleur d'une lumière, une **fenêtre de sélection de couleur** s'ouvre. Elle fonctionne selon le modèle de couleur HSV (Hue/Saturation/Value).

### Interface

* **Carré de couleur** (partie principale) : permet de sélectionner la teinte (horizontal) et la saturation (vertical)
* **Slider vertical** (à droite du carré) : régle la luminosité (Value)

### Application

Les changements de couleur sont appliqués immédiatement au rendu. Fermez le sélecteur pour valider le choix.

## Barre de statut

En bas de la fenêtre, une **barre de statut** affiche des informations contextuelles :

* État du chargement (nombre de lumières, chemins de fichiers)
* Messages d'erreur ou d'avertissement
* Confirmation des actions (sauvegarde, changement de thème)

## Menu File

Le menu **File** (Fichier) du menu bar propose trois actions :

* **Load JSON** (Ctrl+O) : charger une configuration de scène
* **Save** (Ctrl+S) : exporter le rendu actuel en PNG
* **Exit** : quitter l'application

## Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| Ctrl+O | Charger un fichier JSON |
| Ctrl+S | Sauvegarder l'image de rendu |
| Ctrl+T | Basculer le thème (clair ↔ sombre) |
| Ctrl+1 | Afficher/masquer le panneau gauche |
| Ctrl+2 | Afficher/masquer le panneau droit |

## Flux de travail typique

### Charger une scène

1. Lancez ColorStudio
2. Cliquez sur **"Ouvrir un fichier JSON"** ou utilisez Ctrl+O
3. Sélectionnez un fichier de configuration JSON
4. Une barre de progression s'affiche pendant le chargement des images
5. Une fois complètement chargée, la scène s'affiche dans la zone centrale

### Modifier l'éclairage

1. Cliquez sur la section d'une lumière dans le panneau gauche pour l'agrandir
2. Utilisez les curseurs **Position** pour déplacer la lumière
3. Réglez **Exposition** pour ajuster l'intensité
4. Cliquez sur le bouton de couleur pour modifier la teinte
5. Observez le rendu et le cube de chromaticité se mettre à jour en temps réel

### Affiner le rendu global

1. Développez la section **Post-Processing**
2. Réglez **Auto Exposure** pour normaliser la luminosité globale
3. Utilisez **Saturation** pour contrôler l'intensité des couleurs
4. Comparez le cube de chromaticité pour vérifier la distribution des couleurs

### Exporter le résultat

1. Une fois satisfait de l'éclairage, cliquez sur **"Save"** (Ctrl+S)
2. Choisissez un dossier et un nom de fichier
3. L'image PNG est sauvegardée avec le rendu final

## Notes et conseils

* **Mise à jour en temps réel** : tous les changements se reflètent immédiatement, permettant une exploration rapide des configurations d'éclairage.
* **Thèmes** : le thème clair est adapté aux environnements lumineux ; le thème sombre réduit la fatigue oculaire.
* **Masquer/afficher les panneaux** : utilisez Ctrl+1 et Ctrl+2 pour agrandir temporairement la zone de rendu si votre écran est petit.
* **Unités** : les positions de lumière sont exprimées dans les unités de la scène 3D originale (définies au moment du rendu Blender).
