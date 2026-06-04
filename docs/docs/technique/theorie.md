# Fondements Théoriques

Cette section détaille les principes physiques et mathématiques sur lesquels repose le moteur de compositing de **ColorStudio**.

## L'hypothèse d'additivité de la lumière

Dans le monde physique, la lumière obéit à un principe de superposition. Lorsque plusieurs sources lumineuses éclairent une même scène, leurs contributions s'additionnent. Les photons émis par une source n'interfèrent pas avec ceux d'une autre source.

C'est cette **hypothèse d'additivité de la lumière** qui justifie l'approche fondamentale utilisée par ColorStudio. Plutôt que de simuler l'interaction complexe de toutes les lumières simultanément lors du rendu 3D, il est mathématiquement correct de calculer l'effet de chaque lumière de manière isolée, puis de combiner les résultats.

## Modélisation mathématique

Pour formaliser ce principe dans le logiciel, nous adoptons la notation suivante :

Soit **$I_{\langle Light_{i}, pos_{j}
angle}$** l'image de rendu obtenue lorsque **seule** la source lumineuse $Light_{i}$ est active, et qu'elle se trouve à la position $pos_{j}$ sur sa trajectoire.

Dans cette image élémentaire, la valeur de chaque pixel correspond à l'énergie lumineuse reçue en ce point précis de la scène, provenant uniquement de cette lumière spécifique.

## Formule du compositing linéaire

Sous l'hypothèse d'additivité de la lumière, l'image globale résultant de l'activation simultanée de plusieurs sources lumineuses s'écrit tout simplement comme la somme de leurs contributions élémentaires.

Mathématiquement, si l'on souhaite combiner l'éclairage de la lampe $Light_{i}$ (à la position $pos_{j}$) avec celui de la lampe $Light_{k}$ (à une position $pos_{l}$), la formule est la suivante :

$$I(Light_{i} + Light_{k}, pos_{j} + pos_{l}) = I(Light_{i}, pos_{j}) + I(Light_{k}, pos_{l})$$

Cette équation démontre que l'image finale composite s'obtient par une simple addition des pixels (et des canaux de couleur) des images pré-calculées. 

## Application et validité dans ColorStudio

Ce principe est strictement valable dans un **cadre linéaire**. C'est ce fondement théorique qui permet à ColorStudio d'offrir un compositing en temps interactif : l'application manipule les images sous forme de matrices (via NumPy) et réalise des opérations d'addition et de multiplication simples (pour gérer l'intensité et la couleur de chaque lumière).

*Note sur le pipeline : Pour garantir la justesse physique de cette addition de la lumière, il est conseillé de réaliser le compositing sur des valeurs de pixels linéaires (Linear Color Space), avant toute application d'une correction Gamma ou d'un algorithme d'exposition sur l'image finale affichée à l'écran.*
