# /regarder

**Ton Claude entend ta vidéo en même temps qu'il la voit.**

> Tu enregistres ton écran en parlant par-dessus — « ce bouton-**là**, monte-le » — et tu
> envoies le `.mov`. Le mot « là » n'existe que dans l'image. Le geste n'existe que dans le
> son. `/regarder` rend les deux **alignés** : chaque phrase que tu dis porte l'écran de la
> fraction de seconde où tu l'as dite.

**Transcription 100 % locale** — `mlx-whisper` sur la puce graphique. Gratuit, hors ligne,
**aucune clé API**, rien qui sort de la machine.

---

## Le problème que ça règle

Les outils de type `/watch` prennent **les sous-titres natifs en premier** et transcrivent
ensuite par **API Whisper**. Or :

1. un screen record n'a **jamais** de sous-titres intégrés ;
2. sans clé API, l'outil retombe donc sur les **images seules** ;
3. et il le **dit** sur stderr et dans une note du rapport — mais il rend **code 0** et un **rapport d'allure complète**. Un `$?` et une lecture en diagonale passent tous les deux. ⭐ Et ce n'est pas qu'une affaire de clé manquante : `whisper.py` lève « no transcript segments », `watch.py` **attrape** l'exception et la dégrade en une ligne stderr — **même avec une clé valide, un Whisper qui ne rend rien sort en code 0**. Le transcript n'est jamais une condition de succès.

⛔ **Un rapport sans le son se lit exactement comme un rapport réussi.** C'est le pire genre
de défaut : l'outil répond, il ne bloque pas, et il a sauté la moitié de la question. Tu
t'en aperçois trois échanges plus tard, quand la réponse est à côté.

Ici, l'absence de son est un **refus bruyant** avec un code de sortie distinct — jamais un
rapport muet.

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


## Installation

```bash
git clone https://github.com/JNGEE4CHRIST/regarder.git ~/regarder
cd ~/regarder && ./installer.sh
```

L'installeur met `ffmpeg` (par le gestionnaire de paquets de TA machine : Homebrew sur Mac,
apt/dnf/pacman sur Linux) et un Python à part dans `~/.venvs/transcription`, avec **le moteur
de voix qui convient à ta machine** — il le choisit tout seul (tableau ci-dessous). Il ne
touche à rien d'autre.

> ⏳ **La PREMIÈRE vidéo est lente, et c'est normal :** le modèle de voix (~1,5 Go) se
> télécharge à ce moment-là, pas à l'installation. Quelques minutes de silence apparent,
> une seule fois — ensuite il est en cache et tout est hors ligne. ⚠️ C'est écrit ici
> parce que sans l'avoir lu, ce silence se lit comme un blocage, et on tue la commande.

### Sur quelles machines ça marche

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

### Le brancher à Claude Code

```
/plugin marketplace add JNGEE4CHRIST/regarder
/plugin install regarder@regarder
```

Ou, sans passer par les plugins :
```bash
git clone https://github.com/JNGEE4CHRIST/regarder.git ~/.claude/skills/regarder
```

### Le brancher à Codex

```bash
git clone https://github.com/JNGEE4CHRIST/regarder.git ~/regarder
mkdir -p ~/.codex/skills/regarder
cp ~/regarder/codex/SKILL.md ~/.codex/skills/regarder/SKILL.md
```

Puis brancher le déclencheur — **sans lui, Codex ne sait pas QUAND aller chercher le
skill, et l'outil n'existe pas pour lui** :

```bash
~/regarder/codex/bloc-agents.sh >> ~/.codex/AGENTS.md
```

Le script écrit le bloc avec **le chemin réel de ton clone**, et refuse s'il y en a déjà
un (pas de doublon silencieux : deux blocs se lisent tous les deux comme la vérité).

#### S'en servir avec Codex

Il n'y a pas de commande `/regarder` côté Codex — c'est un appel shell, et le skill le
dit à l'agent :

```bash
python3 ~/regarder/scripts/regarder.py "/chemin/video.mov" --sortie /tmp/regard/essai
```

Puis **lire `/tmp/regard/essai/INDEX.md` ET ouvrir l'image de chaque réplique**. Le
transcript seul ne résout pas « ce bouton-**là** » : c'est la paire qui répond.

⚠️ **Hors bac à sable.** Le moteur de voix a besoin de la puce graphique, que le bac à
sable de Codex ne laisse pas voir (`No Metal device available`, mesuré le 14 sept. 2026).
⛔ Et `/watch`, vers quoi la table d'aiguillage renvoie deux cas, est un skill **Claude** :
ce que ça change pour un utilisateur Codex est écrit dans `codex/SKILL.md`.

## Le prouver avant de s'en servir

⛔ **« Installé » n'est pas « ça marche ».** Un garde qu'on n'a jamais vu mordre ne garde
rien :

```bash
python3 scripts/regarder.py --autotest
```

7 phases, ~3 minutes. Il **fabrique lui-même** une vidéo parlée et vérifie qu'il la
réentend. Ce qu'il prouve, une phase à la fois :

| # | Ce qu'il casse exprès | Ce qui doit tenir |
|---|---|---|
| 1 | — | la voix revient, et l'écran attaché est bien celui de l'instant |
| 2 | images à cadence variable | la bonne image est **celle d'avant** la phrase, jamais celle d'après |
| 3 | dossier de sortie qui n'est pas à lui | il refuse **avant** de toucher un seul octet |
| 4 | souffle de micro et silence | marqués 🚫 **INVENTÉE** — et la parole faible ne l'est **pas** |
| 5 | deux voix en même temps | les deux reviennent, chacune sur sa piste |
| 6 | une phrase après 30 s de silence | datée sur la **voix**, pas sur la fenêtre du modèle |
| 7 | le moteur de l'AUTRE plateforme, forcé | la phrase revient **et** le moteur se nomme dans l'INDEX |

`7/7` = l'outil est sain. S'il échoue quand même sur ta vidéo, le problème est ailleurs
(le fichier, la langue, le dossier de sortie) — pas dans l'outil.

> ⚠️ **Hors macOS (Mac Intel excepté), l'autotest est TOUJOURS « ⚪ NON CONCLUANT », et
> c'est normal.** Il fabrique lui-même la voix qu'il doit réentendre avec `say`, qui
> n'existe que sur Mac. Sur Linux et WSL2 il s'arrête proprement en le disant, **sans
> jamais rendre un faux vert** — mais il ne deviendra pas vert non plus, peu importe
> combien de fois tu le relances. **Ta preuve, là-bas, c'est ta première vraie vidéo :**
> si la phrase revient et que l'`INDEX.md` nomme son moteur, l'outil fait sa job.

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

## S'en servir

```
/regarder ~/Desktop/modifs-accueil.mov liste-moi toutes les modifications demandées
```

Ça sort un `INDEX.md` où chaque réplique porte son `[mm:ss]` et **le chemin de l'écran de
ce moment-là**. Ce que ton Claude doit te rendre ensuite :

- une **case à cocher par demande**, dans l'ordre où elles sont dites ;
- l'**horodatage** et la **citation** de ce que tu as dit ;
- **ce qui est à l'écran** à cet instant — c'est ça qui lève l'ambiguïté quand tu dis
  « ça » ou « ce bout-là » ;
- ⛔ **rien d'inventé** : une demande inaudible s'écrit **À CLARIFIER**, elle ne se devine
  pas. Une modification devinée coûte plus cher qu'une question.

En ligne de commande directement :

```bash
python3 scripts/regarder.py "<video>" --sortie /tmp/regard/essai-$(date +%H%M%S)
```

| Drapeau | Ce que ça fait |
|---|---|
| `--sortie <dossier>` | dossier **neuf** où écrire. Il refuse d'écrire dans un dossier qui n'est pas à lui (code 2) — il n'effacera jamais tes fichiers. |
| `--langue fr\|en` | ⛔ **ne se devine pas.** Forcer `fr` sur de l'anglais rend un texte **plausible et faux**, horodatages corrects. Dans le doute : `--essai-langue`, et on compare. |
| `--images N` | combien d'écrans extraire. Monte si l'interface est dense en texte. |
| `--essai-langue [N]` | ⭐ **la commande qui tranche `--langue`.** Transcrit les N premières secondes (90 par défaut) en **fr ET en en**, côte à côte, puis s'arrête — aucun index, aucun fichier touché. La bonne langue est celle qui rend des MOTS. |
| `--autotest` | le contrôle positif ci-dessus. |

## Les codes de sortie

Les trois premiers se lisent tous « la vidéo ne dit rien », et n'ont **pas** le même
correctif — c'est précisément pour ça qu'ils sont séparés :

| Code | Sens | Quoi faire |
|---|---|---|
| `0` | OK | lire l'`INDEX.md` |
| `2` | dossier de sortie pas à lui, ou fichier introuvable | donner un dossier neuf |
| `7` | **la machine n'est pas équipée** (ffmpeg absent) | `./installer.sh` |
| `3` | **aucune piste audio** — l'écran a été capturé sans le micro | rien à sauver, refaire la vidéo |
| `4` | **pistes muettes** — micro fermé ou mauvaise entrée | refaire la vidéo |
| `5` | **transcript vide** malgré du son | vrai défaut : lancer `--autotest` |
| `6` | aucune piste vidéo | rien à montrer |
| `8` | **aucun écran rendu** — transcript obtenu, zéro image | la moitié de la réponse manque : « ce bouton-**là** » ne se résout pas. L'`INDEX.md` est écrit comme preuve. Lancer `--autotest`. |

⚠️ **Si l'installeur n'a pas été lancé**, l'outil sort en `2` avec le message exact à
suivre (`mlx_whisper n'est pas installé dans … · Lancer : <chemin>/installer.sh`) et
**n'écrit aucun rapport** — pas d'`INDEX.md`, pas d'images. Mesuré sur un clone neuf le
20 septembre 2026. ⛔ C'est voulu : un rapport sans le son serait exactement le défaut
que cet outil corrige.

Le code `4` existe parce que **Whisper hallucine des phrases sur du silence**, avec des
horodatages corrects — indiscernables d'un vrai transcript à la lecture. On refuse **avant**
de le lancer plutôt que de rendre un texte inventé.

## Ce qu'il y a dedans

| Fichier | Rôle |
|---|---|
| `scripts/regarder.py` | tout l'outil : découpe, alignement, gardes, autotest |
| `scripts/transcription.py` | le moteur de voix (mlx-whisper). **Extrait automatiquement**, ne pas éditer à la main |
| `scripts/transcrire-fichier.py` | le pont vers l'environnement Python du moteur. **Propre à ce paquet** (voir la note sur la source) |
| `SKILL.md` · `commands/regarder.md` | le skill Claude |
| `codex/` | le skill Codex + la ligne à coller dans `AGENTS.md` |
| `installer.sh` | ffmpeg + le moteur, une fois |

## Note sur la source

Ce dépôt est un **miroir**, pas une deuxième version. La source de vérité vit dans le
dépôt d'outils de JNT Productions, et un script de publication régénère ce paquet à partir
d'elle. Une correction se fait dans la source, puis on republie.

⚠️ **Précisément : DEUX des trois scripts sont régénérés**, `regarder.py` et
`transcription.py`. `transcrire-fichier.py` est **propre à ce paquet** — la version maison
importe le moteur d'un fichier qui n'existe pas ici, alors que celle-ci est autonome. Ce
n'est donc pas une copie qui a dérivé, c'est un fichier différent **par construction**, et
il se corrige ici. ⛔ C'est écrit parce que « le paquet est régénéré » tout court était
**faux pour un tiers des scripts** — et une note de maintenance fausse envoie corriger au
mauvais endroit, ce qui coûte plus cher que pas de note du tout.

⛔ **Pourquoi ça compte :** deux copies modifiées chacune de leur bord **marchent toutes les
deux**. Elles ne font juste plus la même chose — et on l'apprend le jour où un défaut n'est
corrigé que d'un côté. La copie est donc **dérivée**, jamais parallèle.

## Pourquoi ça existe

Écrit les 11 et 12 septembre 2026, après trois revues de code, parce que les deux moitiés
de la réponse vivaient déjà sur le Mac et ne se parlaient pas : le **son** (`mlx-whisper`,
déjà installé pour transcrire des appels) et l'**écran** (`ffmpeg`). Il manquait le pont.

Quelques défauts qui ont été mesurés et corrigés en chemin, tous invisibles à la lecture :

- **Un screen record macOS est à images variables.** Mesuré : 2 554 images pour 52 s
  annoncées « 60 i/s », avec des trous de 1,2 s quand l'écran ne bouge pas. `ffmpeg -ss t`
  rend la première image **≥ t** — donc, dans un trou, l'écran d'**après** le prochain
  changement. « Ce bouton-là » désignait alors un écran pas encore affiché. Corrigé : on lit
  les horodatages réels et on vise la **dernière image ≤ t**, puis on **vérifie** celle que
  ffmpeg a rendue.
- **Deux pistes audio se masquent.** Mélangées, Whisper ne garde que la voix la plus forte,
  et l'instruction dite par-dessus une vidéo disparaissait **sans un mot**. Chaque piste se
  transcrit donc séparément.
- **`no_speech_prob` ne détecte pas les hallucinations.** On l'a cru, puis mesuré sur 9
  « Merci. » inventés sur 290 s de silence : **0,000 sur chacun**, identique aux vraies
  répliques. Le modèle ne sait pas qu'il invente. L'hallucination se mesure à l'amplitude,
  contre le plancher de bruit du fichier.
- **La fenêtre de 30 s du modèle fausse les débuts.** Sans horodatage au mot, une phrase
  dite à 32,1 s était datée 30,0 s — et l'écran attaché était celui de la section d'avant.

---

MIT © 2026 JNT Productions
