---
name: regarder
description: L'AIGUILLEUR DES VIDÉOS, et l'outil pour les screen records. Utiliser dès qu'une vidéo est envoyée, nommée ou mentionnée — fichier local OU lien en ligne : « regarde cette vidéo », « écoute mon screen record », « j'ai enregistré mon écran », « transcris-moi ça », « qu'est-ce qu'il dit dans la vidéo ? », « voici un Loom du client », « watch this video », un enregistrement d'appel Zoom, Meet ou Teams, un lien Loom, Drive, WeTransfer, YouTube ou TikTok, un .mov/.mp4/.webm déposé, une demande de modification faite en vidéo, une transcription de screen recording, ou une vidéo à analyser. Le skill TRANCHE d'abord quel outil convient : lui-même quand quelqu'un PARLE par-dessus un écran (il transcrit la voix EN LOCAL — mlx-whisper, gratuit, hors ligne, aucune clé API — et attache à chaque phrase l'écran de ce moment-là), ou le skill /watch quand c'est une URL à analyser pour son montage, son rythme ou son hook. ⛔ Se tromper de bord ne lève AUCUNE erreur : /watch sur un screen record rend un rapport complet sans une ligne de ce qui a été dit. ⛔ Ne PAS l'utiliser pour MONTER une vidéo (couper, assembler, exporter, ajouter de la musique) : il lit une vidéo, il n'en fabrique pas.
argument-hint: "<chemin-de-la-video> [ce que tu veux en savoir]"
allowed-tools: Bash, Read
license: MIT
user-invocable: true
---

# /regarder — entendre et voir une vidéo, alignés

## Le trou que ça bouche

Une demande de modification vit dans l'**intersection** du son et de l'image :
« ce bouton-**là**, monte-le ». Le mot « là » n'existe que dans l'écran.

- Lire seulement le transcript → tu devines de **quoi** il parle.
- Regarder seulement les images → tu devines ce qu'il en **dit**.

⛔ **Et le piège qui a rendu cet outil nécessaire :** les outils de type `/watch`
transcrivent par **API Whisper**, avec **les sous-titres natifs en premier**. Un screen
record n'a **jamais** de sous-titres. Sans clé API, l'outil retombe donc sur les images
seules — **sans que ça compte comme un échec**. Il le **dit** (une ligne sur stderr, une
note dans le rapport), mais il sort en **code 0** avec un **rapport d'allure complète** :
un `$?` et une lecture en diagonale passent tous les deux. ⭐ Et même avec une clé valide,
un Whisper qui ne rend rien sort **aussi** en code 0 — l'exception est attrapée et dégradée
en une ligne. **Le transcript n'est jamais une condition de succès.** Or **un rapport sans
le son se lit exactement comme un rapport réussi**. C'est la forme de cécité la plus chère : un outil qui répond,
qui ne bloque pas, et qui a sauté la moitié de la question.

Ici, l'absence de son est un **refus bruyant** (code 3, 4 ou 5), jamais un rapport muet.

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


## La commande

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/regarder.py" "<video>" --sortie <dossier-neuf>
```

- `--sortie` : un dossier **neuf**, avec l'heure dedans (ex. `/tmp/regard/modifs-142233`).
  L'outil refuse (code 2) d'écrire dans un dossier qui n'est pas à lui — il ne va jamais
  effacer les fichiers de quelqu'un d'autre.
- `--langue fr` par défaut, `--langue en` pour une vidéo anglaise.
  ⛔ **La langue ne se devine pas.** Forcer `fr` sur de l'anglais ne rate pas bruyamment :
  Whisper rend un texte **plausible et faux**, horodatages corrects, et le travail se
  bâtit dessus. Dans le doute, une commande le tranche — elle transcrit les 90
  premières secondes dans LES DEUX langues, côte à côte, sans rien écrire :
  `python3 ${CLAUDE_SKILL_DIR}/scripts/regarder.py <video> --essai-langue`
- `--images N` : combien d'écrans extraire (défaut raisonnable, monte si l'interface est dense).
- Vitesse : ~5 s pour une vidéo de 45 s sur un M4 Pro.

## Lire le résultat — les 4 étapes, dans l'ordre

1. Ouvrir `INDEX.md` dans le dossier de sortie. Chaque réplique porte son `[mm:ss]` et
   le **chemin de l'écran de ce moment-là**.
2. ⛔ **OUVRIR l'image de chaque réplique avec `Read`**, pas seulement lire son chemin.
   C'est l'image qui dit *quel* bouton, *quelle* section, *quelle* page. Lire le chemin
   sans ouvrir l'image, c'est refaire exactement le défaut que l'outil corrige.
3. La liste « Tous les écrans » en bas ne sert que si une consigne reste ambiguë —
   ne pas ouvrir les 36 images par défaut, ça coûte cher en contexte pour rien.
4. **Rendre la liste des demandes AVANT de coder** : une case à cocher par demande, dans
   l'ordre où elles sont dites, avec l'horodatage, la citation, et ce que l'écran montre
   à cet instant.

⛔ **Rien d'inventé.** Si une demande est inaudible ou ambiguë, l'écrire **À CLARIFIER**
au lieu de la deviner. Une modification devinée coûte plus cher qu'une question.

## Les pièges qui ne plantent pas

| Ce que tu vois | Ce que ça veut dire |
|---|---|
| 🚫 **INVENTÉE** dans l'INDEX | Whisper a fabriqué une phrase sur du silence (souvent « Merci. »). ⛔ Ne jamais l'exécuter ni en tirer une conclusion. |
| `(piste N)` | Deux pistes audio = le son de l'écran **et** le micro. La consigne de la personne est sur la piste du micro. Elles sont transcrites séparément **exprès** : mélangées, la voix la plus forte masque l'autre et l'instruction disparaît sans un mot. |
| « ⚠️ AUCUN écran rendu à cet instant — écran d'APRÈS » | L'image est postérieure à la phrase. La recouper avec l'écran précédent. |
| Un mot bizarre (« mets-le orange » → « mais le range ») | Le transcript n'est pas fiable à 100 % sur les noms propres et les marques. **Ça se vérifie dans l'image**, et en cas de doute réel, on demande. |

## Les codes de sortie — aucun ne veut dire « il n'a rien dit »

Les trois premiers se lisent tous « la vidéo ne dit rien », et n'ont pas le même correctif :

| Code | Sens | Quoi faire |
|---|---|---|
| 0 | OK | lire l'`INDEX.md` |
| 2 | `--sortie` n'est pas un dossier neuf de l'outil, ou fichier introuvable | donner un dossier neuf |
| 7 | **la machine n'est pas équipée** — ffmpeg absent | lancer `./installer.sh` |
| 3 | **aucune piste audio** — l'écran a été capturé sans le micro | redemander la vidéo, micro ouvert. Rien à sauver. |
| 4 | **pistes muettes** — micro fermé ou mauvaise entrée | redemander la vidéo. ⚠️ On refuse AVANT de lancer Whisper, parce qu'il **hallucine** des phrases sur du silence, avec des horodatages corrects — indiscernables d'un vrai transcript à la lecture. |
| 5 | **transcript vide** malgré du son | vrai défaut : ne rien conclure, lancer `--autotest` |
| 6 | aucune piste vidéo | rien à montrer, donc aucun « ça » ne se résout |
| 8 | **aucun écran rendu** — transcript obtenu, zéro image | la moitié de la réponse manque : « ce bouton-**là** » ne se résout pas. L'`INDEX.md` est écrit comme preuve. Lancer `--autotest`. |

## Si ça semble cassé

⛔ Ne pas conclure que l'outil est brisé — le prouver :

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/regarder.py" --autotest
```

7 phases, ~3 min. Il **fabrique lui-même** une vidéo parlée et vérifie qu'il la réentend,
que les refus mordent, que le marqueur INVENTÉE attrape le souffle sans attraper la
parole, que deux voix simultanées reviennent chacune sur sa piste, et qu'une réplique
commence avec la voix et non avec la fenêtre de 30 s du modèle — et que **le 2e moteur
de voix**, celui que cette machine n'utilise pas par défaut, rend la phrase lui aussi.
`7/7` = l'outil est sain,
le problème est ailleurs (le fichier, la langue, le dossier de sortie).

⚠️ **Sauf UN cas, et il ne ressemble pas à lui-même : le bac à sable.** Si l'agent tourne
dans un mode restreint, le moteur de voix ne voit pas la puce graphique et rend
`No Metal device available` — mesuré le 14 sept. 2026. Ce n'est pas l'outil qui est
cassé, c'est l'accès au matériel : le lancer **hors bac à sable**. ⛔ Et si `--autotest`
répond `⚪ NON CONCLUANT` au lieu de `7/7`, ce n'est **pas** un échec non plus : il manque
de quoi sur la machine (la voix `Thomas`, ou `say`). « Non rejoué » et « cassé » sont deux
choses, et l'autotest les dit séparément.
⛔ **Hors macOS (Linux, WSL2), c'est STRUCTUREL et définitif : `say` n'existe pas, donc
l'autotest n'y sera JAMAIS vert.** Ne pas chercher quoi installer — il n'y a rien à
installer. La preuve, là-bas, c'est la première vraie vidéo : la phrase revient et
l'`INDEX.md` nomme son moteur.

## Mettre à jour

⛔ **Rien ne se met à jour tout seul.** Ton dossier reste sur la version que tu as
clonée, aussi longtemps que tu ne vas pas chercher la nouvelle. Pour la prendre :

```bash
cd ~/regarder && git pull
```

Puis, une fois, pour vérifier que tout tient encore chez toi :

```bash
python3 scripts/regarder.py --autotest
```

> ⚠️ **Si `git pull` refuse** en parlant d'historiques qui ont divergé, ce n'est pas un
> bug : l'historique a été réécrit en amont. Reprends la version en ligne telle quelle —
> ⛔ ça efface tes modifications locales dans ce dossier, s'il y en a :
>
> ```bash
> cd ~/regarder && git fetch origin && git reset --hard origin/main
> ```
>
> Pas besoin de relancer l'installeur : ce qui est installé dans `~/.venvs/transcription`
> reste bon.

## Ce que ça demande sur la machine

`./installer.sh` une seule fois — il choisit le moteur tout seul.

| Ta machine | Moteur de voix | Vitesse |
|---|---|---|
| **Mac Apple Silicon** (M1 et plus) | `mlx-whisper`, sur la puce graphique | la plus rapide |
| **Mac Intel** | `faster-whisper`, sur le processeur | **~10× plus lent**, complet |
| **Linux** | `faster-whisper` | **~10× plus lent**, complet |
| **Windows** → **WSL2** | `faster-whisper` (WSL2, c'est du Linux) | **~10× plus lent**, complet |
| **Windows natif** | ⛔ refusé, et l'outil dit quoi faire | — |

⏱ **« ~10× plus lent » veut dire quoi, concrètement ?** Sur Apple Silicon, une vidéo de
5 minutes se transcrit en une poignée de secondes ; sur processeur, compte **quelques
minutes**. C'est utilisable, mais ce n'est pas instantané — et c'est écrit ici parce
qu'un silence de plusieurs minutes se lit comme un blocage, et on tue la commande.

L'installeur **choisit tout seul** : rien à décider. Les deux moteurs sont gratuits, hors
ligne, **sans aucune clé API**.

⭐ **Le moteur retenu est IMPRIMÉ à chaque transcription** (`· piste 1 transcrite par …`) et écrit dans
l'`INDEX.md`. ⛔ Un repli silencieux serait le défaut que cet outil combat, sous un autre
nom : deux moteurs n'ont ni la même vitesse ni exactement la même sortie, et un transcript
ne porte aucune trace de ce qui l'a produit.

⛔ **Pourquoi Windows natif est refusé — et ce n'est PAS le moteur de voix.** `regarder.py`
tient ses garanties d'écriture (ne jamais écraser un fichier qui n'est pas à lui, ne jamais
suivre un lien, détecter un fichier substitué **pendant** le travail) avec **49 appels
POSIX** répartis sur 18 fonctions — `dir_fd`, `O_NOFOLLOW`, `O_DIRECTORY`. Rien de tout ça
n'existe sur Windows. Les remplacer voudrait dire livrer des gardes **jamais testés**, et
c'est précisément ce que cet outil existe pour empêcher.
👉 **WSL2 n'est pas un contournement, c'en est la vraie réponse** : c'est du Linux, donc
l'outil au complet, sans une ligne en moins. Dans PowerShell en administrateur :
`wsl --install`, puis relancer l'installeur dans le terminal Ubuntu.
