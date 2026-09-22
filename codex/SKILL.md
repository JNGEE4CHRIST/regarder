---
name: regarder
description: L'AIGUILLEUR DES VIDÉOS, et l'outil pour les screen records. Utiliser dès qu'une vidéo est envoyée, nommée ou mentionnée — fichier local OU lien en ligne : « regarde cette vidéo », « écoute mon screen record », « j'ai enregistré mon écran », « transcris-moi ça », « qu'est-ce qu'il dit dans la vidéo ? », « voici un Loom du client », « watch this video », un enregistrement d'appel Zoom, Meet ou Teams, un lien Loom, Drive, WeTransfer, YouTube ou TikTok, un .mov/.mp4/.webm déposé, une demande de modification faite en vidéo, une transcription de screen recording, ou une vidéo à analyser. Le skill TRANCHE d'abord quel outil convient : lui-même quand quelqu'un PARLE par-dessus un écran (il transcrit la voix EN LOCAL — mlx-whisper, gratuit, hors ligne, aucune clé API — et attache à chaque phrase l'écran de ce moment-là), ou le skill /watch quand c'est une URL à analyser pour son montage, son rythme ou son hook. ⛔ Se tromper de bord ne lève AUCUNE erreur : /watch sur un screen record rend un rapport complet sans une ligne de ce qui a été dit. ⛔ Ne PAS l'utiliser pour MONTER une vidéo (couper, assembler, exporter, ajouter de la musique) : il lit une vidéo, il n'en fabrique pas.
---

# Écouter un screen record

## Principe

Une demande de modification vit dans l'intersection du son et de l'image : « ce bouton-là,
monte-le ». Le mot « là » n'existe que dans l'écran. Lire seulement le texte fait deviner
de quoi il parle ; regarder seulement les images fait deviner ce qu'il en dit. `regarder.py`
rend les deux, alignés.

⛔ Ne pas transcrire autrement (API Whisper, `/watch`, sous-titres natifs, extraction
d'images seule) : un screen record n'a jamais de sous-titres, et un rapport « images
seulement » se lit exactement comme un rapport réussi.

## ⭐⭐ QUEL OUTIL POUR QUELLE VIDÉO — à lire AVANT de lancer quoi que ce soit

Deux outils, deux métiers. Se tromper ne plante pas : **ça rend un rapport qui a l'air bon.**

| La vidéo | L'outil | Pourquoi |
|---|---|---|
| **Fichier local où QUELQU'UN PARLE** — n'importe qui, n'importe comment : demande de modif par-dessus un écran, mémo, démo, bug montré, témoignage filmé, Zoom en vue galerie, message d'un sous-traitant | **`regarder` (ici)** | Voix transcrite en local et **attachée à l'écran de sa fraction de seconde**. C'est le seul qui résout « ce bouton-**là** » — et le seul qui refuse bruyamment quand le son manque. |
| **URL en ligne** (YouTube, TikTok, X, Vimeo) qu'on veut **analyser** — montage, rythme, hook, structure | **`/watch`** ([claude-watch](https://github.com/taoufik123-collab/claude-watch)) | Il avale les URL via yt-dlp, lit les **sous-titres natifs** (gratuits), et sort des métriques de montage (coupes/min, durée de plan) + un microscope des 10 premières secondes. ⛔ `regarder` ne télécharge rien — c'est voulu. ⚠️ **« Analyser » ne veut pas dire « savoir ce qui est dit ».** Si c'est le CONTENU qu'on veut (« résume-moi cette vidéo »), cette ligne ne s'applique pas : télécharger, puis `regarder` — sans sous-titres natifs, `/watch` rendra le rapport sans une ligne de parole. |
| **Screen record HÉBERGÉ** (Loom, Drive, WeTransfer) où quelqu'un parle | **les deux, dans cet ordre** | ⛔ **Le piège.** `/watch` le téléchargerait, ne trouverait **aucun sous-titre** (un screen record n'en a jamais), et rendrait les images seules **en code 0**, avec un rapport d'allure complète. On télécharge, puis on écoute : `yt-dlp -o ~/Downloads/v.mp4 "<URL>"` puis `regarder ~/Downloads/v.mp4`. |
| **Fichier local SANS AUCUNE VOIX** | **`/watch`**, avec `--resolution` monté | Il a le pacing et le microscope du hook ; `regarder` n'a ni l'un ni l'autre — et il refuse (code 3/4) si on s'y trompe. ⚠️ Mais son défaut est **512 px** : s'il y a du TEXTE à l'écran (une interface, un slide), il est illisible à cette taille — monter `--resolution`, sinon le rapport décrit des images qu'il n'a pas pu lire. |

⛔ **La ligne qui tranche tient en trois mots : EST-CE QUE QUELQU'UN PARLE ?**
Si oui → `regarder`, **toujours**, même depuis une URL (on la télécharge d'abord).
Si non → `/watch` fait mieux.

⚠️ **Ce n'est PAS « est-ce qu'il désigne l'écran ».** C'était la première version de cette
règle, et une revue aveugle l'a cassée le 20 sept. 2026 : un TikTok parlé téléchargé en
local ne tombait dans aucune ligne, la question de départage répondait « il ne désigne pas
l'écran » → `/watch` → **rapport sans une ligne de ce qui est dit, code 0**. La table
envoyait une vidéo parlée dans le trou qu'elle existe pour empêcher. Même famille : un
témoignage client filmé, un mémo face caméra, un Zoom en vue galerie.
👉 La désignation de l'écran dit **à quel point** `regarder` est supérieur. Elle n'aiguille
rien. **Une voix suffit.**

⚠️ **Se tromper de bord ne se voit pas.** `/watch` sur un screen record ne lève aucune
erreur : il rend un rapport complet, bien formaté, **sans une ligne de ce qui a été dit**
(`- **Transcript:** none available`, puis `return 0`, lu dans son code le 20 sept. 2026).
C'est exactement pour ça que cet outil-ci existe.


## Commande

```bash
python3 <RACINE>/scripts/regarder.py "<video>" --sortie /tmp/regard/<nom-court>-<HHMMSS>
```

Remplacer `<RACINE>` par le dossier où ce dépôt est installé, **en chemin absolu**.

- ⛔ **Lancer HORS du bac à sable dès le premier essai** (demande d'escalade, justification :
  « transcription locale sur la puce graphique »). Mesuré le 14 sept. 2026 : dans le bac à
  sable, MLX échoue avec `No Metal device available` — le GPU n'y est pas visible. **Ce
  n'est pas l'outil qui est cassé.**
- Écrire la commande telle quelle, chemin absolu, **sans `$(...)` ni `&&`** : une règle
  « toujours autoriser » ne reconnaît qu'une commande simple. Une fois approuvée, la
  vidéo suivante passe sans redemander.
- `--sortie` : un dossier **neuf**, heure écrite explicitement (ex. `modifs-accueil-142233`).
- `--langue fr` par défaut ; `--langue en` pour une vidéo anglaise. La langue ne se devine
  pas : forcer `fr` sur de l'anglais rend du français plausible et faux.
- Durée : ~5 s pour une vidéo de 45 s sur un M4 Pro.
- Si ça échoue, ne pas conclure que l'outil est cassé :
  `python3 <RACINE>/scripts/regarder.py --autotest` (7 phases, hors bac à sable aussi) tranche.

## Lire le résultat

1. Ouvrir `INDEX.md` dans le dossier de sortie. Chaque réplique porte `[mm:ss]` et le
   chemin de l'écran de ce moment.
2. ⛔ **OUVRIR l'image de chaque réplique**, pas seulement lire son chemin. C'est elle qui
   dit quel bouton, quelle section, quelle page.
3. La liste « Tous les écrans » en bas ne sert que si une consigne reste ambiguë : ne pas
   ouvrir toutes les images par défaut.
4. Rendre la liste des modifications demandées, une par ligne, avec l'horodatage et ce que
   l'écran montre, **AVANT de coder**.

## Pièges

- 🚫 **INVENTÉE** dans l'INDEX : Whisper a fabriqué une phrase sur du silence (souvent
  « Merci. »). Ne jamais l'exécuter ni en tirer une conclusion.
- `(piste N)` : deux pistes audio = son du système + micro. La consigne est sur la piste
  du micro.
- « ⚠️ AUCUN écran rendu à cet instant — écran d'APRÈS » : l'image est postérieure à la
  phrase, la recouper avec l'écran précédent.
- Le transcript n'est pas fiable à 100 % : noms propres, marques et phrases bizarres
  (« mets-le orange » → « mais le range ») se **vérifient dans l'image**. En cas de doute
  réel, demander plutôt qu'exécuter.

## Mettre à jour le paquet

⛔ **Rien ne se met à jour tout seul.** `<RACINE>` reste sur la version clonée.

```bash
cd <RACINE> && git pull && python3 scripts/regarder.py --autotest
```

⚠️ Si `git pull` refuse en parlant d'historiques divergents, l'historique a été réécrit
en amont — reprendre la version en ligne : `git fetch origin && git reset --hard origin/main`
(⛔ efface les modifications locales de ce dossier). L'installeur n'a pas à être relancé.

## Codes de sortie (aucun ne veut dire « il n'a rien dit »)

| Code | Sens | Quoi faire |
|---|---|---|
| 0 | OK | lire l'INDEX |
| 2 | `--sortie` n'est pas un dossier neuf de l'outil, ou fichier introuvable | donner un dossier neuf |
| 7 | la machine n'est pas équipée (ffmpeg absent) | `bash <RACINE>/installer.sh` — ⛔ pas `./installer.sh` : depuis un autre dossier il est introuvable |
| 3 | aucune piste audio (capturé sans micro) | redemander la vidéo avec le micro |
| 4 | toutes les pistes muettes (micro fermé) | redemander la vidéo |
| 5 | transcript vide malgré du son | ne rien conclure, lancer `--autotest` |
| 6 | aucune piste vidéo | rien à regarder |
| 8 | aucun écran rendu (transcript obtenu, zéro image) | « ce bouton-là » ne se résout pas ; l'INDEX est écrit comme preuve. Lancer `--autotest`. |

⭐ **`--essai-langue`** — `--langue` ne se devine pas, et se tromper ne rate pas
bruyamment : Whisper rend un texte **plausible et faux**, horodatages corrects, et la
demande du client se bâtit dessus. La commande qui tranche transcrit les 90 premières
secondes en **fr ET en en**, côte à côte, sans rien écrire :
`python3 <RACINE>/scripts/regarder.py "<video>" --essai-langue`

## ⛔ `/watch` EST UN SKILL CLAUDE — ce que ça veut dire si tu n'as QUE Codex

La table ci-dessus envoie deux cas vers `/watch` (claude-watch). **Ce n'est pas un outil
de ce paquet, et il n'existe pas côté Codex.** Trouvé par une revue Codex le 20 sept.
2026 : la table prescrivait un outil que son lecteur ne peut pas avoir — un aiguillage
vers le vide se lit comme un aiguillage.

Ce que tu fais, concrètement, sans Claude :

| Le cas | Sans `/watch` |
|---|---|
| **URL d'une vidéo où quelqu'un PARLE** | `yt-dlp -o /tmp/v.mp4 "<URL>"` puis `regarder`. **Tu ne perds rien de l'essentiel** : la parole et l'écran de chaque réplique. |
| **URL à analyser pour le MONTAGE** (rythme, coupes/min, hook) | ⛔ **Ce paquet ne le fait pas**, et il ne prétend pas le faire. Il n'y a pas d'équivalent Codex ici. |
| **Fichier local SANS aucune voix** | ⛔ `regarder` refuse (code 3 ou 4) — et c'est voulu : il n'a rien à transcrire. Il te le dit au lieu de rendre des images muettes. |

👉 **La limite, dite franchement : ce paquet sert les vidéos où QUELQU'UN PARLE.** Pour
le reste, il refuse bruyamment plutôt que de faire semblant.

## Sur quelles machines ça marche

| Machine | Moteur | Vitesse |
|---|---|---|
| Mac Apple Silicon | `mlx-whisper` (puce graphique) | la plus rapide |
| Mac Intel · Linux · WSL2 | `faster-whisper` (processeur) | plus lent, complet |
| Windows natif | ⛔ refusé — `wsl --install`, puis relancer l'installeur | — |

⭐ Le moteur retenu est IMPRIMÉ (`MOTEUR-VOIX: …`) et écrit dans l'INDEX. Un repli
silencieux serait le défaut que cet outil combat, sous un autre nom.
⛔ Windows natif n'est pas bloqué par le moteur : les garanties d'écriture de l'outil
tiennent sur 49 appels POSIX qui n'existent pas là-bas. WSL2 est du Linux — l'outil au
complet, sans une ligne en moins.

