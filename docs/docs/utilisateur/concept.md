# Concept & Principes

Cette section explique le fonctionnement théorique de **ColorStudio** et l'approche spécifique qu'il utilise pour générer des rendus interactifs.

## Le Compositing Classique

Dans une approche classique de rendu 3D, une scène complexe prend beaucoup de temps à être calculée. Pour gagner du temps et de la flexibilité, on utilise le **compositing**. Cette technique consiste à rendre une scène en plusieurs "passes" distinctes :
- par objet (ex: rendre un personnage indépendamment de l'arrière-plan),
- par source lumineuse,
- ou par composante (diffuse, spéculaire, ombres, etc.).

Ces différentes images sont ensuite superposées et fusionnées en post-traitement pour obtenir l'image finale. Cette stratégie permet de modifier une partie spécifique de l'image sans avoir à recalculer mathématiquement toute la géométrie de la scène 3D.

## L'approche de ColorStudio

L'approche de **ColorStudio** est de proposer un compositing entièrement basé sur les **sources lumineuses**. 

Au lieu de se contenter d'une seule image statique par lumière, le processus est le suivant :
1. **Trajectoire de la lumière** : Pour chaque source lumineuse (lampe) présente dans la scène, une trajectoire est définie au moment du rendu initial.
2. **Série d'images** : Le moteur de rendu 3D calcule un ensemble d'images (parfois des dizaines ou une centaine) pour représenter les différentes positions possibles de cette lampe le long de sa trajectoire.
3. **Recomposition dynamique** : Dans ColorStudio, vous chargez ces séries d'images. L'application vous permet alors de "déplacer" virtuellement la lumière en naviguant dans cette série d'images, et de combiner les résultats de plusieurs lampes en temps réel.

## Le principe d'additivité de la lumière

ColorStudio s'appuie sur le principe physique de l'additivité de la lumière : l'éclairage total d'une scène est égal à la somme des éclairages de chaque source lumineuse individuelle.

En pratique, cela signifie que le logiciel superpose et additionne les pixels des images correspondant à chaque lampe (à la position, l'intensité et la couleur que vous avez choisies) pour générer l'image finale. 

Grâce à cette méthode, vous pouvez expérimenter avec des configurations d'éclairage complexes de manière totalement interactive, avec un retour visuel instantané !