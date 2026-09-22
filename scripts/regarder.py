#!/usr/bin/env python3
"""
REGARDER — je VOIS et j'ENTENDS un screen record de JNT, d'une seule commande.

⛔ LE TROU QU'IL BOUCHE, NOMMÉ LE 11 SEPTEMBRE 2026. JNT envoie ses modifications de site
en screen record, en PARLANT par-dessus l'écran. Les deux moitiés existaient déjà sur le
Mac et ne se parlaient pas :
  · le SON  → `mlx-whisper` local (ghl-appel.py), gratuit, hors ligne, déjà installé ;
  · l'IMAGE → ffmpeg.
Sans pont entre les deux, je lisais soit le texte sans savoir de QUOI il parle, soit des
images sans savoir ce qu'il en DIT. Or une demande de modification vit exactement dans
l'intersection : « ce bouton-LÀ, monte-le ». Le mot « là » n'existe que dans l'image.

⛔⛔ POURQUOI PAS `/watch`. Le skill claude-watch transcrit par API SEULEMENT (Groq/OpenAI,
   voir scripts/whisper.py) : sans clé, il retombe sur les sous-titres natifs, qu'un screen
   record n'a JAMAIS, et rend alors les images EN SILENCE, sans erreur. Un rapport
   frames-only se lit exactement comme un rapport réussi. Ici, l'absence de son est un
   REFUS BRUYANT (code 3), jamais un rapport muet.

⭐ IL NE RECOPIE AUCUNE LOGIQUE DE TRANSCRIPTION. Il appelle `appel/transcrire-fichier.py`,
   qui importe `transcrire()` de `ghl-appel.py` — même modèle, même sortie horodatée, même
   venv. Une 2e copie divergerait en silence.
   ⛔ NE PAS ÉCRIRE QUE `derive-check.py` PROTÈGE ÇA — vérifié le 11 sept. 2026 : il
   inventorie les OFFRES ET FACTURES, pas le code. Une copie de `transcrire()` ajoutée
   exprès ne l'a pas fait bouger d'un chiffre. La centralisation tient parce qu'elle est
   écrite ici, PAS parce qu'un gate la garde.

── LES TROIS SILENCES QU'IL REFUSE DE CONFONDRE ────────────────────────────────
Ils se lisent tous « la vidéo ne dit rien », et ils n'ont pas le même correctif :
  code 3 · AUCUNE PISTE AUDIO      → l'écran a été capturé sans le micro. Rien à sauver.
  code 4 · PISTES AUDIO MUETTES    → micro fermé ou mauvaise entrée (crête < -45 dB sur
                                      TOUTES les pistes). ⚠️ Whisper HALLUCINE des phrases
                                      sur du silence, avec des horodatages corrects :
                                      indiscernable d'un vrai transcript à la lecture.
                                      On refuse AVANT de le lancer.
  code 5 · TRANSCRIPT VIDE         → il a parlé, le modèle n'a rien rendu. Vrai défaut.
Et deux refus qui ne parlent pas du son :
  code 6 · AUCUNE PISTE VIDÉO      → rien à montrer, donc aucun « ça » ne se résout.
  code 2 · `--sortie` VISE UN DOSSIER QUI N'EST PAS À MOI → on n'efface pas les fichiers
                                      de JNT. Le dossier se reconnaît à son marqueur
                                      `.regarder`, écrit par cet outil et par personne d'autre.

── LES DEUX PIÈGES QUI NE PLANTENT PAS (revue « repli Claude », 11 sept. 2026) ──
  · UNE VOIX PAR PISTE. Un screen record avec le son du système ET le micro porte DEUX
    pistes. Mélangées (`amix`), les deux voix se MASQUENT : Whisper ne garde que la plus
    forte, et l'instruction de JNT, dite par-dessus une vidéo du site, disparaissait sans
    un mot. Chaque piste se transcrit donc SÉPARÉMENT, et l'INDEX dit laquelle a parlé.
  · L'HALLUCINATION SE MESURE CONTRE LE PLANCHER DU FICHIER, pas contre un chiffre fixe.
    Voir `segments_muets`.

── L'ÉCRAN DE L'INSTANT t EST LA DERNIÈRE IMAGE AVANT t, PAS LA PREMIÈRE APRÈS (3e revue
   Codex, 12 sept. 2026) ─────────────────────────────────────────────────────────────
   Un screen record macOS est à IMAGES VARIABLES : mesuré sur la vidéo réelle du 11 sept.,
   2 554 images pour 52 s annoncées « 60 i/s », avec des TROUS de 1,2 s quand l'écran ne
   bouge pas. `ffmpeg -ss t` rend la première image dont l'horodatage est ≥ t — donc, dans
   un trou, l'écran d'APRÈS le prochain changement. Codex l'a mesuré : demandé 1,00 s, rendu
   l'image de 1,96 s. « Ce bouton-là » désignait alors un écran que JNT n'avait pas encore
   vu. On lit donc les horodatages RÉELS des images (`instants`) et on vise la dernière ≤ t.
   ⭐ Et depuis la 4e revue (même jour), CHAQUE image rendue est VÉRIFIÉE : ffmpeg dit
   l'horodatage de l'image qu'il a rendue (`showinfo`), et on le compare à celui visé.
   ⚠️ DEUX HORLOGES SUR UN MÊME FICHIER, mesuré sur la vidéo réelle : à 45,667 s deux
   images portent le MÊME horodatage, et à partir de là `ffprobe -show_frames` rend un
   `best_effort_timestamp` égal au DTS (0,617 s en retard) au lieu du PTS. Le lecteur, le
   son et `ffmpeg -ss` suivent le PTS du conteneur — c'est lui qu'on lit sur les paquets.
   Une référence bâtie sur `best_effort` (celle de Codex) accuse alors deux écrans justes.
   Et une vidéo dont l'horloge ne part pas à 0 (`start_time`) se lit en RELATIF : `-ss`
   compte depuis `start_time`, jamais depuis 0.
   ⛔⛔ ET LE DOUBLON DE 45,667 s TROMPAIT AUSSI `-ss` (5e revue Codex, même jour) : à partir
   de lui, le décodeur h264 étiquette 32 images avec leur DTS, et une recherche précise sur
   45,667 les jette comme « trop tôt » — elle rendait l'image nº 2303 pour la nº 2271, avec
   une étiquette juste par coïncidence. Donc ON NE CHERCHE PLUS UNE IMAGE PAR SON
   HORODATAGE : on la COMPTE depuis l'image-clé précédente (`rendre`), l'ordre de décodage
   étant la seule chose que le doublon ne casse pas (mesuré : 81 images du GOP, 1:1).
   ⚠️ LE WAV NE COMPTE PAS DEPUIS `start_time`, MAIS DEPUIS LA PREMIÈRE IMAGE AUDIO
   (5e revue Codex). ffmpeg n'ajoute pas de silence en tête : sur la vidéo réelle, le son
   part 61 ms après l'image ; sur le banc de Codex, 0,7 s. Whisper compte donc depuis le
   début du SON, et chaque réplique se recale de (début audio − start_time) avant de
   chercher son écran. Le début du son se lit (`ashowinfo`), il ne se suppose pas.

── RIEN NE S'ÉCRIT NI NE S'EFFACE PAR SON NOM (4e revue Codex, 12 sept. 2026) ──────────
   Le dossier de sortie se tient par son DESCRIPTEUR (`tenir`), et chaque fichier s'y ouvre
   RELATIVEMENT à lui, sans jamais suivre un lien (`O_NOFOLLOW`). Codex a prouvé qu'entre un
   contrôle et une écriture par chemin, un `ecrans` renommé ou un `transcript.txt` remplacé
   par un lien envoyait mes octets — ou mon `unlink` — chez JNT. Le WAV et les transcripts
   naissent dans un dossier PRIVÉ et n'entrent dans le dossier de sortie que par ces
   descripteurs. Et un lien posé à un nom inscrit au registre fait REFUSER (code 2) avant la
   première suppression : ce n'est plus « sauté », c'est la preuve d'une altération.
   ⭐ 5e revue Codex (12 sept. 2026) — trois « entre » de plus fermés :
   · `--sortie` se tient UNE fois (`tenir`, `O_NOFOLLOW`), et la preuve de propriété, le
     nettoyage et l'écriture passent par ce même descripteur. Un `islink()` PUIS un `tenir()`
     par chemin laissaient une fenêtre entre les deux.
   · le dossier PRIVÉ aussi : ffmpeg et le transcripteur y écrivent par nom relatif, leur
     répertoire courant étant son descripteur (`fchdir`). Son chemin remplacé par un lien
     pendant le run n'envoie plus le WAV chez JNT.
   · le registre porte une SIGNATURE (`ENTETE`) : un `.regarder` que JNT aurait nommé
     lui-même n'est pas une preuve. Et un transcripteur qui écrit son JSON puis plante
     (code ≠ 0) ne compte pas : c'est un refus, rien n'est copié.
   ⭐ 7e revue Codex (12 sept. 2026) — cinq « par nom » de plus fermés, et un aveu :
   · le REGISTRE s'écrit par le descripteur ouvert à sa création (`Registre`), plus jamais
     rouvert par nom : remplacé pendant le run par un lien physique vers une note de JNT, mes
     lignes partaient dans la note. Et on écrit PUIS on inscrit (`deposer`) : un refus
     d'écriture ne laisse plus une ligne pour un fichier qui n'est pas à moi.
   · le NETTOYAGE garde chaque fichier vérifié OUVERT, compare l'inode du nom à celui du
     fichier vérifié juste avant `unlink`, et RELIT le fichier effacé par son descripteur :
     remplacé entre le contrôle et l'effacement → refus, celui de JNT reste ; modifié entre
     les deux → restauré tel quel et refus. La fenêtre lstat→unlink qui reste est celle de
     POSIX (pas d'`unlink` par inode) ; elle est écrite dans `nettoyer`, pas cachée.
   · le DOSSIER PRIVÉ : le WAV est créé par moi (`O_EXCL`) et ffmpeg l'écrit À TRAVERS mon
     descripteur (`/dev/fd/N`), jamais par nom ; les sorties du transcripteur doivent être
     ABSENTES avant qu'il parte et sont relues par inode ; l'effacement compare l'inode.
   · l'INDEX dit « écran d'APRÈS » quand aucune image n'existe à l'instant d'une réplique
     (vidéo dont l'image commence après le son) : l'écran rendu est le premier d'APRÈS, et
     il ne prouve rien sur ce qui était visible AVANT.
   · l'aveu : le contrôle `st_nlink` d'`ecrire` n'avait jamais été vu bloquer (mutant
     aveugle). La sonde « fichier-cree » le prouve maintenant.

── USAGE ───────────────────────────────────────────────────────────────────────
  python3 scripts/regarder.py <video.mov> [--langue fr] [--images 36]
  python3 scripts/regarder.py --autotest      # se prouve tout seul (7 phases)

  Rend un dossier avec `INDEX.md` : chaque ligne de parole, son horodatage, et
  L'IMAGE DE L'ÉCRAN à cet instant-là. C'est l'INDEX.md que je lis.

⛔ `--langue` NE SE DEVINE PAS. Le défaut est `fr` (les screen records de JNT), et le choix
   est IMPRIMÉ à chaque run. Forcer la mauvaise langue ne rate pas bruyamment : Whisper rend
   un texte plausible et faux, horodatages corrects, et la modification se bâtit dessus.
"""
import argparse, bisect, hashlib, io, json, math, os, re, secrets, shutil, stat, subprocess, sys, tempfile, time
import threading
from concurrent.futures import ThreadPoolExecutor

ICI = os.path.dirname(os.path.abspath(__file__))
# Deux dispositions acceptées, dans cet ordre : le paquet autonome (ce dépôt), puis
# la disposition du dépôt source où l'outil est né. Un seul fichier, aucune copie
# de la logique de transcription — voir `scripts/transcription.py`.
TRANSCRIRE = next((c for c in (os.path.join(ICI, "transcrire-fichier.py"),
                               os.path.join(ICI, "appel", "transcrire-fichier.py"))
                   if os.path.exists(c)), os.path.join(ICI, "transcrire-fichier.py"))
# 1280 px de large : un screen record à 512 px (le défaut de claude-watch) rend le TEXTE
# D'INTERFACE illisible — or c'est précisément ce qu'il faut lire pour situer la demande.
LARGEUR = 1280
# ⛔ SEUIL SUR LA CRÊTE, PAS SUR LA MOYENNE (revue Codex, 11 sept. 2026) : une voix
#    réelle mais faible tombait à -50,8 dB de MOYENNE et se faisait refuser, alors
#    qu'elle se transcrit très bien. Un silence numérique plafonne vers -91 dB.
SEUIL_CRETE_DB = -45.0
# Une réplique est « entendue sur du silence » si sa fenêtre ne monte pas à plus de
# 8 dB au-dessus du plancher de bruit DU FICHIER. Mesuré le 12 sept. 2026 : les vraies
# répliques de JNT montent de 14,8 à 25,3 dB au-dessus du plancher ; les « Merci. »
# inventés par Whisper, de 0,0 à 1,2 dB. Le seuil est au milieu du trou, pas sur un bord.
SEUIL_DESSUS_PLANCHER_DB = 8.0
# …et jamais au-dessus de -30 dBFS : à ce niveau-là, quel que soit le plancher, il y a
# quelque chose dans le micro, et « inventée » serait un mensonge.
PLAFOND_MUET_DBFS = -30.0
# ⛔ LE PLANCHER SE LIT AUTOUR DE LA RÉPLIQUE, PAS SUR LE FICHIER ENTIER (revue Codex du
#    12 sept. 2026). Sur un souffle atténué de 20 dB au milieu de la vidéo puis rétabli,
#    le plancher GLOBAL tombait à -63,9 dBFS et 6 « Merci. » sur 9, inventés sur un souffle
#    à -43 dBFS, passaient pour dits. On lit donc la MÉDIANE des crêtes sur ±5 s autour de
#    chaque réplique : c'est le bruit de CE moment-là.
VOISINAGE_S = 5.0
# ⛔ 11e revue Codex (12 sept. 2026) : un `fin` de 1e308 passait `math.isfinite`, puis
#    `fin / 0,1` devenait l'infini dans `segments_muets` (OverflowError, trace d'appel,
#    code 1), et un entier de 400 chiffres faisait lever `math.isfinite` lui-même. Un
#    horodatage de vidéo tient sous 1e9 secondes (31 ans) : au-delà, ce n'en est pas un.
#    ⚠️ Ce plafond remplace `math.isfinite` : NaN et ±inf ne sont dans aucun intervalle.
PLAFOND_SECONDES = 1e9
# ⛔ LE MARQUEUR EST UN REGISTRE, PAS UN DRAPEAU (2e revue Codex, 12 sept. 2026). Il liste,
#    chemin par chemin, ce que J'AI écrit dans ce dossier — et `nettoyer()` n'efface QUE ce
#    qui y est inscrit. Effacer « par nom » (tout `transcript.txt`, tout `ecrans/ecran-*.jpg`)
#    détruisait un `transcript.txt` de JNT, une image derrière un lien `ecrans` vers SON
#    dossier, et une vidéo que JNT avait nommée `ecrans/ecran-001.jpg`. Un nom n'est pas une
#    preuve de propriété ; une ligne écrite par moi au moment où j'écris le fichier, oui.
MARQUEUR = ".regarder"
CACHE = os.path.expanduser("~/.cache/jnt-regard")
# Les noms que cet outil écrit. Un fichier qui porte un de ces noms SANS être au registre
# n'est pas à moi : je refuse (code 2) plutôt que de l'écraser.
MES_FICHIERS = re.compile(r"^(INDEX\.md|transcript(-piste-\d+)?\.(txt|json)|audio-\d+\.wav|ecrans/ecran-\d+\.jpg)$")
# ⭐ LA PREMIÈRE LIGNE DU REGISTRE EST SA SIGNATURE (5e revue Codex, 12 sept. 2026). Un fichier
#    que JNT aurait nommé `.regarder` lui-même (vide, une note) n'est pas mon registre : sans
#    cette phrase EXACTE en tête, le dossier n'est pas à moi → code 2, rien touché. Avant, la
#    seule EXISTENCE d'un fichier ordinaire à ce nom valait signature.
ENTETE = ("registre de regarder.py — les fichiers listés ici sont les SEULS qu'il effacera "
          "au prochain run")
# ⭐ SONDE D'AUTOTEST. Quand elle est posée, `frames()` et `nettoyer()` l'appellent à des
#    instants précis (« ecrans-ouvert », « ecran-rendu », « fichier-cree », « avant-suppression »,
#    « avant-transcript », « wav-cree », « prive-cree ») : c'est là
#    que l'autotest substitue un dossier ou pose un lien — EXACTEMENT entre le contrôle et
#    l'écriture, là où Codex a mesuré ses fuites. Sans course, donc reproductible.
SONDE = None


def _sonde(etape, *info):
    if SONDE:
        SONDE(etape, *info)


def tenir(dossier):
    """Ouvre `dossier` par DESCRIPTEUR, sans suivre un lien. Tout ce que j'écris ou efface
    ensuite passe par ce descripteur : renommer, remplacer ou lier le dossier pendant le run
    n'envoie plus rien ailleurs. Refus (code 2) si ce n'est pas un dossier ordinaire."""
    try:
        return os.open(dossier, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as e:
        sortir(2, f"`{dossier}` n'est pas un dossier ordinaire à moi ({e.strerror}) — je n'y "
                  "écris pas et je n'y efface rien.")


class _Altere(Exception):
    """Un nom à MOI, dans MON dossier, qui existe déjà ou n'est pas un fichier ordinaire au
    moment d'écrire : levée par `ecrire` (dans un fil d'extraction ou dans le run principal),
    transformée en refus (code 2) par `frames` ou `construire`."""


def ecrire(dfd, nom, donnees):
    """Écrit `donnees` (octets) sous `nom` dans le dossier tenu par `dfd` — UN FICHIER NEUF,
    JAMAIS UN NOM QUI EXISTE (`O_EXCL`), jamais à travers un lien (`O_NOFOLLOW`).
    ⛔ 6e revue Codex (12 sept. 2026) : `O_NOFOLLOW` ne voit pas un lien PHYSIQUE. Un `ln`
      posé à `transcript.txt` vers un document de JNT partage son inode : l'ancien `O_TRUNC`
      vidait le document et y écrivait mon transcript, code 0. Avec `O_EXCL`, tout nom qui
      existe déjà à l'instant d'écrire — lien physique, lien symbolique, vrai fichier glissé
      là — fait REFUSER. Après `nettoyer`, aucun de mes noms n'existe ; un nom qui existe n'est
      donc pas à moi. Et le fichier créé se relit par son descripteur avant le premier octet :
      un fichier ordinaire, UN seul nom (`st_nlink`).
    ⚠️ 7e revue Codex (12 sept. 2026) : ce 2e contrôle n'avait jamais été vu bloquer (mutant
      aveugle). Honnêtement : un lien physique posé sur un inode que JE viens de créer partage
      MON contenu — il ne peut rien détruire de JNT, le garde est une ceinture de plus. La sonde
      « fichier-cree » (entre la création et le contrôle) le prouve quand même.
    Rend le `stat` du fichier créé (dev, inode) — c'est par lui qu'on le reconnaît ensuite.
    `nom` est un nom simple, jamais un chemin — un `/` serait un contournement."""
    assert "/" not in nom, nom
    try:
        fd = os.open(nom, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dfd)
    except OSError as e:
        raise _Altere(f"`{nom}` existe déjà ou n'est pas un fichier ordinaire à moi ({e.strerror}) "
                      "— je n'écris pas par-dessus. Donner un dossier neuf.")
    _sonde("fichier-cree", nom)
    with os.fdopen(fd, "wb") as f:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise _Altere(f"`{nom}` a {st.st_nlink} noms au moment d'écrire (un lien physique posé "
                          "pendant le run ?) — je n'écris pas.")
        f.write(donnees)
    return st


def sortir(code, msg):
    print(f"⛔ {msg}", file=sys.stderr)
    sys.exit(code)


def ffprobe(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,start_time:stream=codec_type",
         "-of", "json", video], capture_output=True, text=True)
    if r.returncode != 0:
        sortir(2, f"ffprobe refuse ce fichier : {r.stderr.strip()[:200]}")
    d = json.loads(r.stdout)
    duree = float(d.get("format", {}).get("duration") or 0)
    depart = float(d.get("format", {}).get("start_time") or 0)
    pistes = [s.get("codec_type") for s in d.get("streams", [])]
    return duree, pistes, depart


def niveaux(video, piste=0):
    """(moyenne, crête) en dB de la piste audio nº `piste` — PAS de la première seulement.
    ⛔ Sans `-map`, ffmpeg ne mesure que la piste par défaut : un micro muet sur la piste 2
    se lisait comme un fichier sain parce que la piste 1 (le son du système) chantait."""
    r = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", video, "-map", f"0:a:{piste}", "-vn",
         "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    def lire(cle):
        m = re.search(cle + r": (-?[\d.]+) dB", r.stderr)
        return float(m.group(1)) if m else None
    return lire("mean_volume"), lire("max_volume")


def pics_par_fenetre(wav, fenetre_s=0.1, nom=None):
    """La crête (en dBFS) de chaque tranche de 100 ms du WAV, dans l'ordre. None si illisible.
    `wav` : un chemin, ou un fichier déjà ouvert (ouvert par descripteur dans le dossier privé,
    5e revue Codex) — `nom` sert alors au message."""
    import wave, array
    try:
        with wave.open(wav) as w:
            n, taux = w.getnframes(), w.getframerate()
            ech = array.array("h"); ech.frombytes(w.readframes(n))
    except Exception as e:
        print(f"⚠️  amplitude NON MESURABLE sur {nom or os.path.basename(str(wav))} ({e}) — aucune "
              "réplique ne sera marquée inventée, ce qui ne veut PAS dire qu'aucune ne l'est.")
        return None
    pas = max(1, int(taux * fenetre_s))
    def dbfs(v): return 20 * math.log10(max(v, 1) / 32768)
    return [dbfs(max((abs(v) for v in ech[i:i + pas]), default=0))
            for i in range(0, len(ech), pas)], fenetre_s


def segments_muets(pics, segments):
    """Quelles répliques ont été « entendues » sur un passage SANS PAROLE ?

    ⛔⛔ LE DÉFAUT LE PLUS DANGEREUX DE L'OUTIL, TROUVÉ PAR LA REVUE CODEX DU 11 SEPT. 2026.
      Le garde de la crête juge la piste ENTIÈRE. Une vidéo de 5 min avec 20 s de parole
      et 4 min 40 de silence passe le seuil — et Whisper a rendu **9 « Merci. » inventés,
      un toutes les 30 s, de 00:30 à 04:30**, sur un passage dont l'amplitude maximale
      mesurée est **exactement 0**. Horodatages corrects, ponctuation correcte :
      **indiscernables de vraies répliques dans l'INDEX.**

    ⛔ ET LE PREMIER CORRECTIF ÉTAIT AVEUGLE EN PRODUCTION (revue « repli Claude », même
      jour). Il jugeait « muet » sous une amplitude FIXE (~-55 dBFS) — calibrée sur un
      silence de laboratoire. Un vrai micro ne descend jamais là : le passage le plus
      silencieux du screen record de JNT est à **-37 dBFS**. Sur 10 s de parole suivies de
      290 s de souffle de micro à -43 dBFS, le garde ne marquait **0 réplique sur 9**.
      👉 On ne compare donc plus à un chiffre : on compare au PLANCHER DE CE FICHIER-LÀ
      (le 5e centile des crêtes de 100 ms). Une réplique dont la fenêtre ne dépasse pas
      ce plancher de 8 dB n'a pas été dite.

    ⛔ CE QU'ON A ESSAYÉ ET QUI NE MARCHE PAS : `no_speech_prob` de Whisper. Mesuré le
      12 sept. 2026 sur les 9 « Merci. » inventés : **0,000 partout**, identique aux vraies
      répliques. Le modèle ne SAIT PAS qu'il invente. Le chiffre est dans le JSON de
      `transcrire()` pour qu'on puisse le revérifier, pas parce qu'il sert.

    ⚠️ On marque, on ne supprime pas : une réplique vraie mal mesurée serait perdue en
      silence, ce qui est le défaut qu'on répare, à l'envers.
    """
    if pics is None:
        return set()
    valeurs, fenetre = pics
    muets, planchers = set(), []
    for i, s in enumerate(segments):
        t, fin = s["debut"], max(s["fin"], s["debut"] + 1.0)
        tranche = valeurs[int(t / fenetre):int(fin / fenetre) + 1]
        # ⛔ PLANCHER LOCAL (revue Codex, 12 sept. 2026) : la médiane des crêtes sur ±5 s
        #    autour de la réplique. Un plancher lu sur le fichier ENTIER prenait la valeur
        #    du passage le plus calme, et le souffle des passages plus bruyants repassait
        #    pour de la parole — 6 hallucinations sur 9 acceptées.
        # ⚠️ Et il se lit sur les tranches où il y a UN SIGNAL (> -80 dBFS) : un bout de
        #    silence numérique tirerait le plancher à -90 dB, et le souffle de micro à
        #    -43 dB repasserait pour de la parole — vu au premier banc.
        voisin = valeurs[max(0, int((t - VOISINAGE_S) / fenetre)):int((fin + VOISINAGE_S) / fenetre) + 1]
        tri = sorted(v for v in voisin if v > -80.0)
        plancher = tri[len(tri) // 2] if tri else -90.0
        seuil = min(plancher + SEUIL_DESSUS_PLANCHER_DB, PLAFOND_MUET_DBFS)
        planchers.append(plancher)
        if tranche and max(tranche) < seuil:
            muets.add(i)
    if not planchers:
        planchers = [-90.0]
    return muets, min(planchers), max(planchers)


def instants(video):
    """Les horodatages RÉELS (PTS) de toutes les images de la vidéo, triés — lus sur les
    paquets, sans décoder (52 s → ~2 500 lignes, instantané). ⛔ C'est LA correction de la
    3e revue Codex (12 sept. 2026) : l'écran affiché à l'instant t est la DERNIÈRE image dont
    le PTS ≤ t, et `-ss t` seul rend la PREMIÈRE dont le PTS ≥ t. Sur une vidéo à images
    variables (tout screen record macOS), l'écart atteint la longueur du trou : 1,2 s mesuré.

    ⭐ RELATIFS À `start_time` (4e revue Codex, 12 sept. 2026). Sur une vidéo dont l'horloge
    part à 0,5 s, `ffmpeg -ss t` cherche t APRÈS start_time, et le WAV (donc Whisper) compte
    aussi depuis start_time : mesuré, un bip posé à 1,5 s absolu se lit à 1,0 s dans le WAV.
    Les PTS absolus des paquets, eux, partaient de 0,5 — et chaque écran arrivait 0,5 s trop
    tard. Tout se compte donc dans la même horloge : celle qui part à start_time.
    ⚠️ PAS `-show_frames` : son `best_effort_timestamp` bascule sur le DTS après un doublon de
    PTS (vu à 45,667 s sur la vidéo réelle : 0,617 s de retard jusqu'à la fin). Les paquets
    portent le PTS du conteneur, celui que le lecteur et `-ss` suivent.
    Rend ([], 0, []) si ffprobe ne lit rien — `frames` REFUSE alors (code 2), plutôt que de
    rendre l'écran d'après.

    ⭐ RENDU : (pts, depart, cles) — `cles` = les INDICES (dans `pts`) des images-clés, lus sur
    le drapeau `K` des paquets (5e revue Codex, 12 sept. 2026). C'est depuis l'image-clé
    précédente que `rendre` COMPTE les images, au lieu de les chercher par horodatage : voir
    `rendre` pour le doublon de PTS qui a rendu la recherche par horodatage fausse de 0,6 s."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "format=start_time:packet=pts_time,flags",
                        "-of", "csv=p=1", video], capture_output=True, text=True)
    pts, cles_pts, depart = [], [], 0.0
    for ligne in r.stdout.splitlines():
        champs = ligne.split(",")
        try:
            if champs[0] == "format":
                depart = float(champs[1])
            elif champs[0] == "packet":
                p = float(champs[1])
                pts.append(p)
                if "K" in champs[2]:
                    cles_pts.append(p)
        except (ValueError, IndexError):
            pass
    pts = sorted(p - depart for p in pts)
    cles = sorted({bisect.bisect_left(pts, p - depart) for p in cles_pts})
    return pts, depart, cles


def rendre(video, pts, depart, cles, k):
    """L'image nº k (dans l'ordre des PTS triés) en JPEG : (octets, None), ou (None, motif).

    ⛔⛔ ON NE CHERCHE PLUS UNE IMAGE PAR SON HORODATAGE, ON LA COMPTE DEPUIS L'IMAGE-CLÉ
      PRÉCÉDENTE (5e revue Codex, 12 sept. 2026). Mesuré sur la vidéo réelle du 11 sept. :
      à 45,667 s, DEUX paquets portent le même PTS (une image P de 214 Ko et une image B de
      3 Ko). À partir de là, le décodeur h264 perd son horloge et étiquette les 32 images
      suivantes avec leur DTS (45,05 → 46,05 s) au lieu de leur PTS (45,67 → 46,28 s), jusqu'à
      l'image-clé suivante. Une recherche `-ss 45,667` jetait donc ces 32 images « trop tôt »
      et rendait l'image nº 2303 — étiquetée 45,667 par coïncidence, donc VÉRIFIÉE JUSTE —
      pour la nº 2271 : 0,6 s de retard, code 0, contrôle passé. Toute réplique entre le
      doublon et l'image-clé suivante recevait le mauvais écran.
      👉 Ce qui reste vrai quand les étiquettes mentent, c'est L'ORDRE. Mesuré : décodé depuis
      l'image-clé nº 2245, la ne image décodée est EXACTEMENT la nº 2245+n, sur les 81 images
      du GOP, doublon compris. Donc : `-ss` sur l'image-clé (`-noaccurate_seek` : ffmpeg part
      de l'image-clé et ne jette rien), `select=eq(n, k−j)`, et `showinfo` AVANT `select` pour
      relire chaque image décodée jusqu'à la cible.
    ⭐ CE QUI EST VÉRIFIÉ, ET CE QUI NE PEUT PAS L'ÊTRE. L'image 0 décodée doit être une
      image-clé (`iskey:1`) à l'horodatage d'une image-clé connue — sinon on ne sait pas d'où
      l'on compte, et on recale ou on refuse. Puis chaque étiquette est comparée au PTS attendu
      JUSQU'AU PREMIER DOUBLON de PTS : après lui, les étiquettes sont mesurées fausses
      (DTS), le compte seul fait foi. Avant un doublon, toute divergence → refus de CETTE image
      (`frames` vise alors la précédente, puis avoue). Jamais une image non vérifiée là où la
      vérification est possible ; jamais une image « à peu près » quand le compte est exact.
    ⚠️ Le coût est celui d'avant : `-ss` précis décodait DÉJÀ depuis l'image-clé."""
    j = cles[bisect.bisect_right(cles, k) - 1] if cles and cles[0] <= k else 0
    ss = pts[j]
    for _ in range(3):
        n = k - j
        r = subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostats", "-v", "info",
             "-ss", f"{ss + 0.0005:.4f}", "-noaccurate_seek", "-copyts", "-i", video,
             "-map", "0:v:0", "-vf", f"showinfo,select='eq(n\\,{n})',scale={LARGEUR}:-2",
             "-frames:v", "1", "-q:v", "3", "-f", "mjpeg", "pipe:1"], capture_output=True)
        lignes = [(float(t) - depart, cle == b"1") for t, cle in
                  re.findall(rb"\] n:\s*\d+ pts:\s*-?\d+ pts_time:\s*(-?[0-9.]+).*?iskey:(\d)",
                             r.stderr)]
        if not lignes:
            return None, f"ffmpeg n'a rien décodé depuis {ss:.3f} s"
        t0, cle0 = lignes[0]
        i0 = bisect.bisect_left(pts, t0 - 0.002)
        j0 = next((i for i in range(i0, min(i0 + 8, len(pts))) if abs(pts[i] - t0) <= 0.002
                   and i in cles), None)
        if j0 is None or not cle0:
            return None, (f"la 1re image décodée ({t0:.3f} s, {'clé' if cle0 else 'PAS une clé'}) "
                          "n'est pas une image-clé connue — je ne sais pas d'où compter")
        if j0 != j:
            if j0 <= k:
                j = j0                                  # atterri sur une autre clé ≤ cible : on recompte
            else:
                ss = pts[j] - 1.0                       # atterri APRÈS la cible : chercher plus tôt
            continue
        if r.returncode != 0 or not r.stdout or len(lignes) <= n:
            return None, f"ffmpeg n'a pas rendu la {n}e image après l'image-clé {j} ({len(lignes)} décodées)"
        for i in range(n + 1):
            if i > 0 and pts[j + i] - pts[j + i - 1] < 1e-6:
                break                                   # doublon : étiquettes mesurées fausses ensuite
            if abs(lignes[i][0] - pts[j + i]) > 0.002:
                return None, (f"image {j + i} décodée à {lignes[i][0]:.3f} s au lieu de "
                              f"{pts[j + i]:.3f} s — le compte depuis l'image-clé {j} ne tient pas")
        return r.stdout, None
    return None, f"impossible d'atterrir sur une image-clé avant l'image {k}"


def frames(video, parole, grille, bfd, dossier, inscrire=None):
    """Une extraction PAR HORODATAGE EXIGÉ, et AUX INSTANTS OÙ IL PARLE.
    `bfd` tient le dossier de sortie ; `dossier` est le chemin ABSOLU de son sous-dossier
    `ecrans` (celui que l'INDEX écrit), ouvert ici RELATIVEMENT à `bfd`.

    ⛔ LA DÉRIVE MESURÉE LE 11 SEPTEMBRE 2026. La v1 sortait les images avec
      `-vf fps=1/<intervalle>` et calculait l'horodatage de la ke image comme
      (k-1) x intervalle. Sur une vidéo dont les images ne sont pas régulières — et un
      screen record ne l'est JAMAIS, macOS baisse la cadence quand l'écran ne bouge pas —
      ça décalait de **1,56 s sur toutes les images**. Le défaut ne plante pas : il attache
      **le mauvais écran à la bonne phrase**. `-ss <t>` avant `-i` rend l'horodatage vrai
      par construction (erreur de recherche mesurée : 0,094 s max, même sur un MOV à une
      seule image-clé).

    ⭐⭐ ET LES INSTANTS VISÉS SONT CEUX DES RÉPLIQUES, PLUS UNE GRILLE (revue du 11 sept.).
      Une grille seule ne tient pas sur une longue vidéo : mesuré sur 3 h, une réplique à
      179:59 recevait l'écran de 175:00 — **299 s d'écart**, sans que rien le signale.
      Or ce qu'on veut n'a jamais été « une image régulière » : c'est **l'écran de
      l'instant où il parle**. On vise donc ses répliques d'abord.

    ⭐ Un point de grille à moins de 0,4 s d'une réplique donne le même écran : on ne
      l'extrait pas. ⛔ MAIS C'EST LA GRILLE QUI S'EFFACE, JAMAIS LA RÉPLIQUE (revue Codex,
      12 sept. 2026) : avant, le dédoublonnage gardait le PREMIER instant, et une image de
      grille à 1,4 s faisait sauter la cible de parole à 1,7 s — la réplique recevait
      l'écran d'AVANT, 0,3 s plus tôt, sans avertissement. Sur un écran qui vient de
      changer, « ce bouton-là » désignait alors le mauvais bouton.
      Les extractions partent 4 à la fois — sur 3 h de vidéo, ce sont des centaines de
      `ffmpeg`, pas une douzaine.

    ⭐⭐ CHAQUE IMAGE RENDUE EST VÉRIFIÉE (4e revue Codex, 12 sept. 2026). `-ss` vise un PTS ;
      `showinfo` dit le PTS de l'image que ffmpeg a VRAIMENT rendue. S'ils diffèrent, l'image
      est jetée et on vise la précédente. Avant, on croyait la commande sur parole — et sur
      une vidéo dont l'horloge part à 0,5 s, toutes les images étaient en retard de 0,5 s,
      code 0. Un outil qui ne relit pas ce qu'il a rendu ne mesure rien.
    """
    nom = os.path.basename(dossier)
    # ⭐ LE DOSSIER SE TIENT PAR SON DESCRIPTEUR, PAS PAR SON NOM (3e revue Codex, 12 sept.
    #    2026). Codex a remplacé `ecrans` par un lien vers un dossier de JNT APRÈS le contrôle
    #    et AVANT ffmpeg : la photo de JNT était écrasée. `ecrans` s'ouvre RELATIVEMENT au
    #    dossier de sortie tenu par `bfd`, `O_NOFOLLOW` refuse un lien posé entre-temps, et
    #    chaque image s'écrit DANS CE descripteur (`dir_fd`) : renommer ou remplacer le
    #    dossier pendant l'extraction n'y change plus rien.
    try:
        os.mkdir(nom, dir_fd=bfd)
    except FileExistsError:
        pass
    _sonde("ecrans-cree")
    try:
        dfd = os.open(nom, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=bfd)
    except OSError as e:
        sortir(2, f"`{dossier}` n'est pas un dossier ordinaire à moi ({e.strerror}) — je n'y "
                  "écris pas.")
    _sonde("ecrans-ouvert")
    # ⛔ 6e revue Codex (12 sept. 2026) : entre `mkdir` et cette ouverture, un VRAI dossier de
    #    JNT (pas un lien — `O_NOFOLLOW` ne voit rien) avait été renommé à la place d'`ecrans`,
    #    avec sa photo `ecran-001.jpg` dedans : elle était écrasée, code 0. Après `nettoyer`,
    #    aucun de mes noms n'existe dans `ecrans` ; un nom à moi qui s'y trouve n'est pas à moi.
    deja = sorted(n for n in os.listdir(dfd) if MES_FICHIERS.match("ecrans/" + n))
    if deja:
        os.close(dfd)
        sortir(2, f"`{dossier}` contient déjà {len(deja)} fichier(s) à mon nom que je n'ai pas "
                  f"inscrits ({', '.join(deja[:3])}) — pas à moi, je n'écris pas par-dessus. Donner "
                  "un dossier neuf.")
    pts, depart, cles = instants(video)
    if not pts:
        os.close(dfd)
        sortir(2, f"ffprobe ne lit AUCUN horodatage d'image dans `{video}` — sans eux, `-ss` "
                  "rendrait la PREMIÈRE image après chaque instant, c'est-à-dire l'écran "
                  "d'APRÈS. Je refuse plutôt que de deviner.")
    retenus = sorted(set(parole))
    for g in sorted(set(grille)):
        if all(abs(g - t) >= 0.4 for t in retenus):
            retenus.append(g)
    retenus.sort()
    chemins = {i: os.path.join(dossier, f"ecran-{i:03d}.jpg") for i in range(1, len(retenus) + 1)}
    def une(args):
        i, t = args
        chemin = chemins[i]
        # ⭐ L'IMAGE AFFICHÉE À t = la dernière dont le PTS ≤ t (3e revue Codex). On vise son
        #    PTS exact, moins ½ ms pour que `-ss` (qui rend la première image ≥ la cible)
        #    tombe sur ELLE et pas sur la suivante. Avant, on demandait t tel quel, puis on
        #    reculait de 50 ms et 500 ms si rien ne sortait : juste sur une vidéo à cadence
        #    fixe, faux jusqu'à 1,2 s sur un screen record. Un `t` avant la 1re image ou
        #    après la dernière rend la 1re ou la dernière — jamais rien, jamais l'écran d'après.
        k = max(0, bisect.bisect_right(pts, t + 1e-6) - 1)
        rendus = []
        for k_ in range(k, max(-1, k - 3), -1):
            # ⭐ L'image se COMPTE depuis l'image-clé précédente, et chaque image décodée est
            #    relue (`rendre`, 5e revue Codex). ⛔ Pas `-seek_timestamp 1` : mesuré, il
            #    déplace la recherche sans déplacer le découpage, et rend l'image d'après.
            jpeg, motif = rendre(video, pts, depart, cles, k_)
            if jpeg is None:
                rendus.append(f"image {k_} ({pts[k_]:.3f} s) : {motif}")
                continue
            if k_ != k:
                print(f"⚠️  écran de {t:.2f} s : l'image de {pts[k]:.3f} s n'a pas pu être rendue "
                      f"({rendus[0]}) — c'est la précédente ({pts[k_]:.3f} s) qui la remplace",
                      file=sys.stderr)
            # Écrite PUIS inscrite (nom + empreinte du contenu), fichier neuf ou refus global :
            # un lien, un fichier ou un lien physique posé à MON nom pendant le run n'est pas
            # une erreur d'écriture, c'est une altération (`_Altere` → code 2). ⛔ 7e revue
            # Codex : inscrire AVANT laissait une ligne au registre pour un fichier de JNT.
            #    ⚠️ Ce mutant était AVEUGLE à la suite (12 sept. 2026) : un fichier de JNT à
            #    mon nom posé AVANT `frames` est refusé par le garde des restes, et posé après,
            #    le bassin de 4 fils rend l'instant imprévisible. La sonde « ecran-rendu »
            #    fixe l'instant : le cas D2 y glisse le fichier de JNT, et seul CET ordre
            #    (écrire puis inscrire) peut laisser le registre sans sa ligne.
            _sonde("ecran-rendu", os.path.basename(chemin))
            st = ecrire(dfd, os.path.basename(chemin), jpeg)
            if inscrire:
                inscrire(chemin, jpeg, st)
            return (t, chemin, pts[k_])
        print(f"⚠️  écran de {t:.2f} s : ffmpeg n'a rendu aucune des images visées "
              f"({' · '.join(rendus) or 'rien rendu'}) — cette réplique prendra l'écran le plus "
              "proche", file=sys.stderr)
        return None
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            faits = list(pool.map(une, enumerate(retenus, 1)))
    except _Altere as e:
        sortir(2, str(e))
    finally:
        os.close(dfd)
    return [f for f in faits if f]


def ecrans(video, segments, muets, duree, n_images, bfd, dossier, inscrire=None):
    """Extrait les écrans et rattache CHAQUE réplique au sien.

    Sortie : (imgs, rattache) — imgs = [(t, chemin, rendu)…] dans l'ordre du temps (`rendu` =
    le PTS de l'image réellement rendue, dans l'horloge de la vidéo), rattache[i] = ce triplet
    pour la réplique i. ⭐ 7e revue Codex : `rendu > t` veut dire qu'AUCUNE image n'existait à
    l'instant visé — l'écran est celui d'APRÈS, et l'INDEX le dit. ⭐ C'est CETTE fonction que l'INDEX écrit et que la
    phase 2 de l'autotest exerce avec des répliques PLACÉES (1,7 · 8,4 · 11,5 · 19,98 s) sur un
    banc de couleurs au demi-seconde : une troncature `int(debut)` ou une grille qui
    l'emporte sur la parole y devient un mauvais écran mesuré, pas un souvenir.
    """
    borne = lambda t: min(max(0.0, t), max(0.0, duree))
    parole = [borne(s["debut"]) for i, s in enumerate(segments) if i not in muets]
    grille = max(1.0, duree / max(1, n_images))
    grid = [borne(k * grille) for k in range(int(duree / grille) + 1)]
    imgs = frames(video, parole, grid, bfd, dossier, inscrire)
    rattache = {}
    if imgs:
        for i, s in enumerate(segments):
            if i not in muets:
                t = borne(s["debut"])
                rattache[i] = min(imgs, key=lambda p: abs(p[0] - t))
    return imgs, rattache


def horodatage(ligne):
    m = re.match(r"\[(\d+):(\d+)\]", ligne)
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def _duree(d):
    """Une avance en secondes, lisible : « +20 ms » sous 0,1 s, « +1.8 s » au-delà."""
    if d < 1e-3:                     # ⛔ 11e revue Codex : une avance de 20 µs s'écrivait
        return f"+{d * 1e6:.0f} µs"   #    « +0 ms », qui se lit « aucune avance »
    return f"+{d * 1000:.0f} ms" if d < 0.1 else f"+{d:.1f} s"


def mmss(t):
    """⛔ ARRONDI, PAS TRONQUÉ. `int(16.67)` affiche « 00:16 » pour l'image de 17,0 s :
    une seconde d'erreur inventée par l'AFFICHAGE, alors que l'extraction était juste à
    0,09 s près. Trouvé par la revue Codex du 11 sept. 2026."""
    t = int(round(t))
    return f"{t // 60:02d}:{t % 60:02d}"


def debut_piste(video, k):
    """Début de la piste audio nº k en secondes ABSOLUES (horloge du fichier) : le `pts_time`
    de sa première image décodée (`ashowinfo`), la même que ffmpeg écrit en tête du WAV.
    ⛔ `-copyts` obligatoire (6e revue) — sans lui, ffmpeg rend un pts déjà ramené à `start_time`.
    ⛔ ET LA PISTE, C'EST `0:a:{k}` (7e revue Codex, 12 sept. 2026) : lue sur la piste 0 pour
      toutes, la 2e piste d'un enregistrement (le micro, décalé de 0,7 s sur le banc) prenait
      l'horloge de la 1re — chaque réplique du micro en avance, code 0."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-copyts",
                        "-i", video, "-map", f"0:a:{k}", "-vn", "-af", "ashowinfo",
                        "-frames:a", "1", "-f", "null", "-"], capture_output=True)
    m = re.search(rb"pts_time:\s*(-?[0-9.]+)", r.stderr)
    if not m:
        sortir(2, f"impossible de lire le début de la piste audio {k + 1} (ashowinfo muet) — sans "
                  "lui, l'horloge du transcript n'est pas prouvée. Je refuse plutôt que de "
                  "supposer qu'elle part avec l'image.")
    return float(m.group(1))


def _creer_prive(pfd, nom, prives):
    """Crée `nom` dans le dossier privé (tenu par `pfd`) — FICHIER NEUF (`O_EXCL`), jamais à
    travers un lien, un seul nom — et retient son (dev, inode) dans `prives`. Rend le
    descripteur ouvert en écriture : c'est LUI que ffmpeg reçoit (`/dev/fd/N`), pas le nom.
    ⛔ 7e revue Codex (12 sept. 2026) : ffmpeg écrivait `audio-1.wav` PAR NOM (relatif au
      dossier privé) et le transcripteur ses deux sorties aussi. Un lien physique posé à ces
      noms entre la création du dossier et l'écriture envoyait mes octets chez JNT, code 0."""
    try:
        fd = os.open(nom, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=pfd)
    except OSError as e:
        raise _Altere(f"`{nom}` existe déjà dans mon dossier privé avant que je le crée "
                      f"({e.strerror}) — pas à moi, je n'écris pas par-dessus.")
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        os.close(fd)
        raise _Altere(f"`{nom}` a {st.st_nlink} noms au moment d'écrire dans mon dossier privé — "
                      "je n'écris pas.")
    prives[nom] = (st.st_dev, st.st_ino)
    return fd


def _ouvrir_prive(pfd, nom, prives, attendu=None):
    """Ouvre en lecture `nom` dans le dossier privé, jamais à travers un lien, et exige un
    fichier ordinaire à UN seul nom. `attendu` = le (dev, inode) que je connais : s'il ne colle
    plus, le nom a été remplacé pendant le run → `_Altere`. Sans `attendu` (une sortie du
    transcripteur, que je n'ai pas créée moi-même), l'inode est RETENU dans `prives` : c'est
    celui-là, et lui seul, que l'effacement final retirera. `FileNotFoundError` remonte tel quel.
    ⚠️ Un fichier ordinaire de JNT glissé À MON NOM pendant que le transcripteur tourne est
      indiscernable d'une sortie du transcripteur : le dossier privé est un `mkdtemp` à 0700,
      à moi par construction — c'est la limite, et elle est écrite ici.
    ⛔ 9e revue Codex (12 sept. 2026) : un FIFO posé à mon nom bloquait cet `open` POUR TOUJOURS
      (mesuré : tué à 5 s, muet). `O_NONBLOCK` le fait rendre tout de suite, et `S_ISREG` le
      refuse juste après ; sur un fichier ordinaire, le drapeau ne change rien à la lecture."""
    try:
        fd = os.open(nom, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=pfd)
    except FileNotFoundError:
        raise
    except OSError as e:
        raise _Altere(f"`{nom}` dans mon dossier privé ne s'ouvre pas comme un fichier ordinaire "
                      f"({e.strerror}) — je m'arrête.")
    st = os.fstat(fd)
    ino = (st.st_dev, st.st_ino)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or (attendu is not None and ino != attendu):
        os.close(fd)
        raise _Altere(f"`{nom}` dans mon dossier privé n'est plus le fichier que j'ai créé "
                      f"({st.st_nlink} nom(s), remplacé pendant le run ?) — je m'arrête.")
    if attendu is None:
        prives[nom] = ino
    return fd


def _retirer_prive(prive, pfd):
    """Retire MON dossier privé (chemin `prive`, tenu par `pfd`) — et ferme `pfd`.
    ⛔ 8e revue Codex (12 sept. 2026) : `os.rmdir(prive)` par chemin retirait un dossier VIDE de
      JNT posé à ce chemin pendant le run (le mien, renommé, restait derrière) ; non vide, le
      message accusait « des fichiers que je n'ai pas créés ». Même geste que `_retirer` : mis à
      part par `rename` (atomique), l'inode se lit sur le nom privé et se compare à `pfd` ; pas
      le mien → il revient à son nom (si libre, sinon il reste sous le nom privé, et je le dis)."""
    mien = os.fstat(pfd)
    os.close(pfd)
    parent, nom = os.path.split(prive)
    try:
        tfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
    except OSError:
        print(f"⚠️  dossier de travail {prive} : son parent ne s'ouvre plus, je le laisse.",
              file=sys.stderr)
        return
    try:
        a_part, st = _a_part(tfd, nom)
        if a_part is None:
            print(f"⚠️  mon dossier de travail n'est plus à {prive} — je ne le cherche pas.",
                  file=sys.stderr)
            return
        if (st.st_dev, st.st_ino) != (mien.st_dev, mien.st_ino):
            ou = _remettre(tfd, a_part, nom, st)
            print(f"⚠️  mon dossier de travail n'est plus à {prive} : ce qui s'y trouvait n'est pas "
                  f"à moi, je n'y touche pas" + ("" if ou == nom else f" (il est sous {os.path.join(parent, ou)})")
                  + ".", file=sys.stderr)
            return
        try:
            os.rmdir(a_part, dir_fd=tfd)
        except OSError:
            ou = _remettre(tfd, a_part, nom, st)
            print(f"⚠️  dossier de travail {os.path.join(parent, ou)} laissé en place : il contient "
                  "des fichiers que je n'ai pas créés.", file=sys.stderr)
    finally:
        os.close(tfd)


def _effacer_prive(pfd, nom, ino):
    """Retire `nom` du dossier privé SEULEMENT si le nom porte encore l'inode `ino` que j'ai
    créé ou retenu. ⛔ 7e revue Codex : on effaçait par nom tout ce que ce run avait créé — un
    fichier de JNT glissé à ce nom entre-temps partait avec. Il reste une fenêtre lstat→unlink
    (POSIX n'a pas d'`unlink` par inode) ; le dossier est un `mkdtemp` à 0700, c'est ce qui la
    tient."""
    try:
        st = os.lstat(nom, dir_fd=pfd)
    except FileNotFoundError:
        return
    if (st.st_dev, st.st_ino) != ino:
        return
    try:
        os.unlink(nom, dir_fd=pfd)
    except FileNotFoundError:
        pass


def _segments_valides(charge):
    """Le JSON du transcripteur, vérifié dans sa FORME : une liste d'objets dont `debut` et `fin`
    sont des nombres de secondes finis et positifs (jamais un booléen, jamais une chaîne, jamais
    absents) et `texte` une chaîne. Rend les segments qui portent du texte. Tout écart est un
    `ValueError` — donc « JSON illisible », code 2. ⛔ 10e revue Codex (12 sept. 2026) : un JSON
    VALIDE mais pas de cette forme (`{}`, un segment sans `debut`, `fin` null ou en chaîne) passait
    `json.loads` et plantait plus loin — `KeyError` dans `segments_muets`, trace d'appel, code 1,
    qui n'est pas un refus ; `{}` passait pour une piste sans parole."""
    if not isinstance(charge, list):
        raise ValueError(f"pas une liste de segments ({type(charge).__name__})")
    for i, s in enumerate(charge):
        if not isinstance(s, dict):
            raise ValueError(f"segment {i} : pas un objet ({type(s).__name__})")
        for cle in ("debut", "fin"):
            v = s.get(cle)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0.0 <= v <= PLAFOND_SECONDES):
                raise ValueError(f"segment {i} : `{cle}` vaut {v!r}, pas un nombre de secondes")
        # ⛔ 12e revue Codex (13 sept. 2026) : un `texte` valide en JSON (un surrogat isolé)
        #    passait la vérification puis faisait lever `UnicodeEncodeError` à l'écriture de
        #    l'INDEX — trace d'appel, code 1, aucune sortie. Et `texte` ABSENT passait pour une
        #    réplique vide (code 5) au lieu d'un refus de forme.
        #    ⚠️ On n'exige PAS `fin` ≥ `debut` : `segments_muets` borne la fenêtre lui-même, et
        #    refuser là-dessus jetterait une vraie transcription pour un arrondi du modèle.
        if not isinstance(s.get("texte"), str):
            raise ValueError(f"segment {i} : `texte` n'est pas une chaîne")
        try:
            s["texte"].encode()
        except UnicodeEncodeError:
            raise ValueError(f"segment {i} : `texte` n'est pas encodable (surrogat isolé ?)")
    return [s for s in charge if s.get("texte")]


def transcrire_piste(video, k, pfd, langue, prives):
    """Extrait la piste audio nº k en WAV 16 kHz mono, la transcrit, rend
    (segments, nom du WAV, début de la piste audio en secondes absolues,
    [(nom, octets)] des transcripts bruts à déposer dans la sortie).
    Les segments viennent du JSON détaillé de `transcrire()` : horodatages en FLOTTANT
    (le .txt les tronque à la seconde), texte, et les probabilités du modèle.
    ⭐ Le WAV et les transcripts NAISSENT DANS LE DOSSIER PRIVÉ tenu par `pfd` — et depuis la
    5e revue Codex (12 sept. 2026), ffmpeg et le transcripteur y écrivent par NOM RELATIF,
    leur répertoire courant étant ce descripteur (`fchdir` dans l'enfant) : le chemin du
    dossier privé peut être remplacé par un lien pendant le run, les octets tombent quand
    même dans le vrai dossier. Rien ne se relit par chemin non plus (`dir_fd`, `O_NOFOLLOW`).
    Seuls les transcripts entrent ensuite dans le dossier de sortie, par descripteur
    (`ouvrir`), après inscription au registre. Le WAV n'y entre jamais (4e revue).
    ⛔ ET LE TRANSCRIPTEUR QUI PLANTE APRÈS AVOIR ÉCRIT SON JSON NE COMPTE PAS (5e revue) :
    avant, `rc ≠ 0 or not exists(detail)` acceptait un JSON écrit puis un exit 1.
    ⭐ L'HORLOGE DU WAV EST CELLE DE LA PISTE AUDIO, PAS CELLE DU FICHIER (5e revue Codex).
    Mesuré : l'échantillon 0 du WAV est la première image AUDIO décodée — sur la vidéo réelle,
    le son part 61 ms après l'image ; sur le banc de Codex, 0,7 s après. Whisper compte donc
    depuis le début du SON ; les écrans, depuis `start_time`. Le début de la piste se lit sur
    sa première image décodée (`ashowinfo`) — la même que ffmpeg écrit en tête du WAV.
    ⛔ ET IL SE LIT EN HORLOGE ABSOLUE (`-copyts`, 6e revue Codex, 12 sept. 2026). Sans lui,
    ffmpeg rend un `pts_time` DÉJÀ ramené à `start_time` : sur une vidéo dont l'horloge part à
    0,5 s, il disait 0 au lieu de 0,5, et `_construire` retranchait `start_time` UNE DEUXIÈME
    fois — chaque écran en avance de 0,5 s, code 0 (mesuré : image nº 10 rendue pour la nº 15 ;
    sur un MPEG-TS à horloge négative, nº 20 pour la nº 14). Sur la vidéo réelle, `start_time`
    vaut 0 : le défaut y était invisible. Le WAV, lui, est extrait SANS `-copyts` — son
    échantillon 0 est bien la première image audio, c'est le repère qu'on lit ici.
    ⭐ Les transcripts bruts sont RENDUS à `_construire`, pas copiés dans la sortie : avec deux
    pistes, ceux de la 1re restaient dans le dossier quand la 2e plantait (6e revue Codex) —
    « code 2, rien copié » était faux. Ils n'entrent qu'une fois TOUTES les pistes transcrites.
    `prives` reçoit {nom: (dev, inode)} de ce que ce run a créé ou retenu dans le dossier
    privé : ce sont les seuls qu'on y effacera, et seulement s'ils portent encore cet inode.
    ⛔ 7e revue Codex (12 sept. 2026) — TROIS « par nom » dans le dossier privé : le WAV est
      maintenant CRÉÉ PAR MOI (`_creer_prive`, `O_EXCL`) et ffmpeg l'écrit à travers mon
      descripteur (`-f wav /dev/fd/N`) ; les deux sorties du transcripteur doivent être ABSENTES
      avant qu'il parte (il écrit par nom, `open(..., "w")`, et suivrait un lien physique) ; et
      tout se relit par inode (`_ouvrir_prive`). L'horloge de la piste se lit dans `debut_piste`
      — sur SA piste, plus sur la 0."""
    wav, txt = f"audio-{k + 1}.wav", f"transcript-piste-{k + 1}.txt"
    detail = f"transcript-piste-{k + 1}.json"
    a_debut = debut_piste(video, k)
    dans_prive = dict(preexec_fn=lambda: os.fchdir(pfd), pass_fds=(pfd,))
    wfd = _creer_prive(pfd, wav, prives)
    try:
        _sonde("wav-cree", wav)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-map", f"0:a:{k}", "-vn",
                        # ⛔ `-fd N fd:`, JAMAIS `/dev/fd/N` (14 sept. 2026) : le bac à sable
                        #   de Codex refuse d'OUVRIR `/dev/fd/6` (« Operation not permitted »),
                        #   donc l'outil était mort pour Codex. Le protocole `fd:` écrit dans le
                        #   descripteur HÉRITÉ sans rien ouvrir, et il reste seekable : l'en-tête
                        #   WAV porte la vraie taille. Même garantie : jamais un nom.
                        "-ac", "1", "-ar", "16000", "-f", "wav", "-fd", str(wfd), "fd:"], check=True,
                       preexec_fn=lambda: os.fchdir(pfd), pass_fds=(pfd, wfd))
    finally:
        os.close(wfd)
    os.close(_ouvrir_prive(pfd, wav, prives, prives[wav]))
    for nom in (txt, detail):
        try:
            os.lstat(nom, dir_fd=pfd)
        except FileNotFoundError:
            continue
        raise _Altere(f"`{nom}` existe déjà dans mon dossier privé avant que le transcripteur "
                      "parte — pas à moi, je ne le laisse pas écrire par-dessus.")
    r = subprocess.run([sys.executable, TRANSCRIRE, wav, txt, "--langue", langue,
                        "--detail-json", detail], capture_output=True, **dans_prive)
    # ⛔ 12e revue Codex (13 sept. 2026) : `text=True` décodait stdout/stderr en UTF-8 STRICT —
    #    un seul octet 0xff écrit par le transcripteur faisait lever `UnicodeDecodeError` AVANT
    #    même qu'on regarde son code de retour : trace d'appel, code 1, aucun INDEX. On lit des
    #    octets et on les rend lisibles (`replace`), sur UNE ligne (son stderr peut en faire dix).
    dit = " ".join(((r.stderr or r.stdout) or b"").decode(errors="replace").split())[:400]
    for nom in (txt, detail):
        try:
            os.close(_ouvrir_prive(pfd, nom, prives))
        except FileNotFoundError:
            pass

    def lire(nom):
        fd = _ouvrir_prive(pfd, nom, prives, prives.get(nom))
        with os.fdopen(fd, "rb") as f:
            return f.read()
    brut = None
    if r.returncode == 0:
        try:
            brut = lire(detail)
        except FileNotFoundError:
            brut = None
    if brut is None:
        sortir(2, f"la transcription de la piste {k + 1} a échoué (code {r.returncode}) : {dit}")
    # ⛔ 12e revue Codex (13 sept. 2026) : le JSON était relu UNE FOIS DE PLUS pour être déposé.
    #    Tronqué entre les deux lectures, l'INDEX se bâtissait sur 40 octets et la preuve brute
    #    déposée en faisait 0 — code 0, stderr vide. On dépose EXACTEMENT les octets validés.
    try:
        bruts = [(txt, lire(txt)), (detail, brut)]
    except FileNotFoundError:           # 10e revue : code 0 et le JSON là, mais pas le .txt → trace
        sortir(2, f"la transcription de la piste {k + 1} a rendu code {r.returncode} sans écrire "
                  f"`{txt}` — rien à en tirer.")
    # ⛔ 8e revue Codex (12 sept. 2026) : un transcripteur qui rend code 0 et un JSON de 0 octet
    #    faisait planter `json.loads` — trace d'appel, code 1, qui n'est pas un refus. Un JSON
    #    illisible se dit en une ligne, code 2. 10e revue : sa FORME aussi (`_segments_valides`).
    try:
        segments = _segments_valides(json.loads(brut))
    except (ValueError, TypeError, AttributeError, RecursionError, OverflowError) as e:
        sortir(2, f"la transcription de la piste {k + 1} a rendu un JSON illisible ({len(brut)} "
                  f"octets, code {r.returncode}) : {e} — {brut[:80]!r}. Rien à en tirer.")
    for s in segments:
        s["piste"] = k
    # ⛔ QUEL MOTEUR A PARLÉ ? (20 sept. 2026, quand l'outil est devenu multiplateforme.)
    #    Deux moteurs existent — `mlx-whisper` sur la puce graphique d'un Mac Apple
    #    Silicon, `faster-whisper` sur le processeur partout ailleurs. Ils n'ont ni la
    #    même vitesse ni exactement la même sortie, et un transcript ne porte AUCUNE
    #    trace de ce qui l'a produit. ⭐ Un repli silencieux serait le défaut qu'on
    #    combat sous un autre nom : ça sort, c'est bon, et rien ne dit d'où ça vient.
    #    ⚠️ Si la ligne manque, on l'écrit quand même — « inconnu » est une information,
    #    « rien » n'en est pas une.
    m = re.search(r"MOTEUR-VOIX\[([^\]]{1,120})\]", dit)
    moteur = m.group(1).strip() if m else "inconnu (le transcripteur ne l'a pas dit)"
    print(f"   · piste {k + 1} transcrite par {moteur}")
    return segments, wav, a_debut, bruts, moteur


def a_moi(bfd):
    """Un dossier (tenu par `bfd`) est à moi s'il porte le marqueur-registre AVEC SA SIGNATURE
    en première ligne (`ENTETE`). ⛔ Rien d'autre ne vaut preuve : l'INDEX.md « # REGARD — » a
    été retiré (2e revue Codex, 12 sept. 2026) — un fichier que JNT peut écrire n'est pas une
    signature ; et depuis la 5e revue, un `.regarder` SANS la phrase exacte non plus. Les
    dossiers d'avant le marqueur sont morts.
    ⚠️ Un marqueur qui est un LIEN n'est pas le mien non plus (`O_NOFOLLOW`, jamais suivi).
    ⛔ 8e revue Codex (12 sept. 2026) : un FIFO à ce nom bloquait l'`open` POUR TOUJOURS (>180 s,
      aucun message). `O_NONBLOCK` ouvre sans attendre ; `S_ISREG` tranche ensuite → refus.
    ⛔ Et un DOSSIER à ce nom passe l'`open` : c'est `fdopen` qui plantait (IsADirectoryError,
      trace d'appel, code 1 — 8e revue). Le `fstat` se fait sur le descripteur NU, avant."""
    try:
        fd = os.open(MARQUEUR, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=bfd)
    except OSError:
        return False
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        return False
    with os.fdopen(fd, "rb") as f:
        return f.readline().rstrip(b"\r\n") == ENTETE.encode()


_VERROU_REGISTRE = threading.Lock()
EMPREINTE = re.compile(r"^[0-9a-f]{64}$")
IDENTITE = re.compile(r"^[0-9]+:[0-9]+$")          # `dev:inode`, tel que `noter` l'écrit


class Registre:
    """Le registre `.regarder` du run : CRÉÉ une fois (fichier neuf, `O_EXCL`, jamais à travers un
    lien), signé (`ENTETE`), puis ÉCRIT PAR CE DESCRIPTEUR jusqu'à la fin — jamais rouvert par nom.
    ⛔ 7e revue Codex (12 sept. 2026) : `noter` rouvrait `.regarder` par nom à chaque ligne. Entre
      deux lignes, Codex renommait mon registre et posait à son nom un LIEN PHYSIQUE vers une
      note de JNT (`O_NOFOLLOW` ne voit pas un lien physique) : mes lignes s'ajoutaient à sa
      note, code 0. Maintenant le descripteur ouvert à la création est le seul chemin d'écriture ;
      un registre remplacé pendant le run reçoit zéro octet, et `construire` le dit à la fin
      (le dossier ne sera plus reconnu comme le mien — refus au prochain run, rien d'autre).
    Chaque ligne : `<sha256 hex> <dev>:<inode> <un de MES noms>` — un nom inscrit sous ma
    signature ne prouve pas que le CONTENU est encore le mien (6e revue : l'empreinte), et
    l'empreinte ne prouve pas que le FICHIER est le mien (8e revue : l'inode). `nettoyer`
    n'efface que sur les deux. Un fichier tronqué ne se distingue pas d'un fichier modifié,
    et c'est voulu.
    ⛔ 8e revue Codex (12 sept. 2026) : Codex a fait `cp -R` d'une sortie — un dossier de JNT
      dont chaque fichier porte MES octets et MON registre — et relancé dessus : 10 fichiers
      effacés et réécrits, code 0. L'empreinte prouvait le contenu, pas la propriété. Avec
      l'inode inscrit, une copie est refusée (« COPIE ») ; un `mv` sur le même disque garde
      les inodes et reste relançable ; déplacé sur un autre disque → refus, rien touché."""

    def __init__(self, bfd):
        self.bfd = bfd
        try:
            self.fd = os.open(MARQUEUR, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_APPEND
                              | os.O_NOFOLLOW, 0o644, dir_fd=bfd)
        except OSError as e:
            raise _Altere(f"`{MARQUEUR}` existe déjà ou n'est pas un fichier ordinaire à moi "
                          f"({e.strerror}) — je n'écris pas par-dessus. Donner un dossier neuf.")
        st = os.fstat(self.fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            os.close(self.fd)
            raise _Altere(f"`{MARQUEUR}` a {st.st_nlink} noms au moment d'écrire — je n'écris pas.")
        self.ino = (st.st_dev, st.st_ino)
        os.write(self.fd, (ENTETE + "\n").encode())

    def noter(self, rel, donnees, st):
        """Inscrit `rel` (relatif au dossier de sortie, tel que `MES_FICHIERS` l'attend),
        l'empreinte SHA-256 des octets ÉCRITS et l'identité `dev:inode` du fichier créé (`st`,
        le `stat` rendu par `ecrire`) — après l'écriture, jamais avant (7e revue)."""
        assert MES_FICHIERS.match(rel), rel
        ligne = f"{hashlib.sha256(donnees).hexdigest()} {st.st_dev}:{st.st_ino} {rel}\n".encode()
        with _VERROU_REGISTRE:
            os.write(self.fd, ligne)

    def toujours_la(self):
        """Le nom `.regarder` du dossier porte-t-il encore MON registre (même dev, même inode) ?"""
        try:
            st = os.lstat(MARQUEUR, dir_fd=self.bfd)
        except OSError:
            return False
        return (st.st_dev, st.st_ino) == self.ino

    def fermer(self):
        os.close(self.fd)


def deposer(reg, rel, donnees):
    """ÉCRIT PUIS INSCRIT `rel` (nom simple, dans le dossier de sortie) — fichier neuf ou refus.
    ⛔ 7e revue Codex (12 sept. 2026) : inscrire AVANT d'écrire laissait, sur un refus d'`ecrire`
      (un `transcript.txt` de JNT glissé là), une ligne au registre pour un fichier qui n'est pas
      à moi. Un plantage ENTRE l'écriture et l'inscription laisse un fichier à mon nom non inscrit
      → `restes` → refus (code 2) au prochain run : toujours un refus, jamais un effacement."""
    st = ecrire(reg.bfd, rel, donnees)
    reg.noter(rel, donnees, st)


def nettoyer(base, bfd):
    """Efface CE QUE LE REGISTRE DIT QUE J'AI ÉCRIT dans mon dossier (tenu par `bfd`), et rien
    d'autre. `base` ne sert qu'aux messages : depuis la 5e revue Codex (12 sept. 2026), c'est
    `construire` qui tient le dossier, UNE fois, et tout le run — contrôle, nettoyage,
    écriture — passe par ce même descripteur. Avant, `nettoyer` rouvrait le dossier par son
    chemin, entre deux contrôles faits par chemin : une fenêtre de plus.

    ⛔ Avant : `shutil.rmtree(base)`. Revue Codex du 12 sept. 2026 : une vidéo que JNT
      avait POSÉE dans un dossier déjà produit par l'outil, relancée avec ce dossier en
      `--sortie`, était effacée AVANT d'être transcrite — code 1, fichier source perdu.
      Un dossier « à moi » n'est pas un dossier où tout est à moi.
    ⛔ Puis (2e revue, même jour) : effacer PAR NOM détruisait encore un `transcript.txt`
      de JNT et suivait un lien `ecrans` jusque dans un dossier à lui. Donc : le registre
      seul décide, un lien symbolique n'est jamais suivi, et un fichier à MON nom qui
      n'est PAS au registre fait REFUSER (code 2) plutôt qu'écraser.
    ⛔ Puis (3e revue, même jour) : une ligne `../temoin` ou `/Users/<toi>/…` glissée dans le
      registre faisait effacer HORS du dossier, code 0. Le registre ne contient que des noms
      que J'ÉCRIS (`MES_FICHIERS`) : toute autre ligne prouve qu'il est altéré → code 2,
      rien touché. Et TOUS les refus se décident AVANT la première suppression : avant,
      l'INDEX inscrit partait, puis le refus tombait — « code 2 » ne voulait pas dire
      « rien n'a bougé ». [[reference_un_code_dechec_ne_garantit_pas_labsence_decriture]]
    ⛔ Puis (4e revue, même jour) : les contrôles étaient justes, mais l'effacement se faisait
      PAR CHEMIN — entre le contrôle et `os.remove`, Codex renommait `ecrans` et posait un lien
      vers un dossier de JNT : sa photo partait. Tout passe maintenant par DESCRIPTEUR
      (`unlinkat`) : le dossier tenu reste le dossier tenu, quel que soit son nom d'après.
      Et un lien posé à un nom INSCRIT n'est plus « sauté » : c'est un registre altéré,
      code 2 avant la première suppression.
    ⛔ Puis (6e revue, même jour) : trois défauts. (a) Un nom inscrit sous ma signature n'est
      pas un CONTENU encore à moi : Codex a copié un run (`cp -R`), modifié l'INDEX.md comme
      JNT annote le sien, relancé — l'INDEX modifié partait. Chaque ligne du registre porte
      maintenant l'EMPREINTE SHA-256 des octets écrits, et un fichier inscrit ne s'efface que
      s'il les porte encore, octet pour octet. (b) `os.rmdir("ecrans")` effaçait un dossier
      vide de JNT glissé à ce nom après les contrôles : on ne retire plus `ecrans`, on le
      réutilise au run suivant. (c) Un nom en double au registre est un registre altéré.
    ⛔ Puis (7e revue, même jour) : le contrôle (étape 3) ouvrait et relisait chaque inscrit,
      puis l'effacement (étape 4) faisait `unlink` PAR NOM — entre les deux, Codex renommait
      mon INDEX.md et posait le sien à ce nom : effacé, code 0. Ou l'annotait sur place :
      effacé aussi. Maintenant chaque inscrit vérifié reste OUVERT ; juste avant `unlink`,
      l'inode du nom est comparé à celui du fichier vérifié (remplacé → refus, celui de JNT
      reste) ; et juste après, le fichier effacé est RELU par son descripteur (modifié entre
      les deux → restauré tel quel sous son nom, et refus).
    ⛔ Puis (8e revue, même jour) : la fenêtre lstat→unlinkat « de POSIX », écrite comme
      inévitable, ne l'était pas. Codex l'a frappée (1 perte sur 29 essais au `RENAME_SWAP`,
      15 sur 3 000 au banc Claude) : un fichier de JNT renommé sur mon nom dans ces 0,4 à 8 µs
      partait, code 0 — et la relecture d'après lisait MON descripteur, donc ne voyait rien.
      Un `unlink` par nom ne se protège pas par un `lstat`. Alors AUCUN nom public n'est plus
      détruit : `_retirer` RENOMME d'abord le nom vers un nom privé imprévisible (atomique :
      il emporte ce que le nom portait, quoi que ce soit), lit l'inode SUR CE NOM-LÀ, et
      n'efface que si c'est mon fichier vérifié, encore intact ; sinon le fichier est RELIÉ à
      son nom public (`link` exclusif) et c'est un refus. Même chose pour `.regarder` (avant :
      `unlink` par nom, sans contrôle — un registre de JNT posé au dernier instant partait) ;
      le registre reste OUVERT de sa lecture à son retrait. Et quand la dernière relecture
      trouve mon fichier modifié par un descripteur tiers, les octets tenus vont dans un
      `mkstemp` si aucun nom n'est libre (avant : « IMPOSSIBLE à restaurer », 37 octets
      d'annotation de JNT mouraient en mémoire). ⚠️ Un `cp -R` d'une sortie est refusé dès
      l'étape 3 : les inodes inscrits ne sont pas ceux des fichiers (« COPIE »).
    """
    registre = os.path.join(base, MARQUEUR)
    efd = rfd = None
    try:
        try:
            st = os.lstat(MARQUEUR, dir_fd=bfd)
        except OSError:
            sortir(2, f"le registre {registre} a disparu pendant le run — je n'efface rien.")
        if not stat.S_ISREG(st.st_mode):
            sortir(2, f"le registre {registre} n'est pas un fichier ordinaire (un lien ?) — il "
                      "est ALTÉRÉ, je n'efface rien. Donner un dossier neuf.")
        # Ouvert SANS attendre (un FIFO à ce nom bloquait pour toujours — 8e revue), vérifié par
        # descripteur, et GARDÉ OUVERT jusqu'à son retrait : c'est ce fichier-là qui partira.
        rfd = os.open(MARQUEUR, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=bfd)
        if not stat.S_ISREG(os.fstat(rfd).st_mode):
            sortir(2, f"le registre {registre} n'est pas un fichier ordinaire — il est ALTÉRÉ, "
                      "je n'efface rien. Donner un dossier neuf.")
        octets_registre = _lire_fd(rfd)
        lignes = octets_registre.decode("utf-8", "replace").splitlines()
        if not lignes or lignes[0] != ENTETE:
            sortir(2, f"le registre {registre} ne porte pas ma signature en première ligne — ce "
                      "n'est pas le mien, je n'efface rien. Donner un dossier neuf.")
        # 1. Un registre que je n'aurais jamais pu écrire n'est pas le mien : chaque ligne
        #    est `<sha256 hex> <dev>:<inode> <un de MES noms>`, et un nom n'y figure qu'une fois.
        inscrits, etrangers, doubles = {}, [], []      # inscrits[rel] = (empreinte, "dev:ino")
        for l in lignes[1:]:
            if not l.strip():
                continue
            h, _, reste = l.partition(" ")
            ident, _, rel = reste.partition(" ")
            if not EMPREINTE.match(h) or not IDENTITE.match(ident) or not MES_FICHIERS.match(rel):
                etrangers.append(l)
            elif rel in inscrits:
                doubles.append(rel)
            else:
                inscrits[rel] = (h, ident)
        if etrangers:
            sortir(2, f"le registre {registre} porte {len(etrangers)} ligne(s) que je n'écris "
                      f"jamais ({', '.join(repr(e[:90]) for e in etrangers[:3])}) — il est ALTÉRÉ, "
                      "je n'efface rien. Donner un dossier neuf.")
        if doubles:
            sortir(2, f"le registre {registre} inscrit deux fois {', '.join(doubles[:3])} — je "
                      "n'écris jamais ça, il est ALTÉRÉ, je n'efface rien. Donner un dossier neuf.")
        try:
            st = os.lstat("ecrans", dir_fd=bfd)
        except FileNotFoundError:
            st = None
        if st is not None:
            if not stat.S_ISDIR(st.st_mode):
                sortir(2, f"`{os.path.join(base, 'ecrans')}` n'est pas un dossier ordinaire (un LIEN "
                          "vers un autre dossier ?) — je n'y écris pas et je n'y efface rien. "
                          "Donner un dossier neuf.")
            efd = os.open("ecrans", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=bfd)

        def tenu(rel):
            """(descripteur, nom) où vit le fichier inscrit `rel` — jamais par chemin."""
            if rel.startswith("ecrans/"):
                return efd, rel[len("ecrans/"):]
            return bfd, rel
        # 2. Ce qui porte un de MES noms sans être au registre n'est pas à moi : refuser, pas
        #    écraser — et le décider AVANT d'avoir effacé quoi que ce soit.
        presents = list(os.listdir(bfd)) + (["ecrans/" + n for n in os.listdir(efd)] if efd else [])
        restes = [rel for rel in presents if MES_FICHIERS.match(rel) and rel not in inscrits]
        if restes:
            sortir(2, f"dans {base}, {len(restes)} fichier(s) portent un nom que j'utilise mais ne "
                      f"sont PAS au registre {MARQUEUR} — donc pas à moi : {', '.join(restes[:4])}\n"
                      "   Je n'écrase pas. Donner un dossier neuf, ou retirer ces fichiers.")
        # 3. Un nom inscrit qui n'est plus un fichier ordinaire (un lien posé là), ou dont les
        #    octets ne sont plus ceux que j'ai inscrits (JNT l'a annoté, ou mon écriture a été
        #    coupée) : altération. Lu par descripteur, jamais à travers un lien — et le
        #    descripteur RESTE OUVERT jusqu'à l'effacement (7e revue Codex).
        tenus = []                              # (rel, dfd, nom, fd) — vérifiés, gardés ouverts
        try:
            for rel, (h, ident) in inscrits.items():
                dfd, nom = tenu(rel)
                if dfd is None:
                    continue
                try:                    # O_NONBLOCK : un FIFO à ce nom rend, puis S_ISREG le refuse (9e revue)
                    fd = os.open(nom, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dfd)
                except FileNotFoundError:
                    continue
                except OSError:
                    sortir(2, f"`{os.path.join(base, rel)}` est inscrit à mon registre mais ne "
                              "s'ouvre pas comme un fichier ordinaire (un LIEN ?) — le dossier est "
                              "ALTÉRÉ, je n'efface rien. Donner un dossier neuf.")
                tenus.append((rel, dfd, nom, fd))
                st_i = os.fstat(fd)
                if not stat.S_ISREG(st_i.st_mode):
                    sortir(2, f"`{os.path.join(base, rel)}` est inscrit à mon registre mais n'est "
                              "pas un fichier ordinaire — le dossier est ALTÉRÉ, je n'efface rien. "
                              "Donner un dossier neuf.")
                if f"{st_i.st_dev}:{st_i.st_ino}" != ident:
                    sortir(2, f"`{os.path.join(base, rel)}` porte mon nom et mon registre, mais ce "
                              "n'est PAS le fichier que j'ai écrit (autre inode) — ce dossier est une "
                              "COPIE d'une de mes sorties, pas ma sortie : je n'y efface rien. "
                              "Donner un dossier neuf.")
                if _sha_fd(fd) != h:
                    sortir(2, f"`{os.path.join(base, rel)}` a été MODIFIÉ depuis que je l'ai écrit "
                              "(son empreinte n'est plus celle du registre) — il n'est plus à moi, "
                              "je n'efface rien. Donner un dossier neuf.")
            _sonde("avant-suppression")
            # 4. Seulement maintenant : retirer ce que le registre dit — jamais un `unlink` sur un
            #    nom public (8e revue Codex) : `_retirer` renomme d'abord, juge l'inode sur le nom
            #    privé, et rend à JNT ce qui n'est pas à moi.
            for rel, dfd, nom, fd in tenus:
                _retirer(base, rel, dfd, nom, fd, inscrits[rel][0])
        finally:
            for _, _, _, fd in tenus:
                os.close(fd)
        # `ecrans` reste en place (vide) : `frames` le réutilise. Le retirer effaçait un dossier
        # vide de JNT glissé à ce nom après les contrôles (6e revue Codex).
        # Le registre part en dernier, par la même procédure : celui que j'ai LU, et lui seul.
        _retirer(base, MARQUEUR, bfd, MARQUEUR, rfd, hashlib.sha256(octets_registre).hexdigest())
    finally:
        if rfd is not None:
            os.close(rfd)
        if efd is not None:
            os.close(efd)


def _a_part(dfd, nom):
    """RENOMME `nom` (dans le dossier tenu par `dfd`) vers un nom privé IMPRÉVISIBLE du même
    dossier — atomique : ce que le nom portait à cet instant, quoi que ce soit, part avec lui,
    et plus personne ne le vise par son nom public. Rend (nom privé, lstat) ; (None, None) si
    `nom` n'existait pas. ⛔ 8e revue Codex (12 sept. 2026) : c'est CE geste qui ferme la fenêtre
    lstat→unlink — on ne détruit jamais un nom que quelqu'un d'autre peut viser."""
    prive = f"{nom}.regarder-efface-{os.getpid()}-{secrets.token_hex(8)}"
    try:
        os.rename(nom, prive, src_dir_fd=dfd, dst_dir_fd=dfd)
    except FileNotFoundError:
        return None, None
    return prive, os.lstat(prive, dir_fd=dfd)


def _remettre(dfd, prive, nom, st):
    """Redonne un nom PUBLIC à ce qui est sous `prive` (mis à part par `_a_part`, pas à moi) :
    `nom` s'il est libre, sinon un nom de récupération — par `link`, qui est EXCLUSIF (jamais
    par-dessus quoi que ce soit), puis le nom privé est retiré. Un dossier (pas de `link`)
    revient par `rename` si son nom est libre. Rend le nom où la chose vit maintenant — le nom
    privé si rien n'a pu être fait : elle n'est jamais perdue, elle a changé de nom au pire."""
    candidats = (nom, nom + ".recupere-par-regarder", nom + f".recupere-{os.getpid()}")
    if stat.S_ISDIR(st.st_mode):
        for candidat in candidats:
            try:
                os.lstat(candidat, dir_fd=dfd)
                continue
            except FileNotFoundError:
                pass
            try:
                os.rename(prive, candidat, src_dir_fd=dfd, dst_dir_fd=dfd)
                return candidat
            except OSError:
                continue
        return prive
    for candidat in candidats:
        try:
            os.link(prive, candidat, src_dir_fd=dfd, dst_dir_fd=dfd, follow_symlinks=False)
        except OSError:
            continue
        try:
            os.unlink(prive, dir_fd=dfd)
        except OSError:
            pass
        return candidat
    return prive


def _sauver(base, dfd, nom, octets):
    """Écrit `octets` sous un nom NEUF du dossier (`nom`, puis deux noms de récupération) ; si
    aucun n'est libre, dans un fichier `mkstemp` — dans le dossier, sinon dans le dossier
    temporaire. Rend le chemin lisible. ⛔ 8e revue Codex : avec trois noms pris, l'annotation de
    JNT restait en mémoire et mourait avec le processus, code 2 (« IMPOSSIBLE à restaurer »)."""
    for candidat in (nom, nom + ".recupere-par-regarder", nom + f".recupere-{os.getpid()}"):
        try:
            ecrire(dfd, candidat, octets)
        except _Altere:
            continue
        return candidat
    for dossier in (base, None, os.path.expanduser("~")):
        try:
            fd, chemin = tempfile.mkstemp(prefix=f"{nom}.regarder-recupere-", dir=dossier)
        except OSError:
            continue
        with os.fdopen(fd, "wb") as f:
            f.write(octets)
        return chemin
    sortir(2, f"impossible d'écrire les {len(octets)} octets de `{nom}` où que ce soit (ni "
              f"dans {base}, ni dans le dossier temporaire, ni dans le dossier personnel) — "
              "ils sont PERDUS, et je le dis plutôt que de le cacher. Rendre un de ces trois "
              "dossiers inscriptible, puis relancer.")


def _retirer(base, rel, dfd, nom, fd, h):
    """Retire le nom `nom` (dans le dossier tenu par `dfd`, `rel` pour les messages) SEULEMENT s'il
    porte encore le fichier vérifié `fd`, dont les octets ont encore l'empreinte `h`. Ne fait rien
    si le nom a disparu. Tout autre cas est un refus (code 2) — sans qu'un fichier de JNT ait
    jamais été `unlink`é.
    ⛔ 8e revue Codex (12 sept. 2026) : `lstat(nom)` puis `unlink(nom)` laissait 0,4 à 8 µs où un
      fichier de JNT renommé sur `nom` partait (mesuré : 1 perte/29 essais, 15/3 000), code 0, et
      la relecture d'après lisait MON descripteur — donc ne voyait rien. POSIX n'a pas d'`unlink`
      par inode : un `unlink` par nom ne se protège pas. Alors le nom est d'abord mis À PART
      (`_a_part`, rename atomique vers un nom que personne ne vise), et c'est SUR CE NOM que
      l'inode se lit :
        · mon fichier vérifié, octets intacts → `unlink` du nom privé ;
        · celui de JNT (autre inode), ou le mien modifié sur place → RELIÉ à son nom public
          (`_remettre`, exclusif), refus. S'il n'a pas pu l'être, il vit sous son nom privé et le
          message le nomme. Rien ne se perd.
      Après l'`unlink` du mien, une dernière relecture par descripteur (modifié entre-temps par
      un descripteur déjà ouvert — par le nom, c'était devenu impossible) → `_sauver`.
    ⛔ 9e revue Codex (12 sept. 2026) : le nom privé n'est secret que pour qui ne fait pas `ls`.
      Un fichier de JNT renommé PAR-DESSUS (rename écrase) laissait mon inode intact sous `fd`
      — donc l'inode collait — mais SANS nom (`st_nlink` 0), et l'`unlink` du nom privé effaçait
      le sien (mesuré : 24 → 0 octets, code 0). Le compte de noms de `fd` se compare donc à celui
      lu sur le nom privé : s'il a baissé, ce qui vit sous ce nom n'est pas à moi → remis à son
      nom, refus.
    ⛔ 10e revue Codex (12 sept. 2026) : ce compte de noms se CONTOURNAIT sans course — un lien
      physique vers mon fichier (`link`, le compte remonte), PUIS le rename de la note de JNT
      par-dessus mon nom privé : compte égal, inode de `fd` intact, et l'`unlink` effaçait SA
      note (mesuré : 24 → 0 octets, code 0). Le compte de noms ne dit rien de ce qui vit sous
      un NOM. Alors c'est l'IDENTITÉ (`dev:ino`) de ce qui est sous le nom privé qui se relit,
      par `lstat`, JUSTE AVANT l'`unlink` — pas au moment du rename : si ce n'est plus mon inode
      vérifié, c'est relié à son nom public, refus. ⚠️ La fenêtre entre ce `lstat` et l'`unlink`
      reste (quelques µs) : POSIX n'a pas d'`unlink` par inode, et c'est écrit ici plutôt que
      caché."""
    chemin = os.path.join(base, rel)
    dossier = os.path.dirname(rel)
    _sonde("avant-retrait", nom)
    prive, _ = _a_part(dfd, nom)
    if prive is None:
        return
    _sonde("mis-a-part", nom)               # le nom public est LIBRE ici : cas M2 y pose un fichier de JNT
    st = os.fstat(fd)

    def sous_le_nom_prive():
        """Ce qui est SOUS le nom privé À CET INSTANT (`lstat`) — None s'il n'y a plus rien."""
        try:
            return os.lstat(prive, dir_fd=dfd)
        except FileNotFoundError:
            return None

    def remplace(st_la):
        """Sous le nom privé vit autre chose que mon fichier vérifié : relié à son nom public,
        refus — ET mes octets sont sauvés s'ils ne sont plus ceux du registre.
        ⛔ 12e revue Codex (13 sept. 2026) : quand l'annotation de JNT arrive APRÈS la première
          empreinte (sonde « empreinte-relue »), mon inode n'a plus de nom — le rename l'a
          emporté — et ses octets ne vivent plus que dans `fd`. On rendait sa note (24/24) en
          laissant mourir son annotation (24 → 0 octet), sous un message qui ne la nommait même
          pas. La règle ne connaît pas deux cas : ce qui n'est PAS ce que j'ai écrit ne s'efface
          jamais, sous un nom comme dans un descripteur.
        ⚠️ L'empreinte se relit ICI, au plus tard : une annotation qui arrive après cette
          lecture-là tombe dans la même fenêtre de quelques µs que `lstat`→`unlink`."""
        ou = None if st_la is None else _remettre(dfd, prive, nom, st_la)
        garde = None
        if _sha_fd(fd) != h:
            garde = _sauver(base, dfd, nom, _lire_fd(fd))
            if "/" not in garde:
                garde = os.path.join(base, dossier, garde)
        sortir(2, f"`{chemin}` a été REMPLACÉ" + (" puis RETIRÉ" if ou is None else "")
                  + " pendant le nettoyage (ce n'est plus le fichier que j'ai vérifié) — "
                  + ("je n'ai rien effacé" if ou is None else "je m'arrête là, celui-ci reste"
                     + ("" if ou == nom else f" sous `{os.path.join(base, dossier, ou)}`"))
                  + ("" if garde is None else f", et ses octets MODIFIÉS sont restaurés sous "
                                              f"`{garde}`")
                  + ". Donner un dossier neuf.")
    if _sha_fd(fd) != h:
        st_la = sous_le_nom_prive()
        if st_la is None or (st_la.st_dev, st_la.st_ino) != (st.st_dev, st.st_ino):
            # ⛔ 11e revue (repli Claude) : MODIFIÉ *puis* REMPLACÉ — mon inode porte les octets
            #    de quelqu'un d'autre ET n'a plus de nom. `remplace` rend son nom public au
            #    remplaçant et SAUVE mes octets modifiés (12e revue : c'est lui qui le fait,
            #    pour que les deux branches ne puissent plus diverger).
            remplace(st_la)
        ou = _remettre(dfd, prive, nom, st_la)
        sortir(2, f"`{chemin}` a été MODIFIÉ pendant le nettoyage (ses octets ne sont plus ceux du "
                  f"registre) — il reste tel quel"
                  + ("" if ou == nom else f", sous `{os.path.join(base, dossier, ou)}`")
                  + ", je m'arrête là. Donner un dossier neuf.")
    _sonde("empreinte-relue", nom)   # ⛔ 11e revue : l'identité se relit APRÈS l'empreinte
    st_la = sous_le_nom_prive()         # ⛔ 10e revue : l'IDENTITÉ sous le nom privé, relue ICI —
    if st_la is None or (st_la.st_dev, st_la.st_ino) != (st.st_dev, st.st_ino):   # cas M2 (le
        remplace(st_la)                 # rename a emporté un fichier de JNT) et Y/AA (visé après)
    os.unlink(prive, dir_fd=dfd)
    _sonde("apres-retrait", nom)
    if _sha_fd(fd) != h:
        ou = _sauver(base, dfd, nom, _lire_fd(fd))
        if "/" not in ou:
            ou = os.path.join(base, dossier, ou)
        sortir(2, f"`{chemin}` a été MODIFIÉ pendant que je l'effaçais — restauré tel quel sous "
                  f"`{ou}`, je m'arrête là. Donner un dossier neuf.")


def _lire_fd(fd):
    """Tous les octets du fichier ouvert `fd`, depuis le début — par le descripteur, jamais par nom."""
    os.lseek(fd, 0, os.SEEK_SET)
    morceaux = []
    while True:
        bloc = os.read(fd, 1 << 20)
        if not bloc:
            return b"".join(morceaux)
        morceaux.append(bloc)


def _sha_fd(fd):
    """Empreinte SHA-256 du fichier ouvert `fd`, relu depuis le début."""
    return hashlib.sha256(_lire_fd(fd)).hexdigest()


def construire(video, langue, n_images, base):
    video = os.path.abspath(video)          # les enfants changent de répertoire courant
    duree, pistes, depart = ffprobe(video)
    if "video" not in pistes:
        sortir(6, "AUCUNE PISTE VIDÉO — il n'y a aucun écran à montrer, donc aucun « ça » "
                  "ni « ce bouton-là » ne pourra être résolu. Un transcript nu n'est pas "
                  "ce que cet outil promet.")
    if "audio" not in pistes:
        sortir(3, "AUCUNE PISTE AUDIO dans ce fichier — l'écran a été capturé sans le "
                  "micro. Il n'y a rien à transcrire, et ce n'est PAS « il n'a rien dit ».")
    n_audio = pistes.count("audio")
    mesures = [niveaux(video, k) for k in range(n_audio)]
    actives = [k for k, (moy, crete) in enumerate(mesures)
               if crete is not None and crete >= SEUIL_CRETE_DB]
    if not actives:
        cretes = ", ".join(f"{c:.1f}" for _, c in mesures if c is not None) or "?"
        sortir(4, f"PISTE(S) AUDIO MUETTE(S) (crête {cretes} dB, seuil {SEUIL_CRETE_DB} dB) — "
                  "micro fermé ou mauvaise entrée. ⛔ Whisper INVENTE des phrases sur du "
                  "silence, avec des horodatages corrects. Refusé avant de le lancer.")

    # ⛔ LA SUPPRESSION VIENT APRÈS LES REFUS, JAMAIS AVANT (revue Codex, 11 sept. 2026).
    #    Avant, `--sortie` effaçait récursivement le dossier PUIS refusait en code 3 :
    #    un code d'échec se lit « rien n'a bougé », et c'était faux.
    #    [[reference_un_code_dechec_ne_garantit_pas_labsence_decriture]]
    # ⛔ ET ELLE NE TOUCHE QU'À UN DOSSIER QUE CET OUTIL A CRÉÉ (revue « repli Claude »).
    #    `--sortie ~/Documents` aurait effacé Documents. Le marqueur `.regarder` SIGNÉ est la
    #    seule preuve acceptée ; un dossier vide passe aussi.
    # ⭐ LE DOSSIER SE TIENT UNE FOIS, ET TOUT PASSE PAR CE DESCRIPTEUR (5e revue Codex, 12 sept.
    #    2026) : la preuve de propriété, le nettoyage, le registre, les transcripts, l'INDEX,
    #    les écrans. `O_NOFOLLOW` est LE garde contre un `--sortie` qui est un lien : un
    #    `islink()` par chemin, suivi d'un `tenir()` par chemin, laissait une fenêtre entre les
    #    deux — mesuré par Codex avec un `tenir` remplacé. Il n'y a plus de « entre ».
    try:
        os.makedirs(base, exist_ok=True)
    except FileExistsError:
        pass                                    # un lien ou un fichier à ce nom : `tenir` tranche
    bfd = tenir(base)
    try:
        if os.listdir(bfd):
            if not a_moi(bfd):
                sortir(2, f"`--sortie` vise un dossier qui existe et qui N'EST PAS À MOI : {base}\n"
                          f"   (pas de marqueur {MARQUEUR} signé). Je n'efface pas les fichiers de "
                          "JNT — donner un dossier neuf, ou un dossier déjà produit par cet outil.")
            nettoyer(base, bfd)                 # ⛔ jamais rmtree : seuls les fichiers AU REGISTRE partent
        # Le dossier privé (WAV, transcripts bruts) se tient lui aussi par descripteur : ffmpeg
        # et le transcripteur y écrivent par nom relatif, leur répertoire courant étant `pfd`.
        prive = tempfile.mkdtemp(prefix="regarder-prive-")
        pfd = tenir(prive)
        prives = {}                             # {nom: (dev, inode)} créés/retenus par CE run
        reg = None
        try:
            _sonde("prive-cree", prive)
            reg = Registre(bfd)                 # créé, signé, puis écrit par CE descripteur
            return _construire(video, langue, n_images, base, bfd, reg, pfd, duree, depart,
                               n_audio, mesures, actives, prives)
        except _Altere as e:
            sortir(2, f"dans {base} : {e}")
        finally:
            if reg is not None:
                if not reg.toujours_la():
                    print(f"⚠️  le registre `{MARQUEUR}` de {base} a été REMPLACÉ pendant le run : "
                          "mes fichiers y sont, mais ce dossier ne sera plus reconnu comme le "
                          "mien (refus au prochain run). Rien d'autre n'a été touché.",
                          file=sys.stderr)
                reg.fermer()
            # ⛔ 6e revue Codex : on effaçait TOUT nom à moi trouvé dans le privé — y compris
            #    un fichier de JNT glissé là pendant le run. Seuls les noms créés par ce run
            #    partent ; un dossier privé qui ne se vide pas reste, et on le dit.
            # ⛔ 7e revue : et seulement si le nom porte ENCORE l'inode créé (`_effacer_prive`).
            for nom, ino in prives.items():
                _effacer_prive(pfd, nom, ino)
            _retirer_prive(prive, pfd)
    finally:
        os.close(bfd)


def _construire(video, langue, n_images, base, bfd, reg, pfd, duree, depart, n_audio, mesures,
                actives, prives):
    moy, crete = mesures[actives[0]]
    print(f"🎧 langue forcée : {langue}   ·   ⏱ {duree:.0f} s   ·   "
          + " · ".join(f"piste {k + 1} : moy {m:.1f} / crête {c:.1f} dB"
                       for k, (m, c) in enumerate(mesures)))
    if n_audio > 1:
        print(f"🎚  {n_audio} PISTES AUDIO — transcrites SÉPARÉMENT (mélangées, la voix la "
              "plus forte masque l'autre).")
    for k in range(n_audio):
        if k not in actives:
            print(f"   · piste {k + 1} MUETTE (crête {mesures[k][1]:.1f} dB) — ignorée")

    # ⛔ CE BANDEAU DISAIT « mlx-whisper » EN DUR (corrigé le 20 sept. 2026, trouvé par
    #    une revue aveugle). Sur une machine Intel ou Linux, l'écran affirmait donc un
    #    moteur pendant qu'un AUTRE travaillait — et l'INDEX, lui, disait le vrai. Deux
    #    sources qui se contredisent, c'est pire qu'une seule qui se tait : on croit la
    #    première qu'on lit. Le nom du moteur n'est connu qu'APRÈS le 1er appel, donc
    #    ici on ne le nomme pas — la ligne « piste N transcrite par … » le fera.
    print("🎙  transcription locale, hors ligne (aucune clé API)…")
    # ⛔ `aveugles` — TROUVÉ PAR KIMI LE 20 SEPT. 2026. Quand l'amplitude n'est pas
    #    mesurable, `pics_par_fenetre` rend None, `segments_muets(None)` rend un ensemble
    #    VIDE, et AUCUNE réplique n'est marquée 🚫 INVENTÉE. L'avertissement partait sur
    #    stdout — l'INDEX, qui est l'artefact qu'on LIT (et qu'on relit des jours plus
    #    tard), n'en disait rien. Mesuré par Kimi : `grep -ci "INVENT" INDEX.md` → 0.
    #    👉 Un transcript sans aucune marque est IDENTIQUE, à la lecture, à un transcript
    #    dont chaque ligne a été vérifiée. C'est le garde aveugle qui se lit comme un
    #    garde vert. Il se dit donc DANS l'index.
    segments, muets, planchers, a_copier, vides, aveugles = [], set(), {}, [], [], []
    moteurs = set()
    for k in actives:
        segs, wav, a_debut, bruts, moteur = transcrire_piste(video, k, pfd, langue, prives)
        moteurs.add(moteur)
        a_copier += bruts
        if not segs:
            # ⛔ 8e revue Codex (12 sept. 2026) : une 2e piste NON muette dont le modèle ne rend
            #    rien passait pour transcrite — une ligne sur stdout, code 0, INDEX muet dessus.
            #    Cette voix est ABSENTE : ça se dit en ⚠️ et ça s'écrit dans l'INDEX.
            vides.append(k)
            print(f"⚠️  piste {k + 1} : NON muette (crête {mesures[k][1]:.1f} dB) mais le modèle n'en "
                  "a rendu AUCUNE réplique — cette voix est ABSENTE du transcript et de l'INDEX.",
                  file=sys.stderr)
        fd = _ouvrir_prive(pfd, wav, prives, prives[wav])
        with os.fdopen(fd, "rb") as f:
            pics = pics_par_fenetre(f, nom=wav)
        _effacer_prive(pfd, wav, prives.pop(wav))
        if pics is None:
            aveugles.append(k)
        # ⚠️ L'amplitude se juge dans l'horloge du WAV (celle des segments bruts)…
        res = segments_muets(pics, segs)
        if res:
            m, p_min, p_max = res
            planchers[k] = (p_min, p_max)
            muets |= {len(segments) + i for i in m}
        # … puis SEULEMENT les horodatages passent dans l'horloge de la vidéo (5e revue Codex,
        # 12 sept. 2026) : le WAV part à la première image AUDIO, les écrans à `start_time`.
        # Mesuré 61 ms sur la vidéo réelle, 0,7 s sur le banc de Codex — dans les deux cas
        # l'écran rattaché était celui d'AVANT la phrase. ⚠️ `transcript-piste-N.*` restent
        # bruts (horloge du WAV) ; `transcript.txt` et l'INDEX sont dans l'horloge de la vidéo.
        decalage = a_debut - depart
        if abs(decalage) >= 0.001:
            print(f"   · piste {k + 1} : le son part {decalage:+.3f} s par rapport à l'horloge de "
                  f"la vidéo — transcript recalé de {decalage:+.3f} s")
        for s in segs:
            s["debut"] += decalage
            s["fin"] += decalage
        segments += segs
    if not segments:
        sortir(5, "TRANSCRIPT VIDE alors que la piste audio n'est pas muette. C'est un "
                  "vrai défaut du moteur, pas un silence — ne rien conclure de la vidéo.")
    # Toutes les pistes ont rendu : les transcripts bruts entrent dans la sortie, maintenant
    # seulement (avant, ceux de la piste 1 restaient quand la piste 2 plantait — 6e revue Codex).
    for nom, donnees in a_copier:
        deposer(reg, nom, donnees)
    # Les pistes se fusionnent dans l'ordre du temps ; on garde la trace des indices.
    ordre = sorted(range(len(segments)), key=lambda i: segments[i]["debut"])
    segments = [segments[i] for i in ordre]
    muets = {nouveau for nouveau, ancien in enumerate(ordre) if ancien in muets}

    lignes = []
    for s in segments:
        mn, sc = divmod(int(s["debut"]), 60)
        etiquette = f" (piste {s['piste'] + 1})" if n_audio > 1 else ""
        lignes.append(f"[{mn:02d}:{sc:02d}]{etiquette} {s['texte']}")
    _sonde("avant-transcript")
    deposer(reg, "transcript.txt", ("\n".join(lignes) + "\n").encode())
    if planchers:
        print("   · plancher de bruit (lu sur ±5 s autour de chaque réplique) : " + " · ".join(
            f"piste {k + 1} {a:.1f}…{b:.1f} dB (muet sous plancher + {SEUIL_DESSUS_PLANCHER_DB:.0f}, "
            f"plafond {PLAFOND_MUET_DBFS:.0f})" for k, (a, b) in planchers.items()))
    if muets:
        print(f"⚠️  {len(muets)} réplique(s) ENTENDUE(S) SUR DU SILENCE — marquées "
              "🚫 INVENTÉE dans l'INDEX. Whisper hallucine sur les passages muets.")

    # Les instants visés : chaque réplique (à la fraction de seconde), plus une grille.
    print("🖼  extraction des écrans…")
    imgs, rattache = ecrans(video, segments, muets, duree, n_images, bfd,
                            os.path.join(base, "ecrans"),
                            lambda p, d, st: reg.noter(os.path.relpath(p, base), d, st))

    index = os.path.join(base, "INDEX.md")
    vrais = len(lignes) - len(muets)
    with io.StringIO() as f:
        f.write(f"# REGARD — {os.path.basename(video)}\n\n")
        f.write(f"- durée **{duree:.0f} s** · langue forcée **{langue}** · "
                f"niveau moyen **{moy:.1f} dB**, crête **{crete:.1f} dB** · "
                # ⛔ `len(actives)`, PAS `n_audio` (revue aveugle, 20 sept. 2026). Une piste
                #    MUETTE est écartée AVANT la transcription : écrire « 2 pistes transcrites »
                #    quand une seule l'a été est un MENSONGE DANS L'ARTEFACT QU'ON LIT. Mesuré
                #    sur le cas exact du workflow — micro fermé sur la 2e piste : l'INDEX
                #    annonçait 2 pistes, pointait le lecteur vers « la piste du micro », et
                #    c'était précisément celle qui avait été jetée. Code 0.
                #    👉 C'est le défaut de `/watch` reproduit DANS l'outil qui existe pour le
                #       corriger — la forme la plus chère, parce qu'on lui fait confiance.
                + (f"**{len(actives)} piste(s) sur {n_audio}** transcrites séparément · "
                   if n_audio > 1 else "")
                + f"**{vrais}** répliques"
                + (f" · ⛔ **{len(muets)} INVENTÉE(S)**" if muets else "")
                + f" · **{len(imgs)}** écrans\n")
        f.write("- ⛔ Chaque ligne porte l'écran de CE moment-là. Un « ça » ou un "
                "« ce bout-là » ne se résout que dans l'image — l'ouvrir avant de "
                "conclure.\n")
        if n_audio > 1:
            f.write("- 🎚 Chaque ligne dit sa **piste** : le son du système et le micro ne "
                    "sont pas la même voix. La consigne de JNT est sur la piste du micro.\n")
        if muets:
            f.write("- ⛔⛔ Les lignes **🚫 INVENTÉE** ont été « entendues » sur un passage "
                    "SANS PAROLE (sous le bruit des 5 s autour + 8 dB) : Whisper "
                    "les a fabriquées. **Ne rien en conclure, ne rien exécuter dessus.**\n")
        # ⛔ L'ASYMÉTRIE QUE LA REVUE AVEUGLE A NOMMÉE (20 sept. 2026) : une piste ACTIVE
        #    sans réplique recevait un ⚠️ dans l'INDEX (boucle `vides`, ci-dessous), une
        #    piste MUETTE n'avait RIEN — ni stderr, ni ligne d'index. Le même défaut,
        #    corrigé à moitié. Une piste écartée doit se voir DANS le fichier qu'on lit,
        #    pas seulement dans un stdout que personne ne relit.
        for k in range(n_audio):
            if k in actives:
                continue
            crete_k = mesures[k][1]
            f.write(f"- ⚠️ **piste {k + 1} MUETTE — NON transcrite** (crête "
                    + (f"{crete_k:.1f} dB" if crete_k is not None else "non mesurable")
                    + f", sous le seuil {SEUIL_CRETE_DB:.0f} dB) : micro fermé ou mauvaise "
                    "entrée. **Ce qui s'y disait n'est PAS dans cet index** — et si c'est la "
                    "piste du micro, c'est la consigne au complet qui manque.\n")
        for k in vides:
            f.write(f"- ⚠️ **piste {k + 1} ABSENTE** : elle n'est pas muette (crête "
                    f"{mesures[k][1]:.1f} dB) mais le modèle n'en a rendu aucune réplique — ce qui "
                    "s'y disait n'est PAS dans cet index.\n")
        # ⭐ Le moteur est écrit dans l'artefact, pas seulement crié à l'écran : l'INDEX
        #    se relit des jours plus tard, quand plus personne ne se souvient de la
        #    machine sur laquelle il a été produit.
        if moteurs:
            f.write(f"- 🔊 transcrit par **{' · '.join(sorted(moteurs))}**\n")
        for k in aveugles:
            f.write(f"- ⚠️ **piste {k + 1} : LE GARDE DES RÉPLIQUES INVENTÉES N'A PAS PU "
                    "S'ARMER** — l'amplitude de cette piste n'était pas mesurable, donc "
                    "**aucune ligne n'a pu être marquée 🚫 INVENTÉE**. ⛔ Ne pas lire "
                    "l'absence de marque comme une vérification : rien n'a été vérifié "
                    "ici. Whisper fabrique des phrases plausibles sur du silence, avec "
                    "des horodatages corrects.\n")
        f.write("\n---\n\n")
        derniere = None
        for i, (s, l) in enumerate(zip(segments, lignes)):
            f.write(f"{'🚫 INVENTÉE · ' if i in muets else ''}{l}\n")
            if i not in rattache:
                # ⛔ REVUE AVEUGLE, 20 SEPT. 2026 — `continue` NU : la réplique s'écrivait
                #    sans sa ligne « ↳ écran » ET SANS UN MOT. C'est le défaut qu'on
                #    combat, retourné comme un gant : le son sans l'image au lieu de
                #    l'image sans le son. La promesse du produit — « l'écran de CE
                #    moment-là » — n'était pas tenue, et l'INDEX ne le disait pas.
                f.write("  ↳ ⚠️ **AUCUN ÉCRAN pour cette réplique** — le « là » de « ce "
                        "bouton-là » n'est PAS résolu ici : ne rien déduire de ce qui "
                        "était affiché.\n")
                continue
            proche = rattache[i]
            vise = min(max(0.0, s["debut"]), max(0.0, duree))
            # ⛔ 12e revue Codex (13 sept. 2026) : la ligne « ↳ écran » ne s'écrit pas quand la
            #    réplique PARTAGE son écran avec la précédente — donc l'avertissement de repli
            #    ne s'écrivait pas non plus, et l'artefact redevenait muet (mesuré : deux
            #    répliques, un seul ↳, zéro avertissement). Un repli force donc sa ligne.
            rate = abs(proche[0] - vise) > 1e-9
            if proche[1] != derniere or rate:
                ecart = abs(proche[0] - s["debut"])
                marque = "" if ecart <= 1.5 else f" ⚠️ écran le plus proche à {ecart:.0f} s"
                # ⛔ 7e revue Codex (12 sept. 2026) : quand l'image de la vidéo commence APRÈS
                #    le son, la réplique reçoit la 1re image — celle d'APRÈS — sans un mot.
                #    On dit qu'aucune image n'existait à cet instant : l'écran ne prouve rien
                #    sur ce qui était visible AVANT.
                #    ⛔ 8e revue : la tolérance était 1 ms — une réplique 0,5 ms avant la 1re
                #    image n'avait pas d'avertissement, et à 1,5 ms il disait « +0.0 s ». La
                #    tolérance est celle du choix d'image (1 µs) et l'avance se dit en ms.
                # ⛔ 11e revue Codex (12 sept. 2026) : quand ffmpeg refuse les TROIS images
                #    visées, la réplique reçoit l'écran le plus proche — l'avertissement partait
                #    sur stderr, et l'INDEX, qui est l'artefact qu'on lit, n'en disait rien.
                if rate:
                    marque += (f" ⚠️ AUCUNE image RENDUE à l'instant de cette réplique — c'est "
                               f"l'écran de {proche[0]:.3f} s ({_duree(abs(proche[0] - vise))} "
                               "d'écart) qui la remplace : ne rien conclure sur ce qui était "
                               "visible ICI")
                avance = proche[2] - vise
                if avance > 1e-6:
                    marque += (f" ⚠️ AUCUN écran rendu à cet instant — écran d'APRÈS "
                               f"({_duree(avance)}) : ne rien conclure sur ce qui était "
                               "visible AVANT")
                f.write(f"  ↳ écran ~{mmss(proche[0])} · `{proche[1]}`{marque}\n")
                derniere = proche[1]
        f.write("\n---\n\n## Tous les écrans, dans l'ordre\n\n")
        for t, p, r in imgs:
            apres = f" (image rendue : {r:.3f} s — la première après cet instant, {_duree(r - t)})" if r > t + 1e-6 else ""
            f.write(f"- `[{mmss(t)}]` `{p}`{apres}\n")
        deposer(reg, "INDEX.md", f.getvalue().encode())

    print(f"\n{'✅' if imgs else '⛔'} {vrais} répliques"
          + (f" · ⛔ {len(muets)} inventée(s)" if muets else "")
          + (f" · {len(imgs)} écrans" if imgs else " · ⛔ AUCUN ÉCRAN"))
    print(f"📄 À LIRE : {index}")

    # ⛔ ZÉRO RÉPLIQUE VRAIE N'EST PAS UN SUCCÈS (revue aveugle, 20 sept. 2026).
    #    Le code 5 couvrait « transcript VIDE » ; il ne couvrait pas « transcript
    #    ENTIÈREMENT HALLUCINÉ » — des lignes existent, elles sont toutes marquées
    #    🚫 INVENTÉE, et l'outil rendait `✅ 0 répliques · ⛔ 9 inventée(s)`, code 0.
    #    Un crochet vert sur une vidéo où personne n'a rien dit.
    # ⭐ L'INDEX est écrit AVANT de sortir, et on le nomme : il porte les lignes
    #    inventées, qui sont la PREUVE de ce qui s'est passé. Refuser en effaçant
    #    la preuve obligerait à relancer pour comprendre.
    if not vrais:
        sortir(5, f"AUCUNE réplique vraie — les {len(muets)} ligne(s) rendues sont toutes "
                  f"marquées INVENTÉE (fabriquées par le modèle sur du silence).\n"
                  f"   ⛔ Ne rien en conclure. L'index est écrit pour la preuve : {index}\n"
                  f"   · micro trop loin ou trop bas ? · mauvaise langue (`--langue`) ?")

    # ⛔ CODE 8 — « RIEN D'EXPLOITABLE ». Né de la revue aveugle du 20 sept. 2026, qui a
    #    nommé le trou que les 7 autres codes laissaient : ILS RÉPONDENT TOUS À « la
    #    machine a-t-elle fonctionné ? », AUCUN À « ai-je entendu ET VU quelque chose
    #    d'utilisable ? ». Ici, ffmpeg n'a rendu AUCUNE image : chaque réplique est
    #    orpheline, l'outil se réduit à un transcript — c'est-à-dire exactement ce que
    #    fait le concurrent qu'on remplace, et pour la même raison (un tuyau qui échoue
    #    sans faire échouer le programme).
    # ⭐ Comme pour le 5 : l'INDEX est écrit AVANT, et nommé. La preuve ne s'efface pas.
    if not imgs:
        sortir(8, f"AUCUN ÉCRAN rendu sur toute la vidéo — {len(lignes)} réplique(s) "
                  f"transcrite(s), zéro image.\n"
                  f"   ⛔ La moitié de la réponse manque : « ce bouton-LÀ » ne se résout "
                  f"pas, et le « là » n'existe QUE dans l'image.\n"
                  f"   L'index est écrit pour la preuve : {index}\n"
                  f"   · piste vidéo illisible ? · ffmpeg trop vieux ? → `--autotest`")
    return index


# ══════════════════════════════════════════════════════════════════════════════
# AUTOTESTS — un gate jamais vu bloquer ne garde rien
# ══════════════════════════════════════════════════════════════════════════════

def _voix(tmp, nom, phrase, voix="Thomas"):
    aiff = os.path.join(tmp, nom + ".aiff")
    subprocess.run(["say", "-v", voix, "-o", aiff, phrase], check=True)
    return aiff


def autotest():
    """CONTRÔLE POSITIF : une vidéo fabriquée qui dit une phrase qu'aucun modèle ne devine.

    ⛔ Sans lui, une sonde muette rendrait « rien dit » et se lirait comme une vidéo sans
       parole. On vérifie que la PHRASE revient, pas que la commande finit sans planter.
    """
    phrase = "le bouton orange en haut à droite monte-le de vingt pixels"
    # ⚠️ Chaque attendu est une LISTE DE FORMES ACCEPTÉES. Le 11 sept. 2026, l'autotest
    #    a rendu 🔴 CASSÉ sur un tuyau SAIN : Whisper normalise « vingt » en « 20 ».
    #    Un contrôle positif calé sur UNE seule écriture du mot attendu échoue sur la
    #    transcription correcte — c'est le test qui ment, pas l'outil.
    attendus = [("orange",), ("vingt", "20"), ("pixel",)]
    tmp = tempfile.mkdtemp(prefix="regarder-autotest-")
    try:
        if not shutil.which("say"):
            print("⚪ NON REJOUÉ — `say` absent (macOS requis)"); return 3
        # ⛔ LA VOIX SE VÉRIFIE, ELLE NE SE SUPPOSE PAS — trouvé par Kimi le 20 sept. 2026,
        #    et MESURÉ : `say -v ZZZZ -o fichier.aiff "essai"` rend **EXIT 0** et un vrai
        #    fichier audio, lu par la voix PAR DÉFAUT. Sur un Mac où `Thomas` n'est pas
        #    installé, l'autotest fabriquait donc sa phrase française avec une voix
        #    anglaise ; transcrite en `--langue fr`, elle rend un charabia du genre
        #    « le logo en ôtus de trôpe petit », la phase 1 échoue, et le README fait alors
        #    conclure « le problème est ailleurs, pas dans l'outil » — FAUX, et c'est le
        #    contrôle positif lui-même qui ment.
        #    ⭐ Un repli SILENCIEUX dans la fabrique du banc d'essai rend un ROUGE sur une
        #    installation SAINE. On refuse en NOMMANT la voix : « non rejoué » n'est pas
        #    « cassé », et les deux ne doivent pas se lire pareil.
        voix_dispo = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
        # ⚠️ `re.search`, PAS `re.match` : `re.match` n'essaie qu'à la POSITION 0, même
        #    avec `re.M` — et `Thomas` n'est jamais la première voix de la liste. Écrit
        #    avec `match`, ce garde rendait « voix absente » sur une machine qui l'a
        #    (mesuré tout de suite après l'avoir écrit). Un garde faux coûte le prix
        #    du défaut qu'il prétend couvrir.
        if not re.search(r"^Thomas\s", voix_dispo, re.M):
            print("⚪ NON REJOUÉ — la voix `Thomas` (fr_FR) n'est pas installée sur cette "
                  "machine.\n   ⛔ Ce n'est PAS un défaut de l'outil : sans elle, `say` "
                  "retombe EN SILENCE sur la voix par défaut (mesuré : exit 0), le banc "
                  "d'essai parle anglais, et l'autotest rendrait un faux rouge.\n"
                  "   Réglages ▸ Accessibilité ▸ Contenu énoncé ▸ Voix système ▸ Français.")
            return 3
        aiff = _voix(tmp, "voix", phrase)
        video = os.path.join(tmp, "faux-screenrecord.mp4")
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
             "-i", "testsrc=size=1280x720:rate=10", "-i", aiff,
             "-shortest", "-pix_fmt", "yuv420p", video], check=True)
        base = os.path.join(tmp, "regard")
        construire(video, "fr", 8, base)
        texte = open(os.path.join(base, "transcript.txt")).read().lower()
        manquants = [f[0] for f in attendus if not any(v in texte for v in f)]
        n_img = len(os.listdir(os.path.join(base, "ecrans")))
        if manquants:
            print(f"\n🔴 CASSÉ — mots absents du transcript : {manquants}\n{texte[:300]}")
            return 1
        if n_img < 2:
            print(f"\n🔴 CASSÉ — {n_img} écran(s) extrait(s), il en fallait plusieurs")
            return 1
        if "INVENTÉE" in open(os.path.join(base, "INDEX.md")).read():
            print("\n🔴 CASSÉ — une vraie réplique a été marquée INVENTÉE sur une vidéo saine")
            return 1
        print(f"\n✅ AUTOTEST PASSÉ — la phrase est revenue du son, {n_img} écrans extraits")
        print(f"   transcript : {texte.strip()[:120]}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def autotest_second_moteur():
    """LE 2e MOTEUR : celui que CETTE machine n'utilise pas par défaut marche-t-il ?

    ⛔⛔ POURQUOI CETTE PHASE EXISTE. L'outil a deux moteurs de voix — `mlx-whisper`
       (puce graphique Apple) et `faster-whisper` (processeur : Mac Intel, Linux, WSL2).
       Sur une machine donnée, UN SEUL des deux sert. L'autre n'est donc JAMAIS exercé :
       du code multiplateforme qui n'a jamais tourné, et qu'on annonce comme fonctionnel.
       ⭐ Ce n'est pas théorique : le 20 sept. 2026, un vestige `import mlx_whisper`
       codé en dur dans l'installeur tuait Mac Intel, Linux ET WSL2 en code 4 — et rien
       sur la machine de développement (Apple Silicon) ne pouvait le voir, parce que les
       deux contrôles y passaient. Il a fallu une revue aveugle qui SIMULE l'autre
       machine. **Cette phase est là pour que la machine le fasse elle-même.**

    ⚠️ ⚪ NON REJOUÉ n'est PAS un échec : si le 2e moteur n'est pas installé (le cas
       normal), il n'y a rien à prouver ici. Mais « non rejoué » et « cassé » ne doivent
       jamais se lire pareil — c'est le sens du ⚪.
    """
    # ⛔ LES DEUX MOTEURS VIVENT DANS LE VENV, PAS DANS CE PYTHON-CI. Interroger
    #    `sys.executable` rendrait « absent » pour les DEUX, toujours — la phase serait
    #    ⚪ à vie et ne garderait rien. C'est le même piège que la sonde qui répond zéro
    #    partout parce qu'elle regarde au mauvais endroit.
    venv_py = os.path.expanduser("~/.venvs/transcription/bin/python")
    if not os.path.exists(venv_py):
        print("⚪ NON REJOUÉ — le venv de transcription est introuvable "
              f"({venv_py}) : lancer l'installeur.")
        return 3
    def installe(mod):
        r = subprocess.run([venv_py, "-c",
                            f"import importlib.util as u,sys;"
                            f"sys.exit(0 if u.find_spec({mod!r}) else 9)"],
                           capture_output=True)
        return r.returncode == 0
    presents = {m: installe(m) for m in ("mlx_whisper", "faster_whisper")}
    if not any(presents.values()):
        print("⚪ NON REJOUÉ — aucun moteur installé dans le venv : lancer l'installeur.")
        return 3
    # Le moteur COURANT est celui que `moteur_voix()` choisirait : mlx d'abord.
    courant = "mlx" if presents["mlx_whisper"] else "cpu"
    autre = "cpu" if courant == "mlx" else "mlx"
    module = "faster_whisper" if autre == "cpu" else "mlx_whisper"
    if not presents[module]:
        print(f"⚪ NON REJOUÉ — `{module}` (le 2e moteur) n'est pas installé sur cette "
              f"machine.\n   ⛔ Ce n'est PAS un défaut : cette machine tourne sur "
              f"`{courant}`, et c'est le bon choix pour elle.\n"
              f"   👉 Pour exercer l'autre chemin ici : "
              f"`~/.venvs/transcription/bin/pip install {module.replace('_', '-')}`")
        return 3
    if not shutil.which("say"):
        print("⚪ NON REJOUÉ — `say` absent (macOS requis pour fabriquer le banc)")
        return 3
    phrase = "le bouton orange en haut à droite monte-le de vingt pixels"
    attendus = [("orange",), ("vingt", "20"), ("pixel",)]
    tmp = tempfile.mkdtemp(prefix="regarder-moteur2-")
    try:
        aiff = _voix(tmp, "voix", phrase)
        video = os.path.join(tmp, "banc.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=1280x720:rate=10", "-i", aiff,
                        "-shortest", "-pix_fmt", "yuv420p", video], check=True)
        base = os.path.join(tmp, "regard")
        # ⭐ C'EST ICI QUE TOUT SE JOUE : on FORCE l'autre moteur. Sans ce forçage, le
        #    test relancerait le moteur déjà prouvé et rendrait un vert qui ne prouve
        #    rien — un contrôle positif qui teste la mauvaise chose est pire qu'absent.
        ancien = os.environ.get("REGARDER_MOTEUR")
        os.environ["REGARDER_MOTEUR"] = autre
        try:
            construire(video, "fr", 8, base)
        finally:
            if ancien is None:
                os.environ.pop("REGARDER_MOTEUR", None)
            else:
                os.environ["REGARDER_MOTEUR"] = ancien
        texte = io.open(os.path.join(base, "transcript.txt"), encoding="utf-8").read().lower()
        manquants = [f[0] for f in attendus if not any(v in texte for v in f)]
        if manquants:
            print(f"\n🔴 CASSÉ — le 2e moteur ({autre}) n'a pas rendu : {manquants}\n"
                  f"{texte[:300]}")
            return 1
        index = io.open(os.path.join(base, "INDEX.md"), encoding="utf-8").read()
        # ⛔ Et il doit se NOMMER : un moteur qui travaille sans le dire, c'est le
        #    repli silencieux — le défaut que tout cet outil existe pour empêcher.
        if "transcrit par" not in index:
            print("\n🔴 CASSÉ — le 2e moteur a transcrit sans se nommer dans l'INDEX")
            return 1
        nomme = [l for l in index.splitlines() if "transcrit par" in l][0]
        print(f"\n✅ LE 2e MOTEUR ({autre}) REND LA PHRASE — et il se nomme")
        print(f"   {nomme.strip()}")
        print(f"   transcript : {texte.strip()[:120]}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def autotest_alignement():
    """L'ÉCRAN ANNONCÉ À [mm:ss] EST-IL VRAIMENT CELUI DE [mm:ss] ?

    ⛔ LE DÉFAUT LE PLUS DANGEREUX DE CET OUTIL, ET IL EST MUET. Un écran décalé
      n'a l'air de rien : je décris alors un bouton qui n'est pas celui dont JNT
      parle, avec un horodatage juste à côté. Rien ne signale l'erreur — ni une
      exception, ni un vide, ni un chiffre aberrant.

    ⭐ LE BANC : une vidéo où CHAQUE SECONDE porte une couleur unique, décodable.
      On extrait, on relit la couleur, on retrouve la seconde. Zéro jugement humain.

    ⭐⭐ ET UN 2e BANC À IMAGES VARIABLES (3e revue Codex, 12 sept. 2026) : 4 images aux
      PTS 0 · 0,90 · 1,96 · 1,99 s — la forme réelle d'un screen record macOS. À 1,00 s,
      l'écran est celui de 0,90 s ; l'ancien `-ss t` rendait celui de 1,96 s. Un banc à
      cadence fixe ne peut PAS voir cette erreur : elle y vaut une image, 16 ms.

    ⚠️⚠️ LE BANC A MENTI DEUX FOIS AVANT DE MESURER QUOI QUE CE SOIT (11 sept. 2026).
      1re version : pas de couleur de 6 unités — or le JPEG déplace le rouge de ~7.
      2e version : pas de 12. Dans les deux cas la sonde ne pouvait pas distinguer
      deux secondes voisines, et elle a rendu « 1,00 s » puis « 1,67 s » de dérive :
      des chiffres PLAUSIBLES, entièrement dans son propre bruit. Ils ont d'abord
      fait accuser un outil sain, puis fait croire que la correction avait empiré
      les choses. **Pas de 32 unités** ici, très au-dessus du bruit : c'est ce qui
      rend le 0,00 s significatif.
      👉 Une sonde dont le bruit vaut la grandeur mesurée ne mesure rien.
    """
    if not shutil.which("say"):
        print("⚪ NON REJOUÉ — `say` absent (macOS requis)"); return 3
    tmp = tempfile.mkdtemp(prefix="regarder-align-")
    global instants, TRANSCRIRE
    try:
        # ⚠️ LE BANC DOIT DURER. Une dérive s'ACCUMULE : sur 5 s elle est sous le seuil
        #    et l'autotest passerait au vert sur un outil décalé. 20 s de banc, donc on
        #    ALLONGE la piste audio au silence (`apad`) plutôt que de laisser `-shortest`
        #    couper la vidéo à la longueur de la phrase.
        aiff = _voix(tmp, "v", "Je parle pendant que les couleurs defilent, "
                               "une couleur differente a chaque seconde du test.")
        long_aiff = os.path.join(tmp, "v20.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", aiff,
                        "-af", "apad", "-t", "20", long_aiff], check=True)
        # ⭐ Une couleur par DEMI-seconde (revue Codex, 12 sept. 2026) : à la seconde, une
        #    troncature `int(debut)` — 1,7 s rendu comme 1,0 s — restait invisible.
        seg = []
        for n in range(40):
            r, g, b = (n % 8) * 32, (n // 8) * 32, 64      # pas de 32 : hors du bruit JPEG
            f = os.path.join(tmp, f"s{n:03d}.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                            "-i", f"color=c=0x{r:02x}{g:02x}{b:02x}:size=640x360:d=0.5:r=60",
                            "-pix_fmt", "yuv420p", f], check=True)
            seg.append(f)
        liste = os.path.join(tmp, "l.txt")
        open(liste, "w").write("".join(f"file '{f}'\n" for f in seg))
        muet = os.path.join(tmp, "m.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                        "-i", liste, "-c", "copy", muet], check=True)
        video = os.path.join(tmp, "banc.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", muet, "-i", long_aiff,
                        "-shortest", "-pix_fmt", "yuv420p", video], check=True)

        def couleur(chemin):
            px = subprocess.run(["ffmpeg", "-v", "error", "-i", chemin, "-vf", "scale=1:1",
                                 "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                                capture_output=True).stdout
            return None if len(px) < 3 else min(round(px[0] / 32), 7) + 8 * round(px[1] / 32)

        # ⭐⭐ RÉPLIQUES PLACÉES, SANS WHISPER (revue Codex, 12 sept. 2026). 7 images sur 20 s
        #    → grille à 2,857 s (0 · 2,86 · 5,71 · 8,57 · 11,43 · …), qui tombe exprès au
        #    MILIEU des demi-secondes. Trois pièges, un par réplique :
        #      · 1,7 s — une troncature `int(debut)` la rend à 1,0 s : autre demi-seconde ;
        #      · 11,5 s — 0,07 s APRÈS le point de grille 11,43 s : un dédoublonnage qui
        #        garde le PREMIER instant efface la réplique et lui donne l'écran de 11,43 s,
        #        qui montre encore la demi-seconde D'AVANT. C'est le cas Codex ;
        #      · 8,4 s — 0,17 s AVANT la grille 8,57 s : c'est la grille qui doit s'effacer ;
        #      · 19,98 s — 20 ms avant la FIN (vidéo à 60 i/s) : l'écran doit être celui de
        #        19,98 s, pas un recul « de sécurité » à 19,95 s (2e revue Codex, 12 sept.) ;
        #      · 19,52 s — 20 ms APRÈS le dernier changement de couleur : un recul « seulement
        #        en fin de vidéo » y rend la demi-seconde d'avant (3e revue Codex, 12 sept.) ;
        #      · 8,9995 s — 0,5 ms AVANT la même frontière : la tolérance de 1 ms (déclarée
        #        « équivalente » jusqu'à la 11e revue) y rend l'écran d'APRÈS. Codex l'a mesuré :
        #        à 60 Hz, deux images sont à 16,7 ms l'une de l'autre, mais une réplique peut
        #        tomber à 0,5 ms de la suivante — l'espacement des images ne prouve rien ;
        #      · 8,995 s — 5 ms AVANT une frontière (à 60 i/s, l'image de 9,000 existe) : une
        #        tolérance de 10 ms sur le choix de l'image rend l'écran d'APRÈS (8e revue).
        #    Chaque réplique doit recevoir l'écran de SON demi-seconde, à l'instant EXACT.
        places = [{"debut": 1.7, "fin": 2.3, "texte": "a"}, {"debut": 8.4, "fin": 9.0, "texte": "b"},
                  {"debut": 11.5, "fin": 12.1, "texte": "c"}, {"debut": 19.52, "fin": 19.9, "texte": "e"},
                  {"debut": 19.98, "fin": 20.0, "texte": "d"}, {"debut": 8.995, "fin": 9.4, "texte": "f"},
                  {"debut": 8.9995, "fin": 9.45, "texte": "g"}]
        tfd = tenir(tmp)
        _, rattache = ecrans(video, places, set(), 20.0, 7, tfd, os.path.join(tmp, "places"))
        faux = []
        for i, s in enumerate(places):
            t_img, chemin = rattache.get(i, (None, None, None))[:2]
            n = couleur(chemin) if chemin else None
            attendu = int(s["debut"] / 0.5)
            if t_img is None or abs(t_img - s["debut"]) > 0.001 or n != attendu:
                faux.append(f"   réplique à {s['debut']} s → écran {t_img} s, couleur nº{n} "
                            f"(attendu nº{attendu})")
        if faux:
            print("\n".join(faux))
            print("\n🔴 CASSÉ — une réplique PLACÉE reçoit un autre écran que celui de son "
                  "instant : « ce bouton-là » désignera le mauvais bouton.")
            return 1
        print(f"   ✅ {len(places)} répliques placées (1,7 · 8,4 · 8,995 · 8,9995 · 11,5 · 19,52 · 19,98 s) → chacune SON demi-seconde, à l'instant exact")

        # ⭐⭐ LE MÊME BANC, L'HORLOGE DÉCALÉE DE 0,5 s (4e revue Codex, 12 sept. 2026). Codex a
        #    ré-encodé une vidéo avec `-output_ts_offset 0.5` : `start_time` 0,5, images B, et
        #    CHAQUE écran arrivait 0,5 s en retard — l'outil demandait un PTS absolu à un `-ss`
        #    qui compte depuis start_time. Le banc se vérifie lui-même (start_time ≈ 0,5, sinon
        #    rien n'est mesuré), et le WAV doit commencer à parler au MÊME instant que sur le
        #    banc d'origine : Whisper et les écrans lisent la même horloge, celle de start_time.
        decale = os.path.join(tmp, "decale.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-output_ts_offset", "0.5",
                        "-c:v", "libx264", "-preset", "ultrafast", "-bf", "3", "-c:a", "aac",
                        decale], check=True)
        pts_decale, depart, _ = instants(decale)
        if abs(depart - 0.5) > 0.05:
            print(f"⚪ BANC INVALIDE — `decale.mp4` a start_time {depart:.3f}, attendu ≈ 0,5 : "
                  "le décalage d'horloge n'est pas reproduit, rien mesuré"); return 1
        # ⚠️ L'AAC ajoute ~46 ms d'amorce : la piste audio part à 0,454, la vidéo à 0,500, et
        #    `start_time` (le plus tôt des deux) vaut 0,454. Dans l'horloge relative, TOUT le
        #    banc est donc décalé de `glissement` = 0,046 s — le son (mesuré sur l'attaque de la
        #    voix) comme l'image (premier PTS relatif). Les deux mesures doivent concorder,
        #    sinon la prémisse « une seule horloge » est fausse et rien n'est prouvé.
        glissement = pts_decale[0]

        def onset(v):
            wav = os.path.join(tmp, "onset.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-map", "0:a:0", "-vn",
                            "-ac", "1", "-ar", "16000", wav], check=True)
            import wave, array
            with wave.open(wav) as w:
                ech = array.array("h"); ech.frombytes(w.readframes(w.getnframes()))
            for i, e in enumerate(ech):
                if abs(e) > 1000:
                    return i / 16000
            return None
        o_banc, o_decale = onset(video), onset(decale)
        if o_banc is None or o_decale is None or abs((o_decale - o_banc) - glissement) > 0.01:
            print(f"⚪ BANC INVALIDE — la voix attaque à {o_decale} s sur le banc décalé contre "
                  f"{o_banc} s sur l'original (glissement {o_decale - o_banc:+.4f} s), mais la 1re "
                  f"image relative est à {glissement:.4f} s : le son et l'image ne partagent pas "
                  "la même horloge, rien mesuré")
            return 1
        _, rattache = ecrans(decale, places, set(), 20.0, 7, tfd, os.path.join(tmp, "places-decale"))
        faux = []
        for i, s in enumerate(places):
            t_img, chemin = rattache.get(i, (None, None, None))[:2]
            n = couleur(chemin) if chemin else None
            # La réplique à `debut` (horloge du WAV) voyait la couleur de l'instant
            # `debut − glissement` du banc d'origine.
            attendu = int((s["debut"] - glissement) / 0.5)
            if t_img is None or n != attendu:
                faux.append(f"   réplique à {s['debut']} s → couleur nº{n} (attendu nº{attendu})")
        if faux:
            print("\n".join(faux))
            print(f"\n🔴 CASSÉ — sur une vidéo dont l'horloge part à {depart:.2f} s, les écrans "
                  "sont DÉCALÉS : « ce bouton-là » désignera ce qui était affiché une demi-seconde "
                  "plus tard.")
            return 1
        print(f"   ✅ horloge décalée (start_time {depart:.3f} s, images B, glissement AAC "
              f"{glissement:.3f} s mesuré sur le son ET l'image) : les 5 répliques placées reçoivent "
              "la couleur qu'elles voyaient")

        # ⭐⭐ LA MÊME HORLOGE, DE BOUT EN BOUT (6e revue Codex, 12 sept. 2026). Le test ci-dessus
        #    appelle `ecrans` avec `decalage` = 0 : il ne voit pas ce que `transcrire_piste` MESURE.
        #    Mesuré par Codex : la sonde `ashowinfo` SANS `-copyts` rendait un début de piste
        #    déjà NORMALISÉ (0 sur une piste qui part à 0,5 ; 0 sur un début négatif), donc
        #    `decalage = a_debut − depart` valait −0,454 ici — et chaque écran partait d'une
        #    demi-seconde. Ici, `construire` tourne pour de vrai avec un transcripteur qui répond
        #    3 répliques posées sur la voix, et l'INDEX doit lier la couleur qu'elles voyaient.
        faux_py = os.path.join(tmp, "faux-transcripteur-horloge.py")
        open(faux_py, "w").write(
            "import json, os, sys\n"
            "detail = sys.argv[sys.argv.index('--detail-json') + 1]\n"
            "segs = json.loads(os.environ['FAUX_SEGMENTS'])\n"
            "open(sys.argv[2], 'w').write(''.join(s['texte'] + '\\n' for s in segs))\n"
            "json.dump(segs, open(detail, 'w'))\n")
        # Trois répliques posées LÀ OÙ LA VOIX PARLE (sinon le marqueur INVENTÉE les écarte, à
        # raison) : lues sur `onset.wav`, qui est la piste du banc décalé (dernier `onset`),
        # à 0,2 s dans une demi-seconde bruyante, jamais à cheval sur une frontière.
        import wave, array
        with wave.open(os.path.join(tmp, "onset.wav")) as w:
            ech = array.array("h"); ech.frombytes(w.readframes(w.getnframes()))
        trois = []
        for k in range(2, 36):
            if trois and k * 0.5 - trois[-1]["debut"] < 1.0:
                continue
            fen = ech[int((k * 0.5 + 0.1) * 16000):int((k * 0.5 + 0.45) * 16000)]
            if fen and sum(abs(e) for e in fen) / len(fen) > 1500:
                trois.append({"debut": round(k * 0.5 + 0.2, 2), "fin": round(k * 0.5 + 0.45, 2),
                              "texte": "xyz"[len(trois)]})
            if len(trois) == 3:
                break
        if len(trois) < 3:
            print(f"⚪ BANC INVALIDE — {len(trois)} demi-seconde(s) bruyante(s) seulement sur le banc "
                  "décalé, il en faut 3 : rien mesuré"); return 1
        pfd_h = os.open(tempfile.mkdtemp(prefix="regarder-prive-", dir=tmp), os.O_RDONLY | os.O_DIRECTORY)
        vrai_transcrire, TRANSCRIRE = TRANSCRIRE, faux_py
        os.environ["FAUX_SEGMENTS"] = json.dumps(trois)
        try:
            _, _, a_debut, _, _ = transcrire_piste(decale, 0, pfd_h, "fr", {})
            bout = os.path.join(tmp, "horloge-bout-en-bout")
            try:
                construire(decale, "fr", 7, bout)
                code = 0
            except SystemExit as e:
                code = e.code
        finally:
            TRANSCRIRE = vrai_transcrire
            del os.environ["FAUX_SEGMENTS"]
            os.close(pfd_h)
        # Avec `-copyts`, le début de piste se lit dans l'horloge du conteneur : ≈ start_time
        # (l'AAC part 46 ms avant l'image, et c'est lui le plus tôt). Sans, il se lit 0.
        if abs(a_debut - depart) > 0.002:
            print(f"\n🔴 CASSÉ — le début de la piste audio se lit {a_debut:.4f} s, start_time vaut "
                  f"{depart:.4f} s : la sonde ne lit pas l'horloge du conteneur, et le décalage "
                  f"appliqué aux écrans ({a_debut - depart:+.3f} s) est faux.")
            return 1
        index = open(os.path.join(bout, "INDEX.md")).read() if code == 0 else ""
        lies = dict(re.findall(r"\[\d\d:\d\d\] (\w)\n  ↳ écran ~[\d:]+ · `([^`]+)`", index))
        inventees = [s["texte"] for s in trois
                     if f"INVENTÉE · [{int(s['debut']) // 60:02d}:{int(s['debut']) % 60:02d}] {s['texte']}" in index]
        if inventees:
            print(f"⚪ BANC INVALIDE — les répliques {inventees} sont tombées sur du silence : "
                  "rien mesuré"); return 1
        faux = []
        for s in trois:
            chemin = lies.get(s["texte"])
            n = couleur(os.path.join(bout, chemin)) if chemin else None
            attendu = int((s["debut"] - glissement) / 0.5)
            if n != attendu:
                faux.append(f"   réplique « {s['texte']} » à {s['debut']} s → couleur nº{n} (attendu nº{attendu})")
        if code != 0 or faux:
            print("\n".join(faux))
            print(f"\n🔴 CASSÉ — de bout en bout (code {code}), sur une vidéo dont l'horloge part à "
                  f"{depart:.2f} s, l'INDEX lie des écrans DÉCALÉS.")
            return 1
        print(f"   ✅ horloge de bout en bout : début de piste lu {a_debut:.3f} s (= start_time), "
              "les 3 répliques transcrites sont liées à la couleur qu'elles voyaient dans l'INDEX")

        # ⭐⭐ BANC À IMAGES VARIABLES (3e revue Codex, 12 sept. 2026). Quatre images seulement,
        #    aux PTS 0 · 0,90 · 1,96 · 1,99 s, comme un screen record dont l'écran ne bouge pas.
        #    Le banc se VÉRIFIE lui-même (ffprobe) avant de juger : une vidéo que ffmpeg aurait
        #    re-cadencée à 25 i/s rendrait le test vert sans avoir rien mesuré.
        vfr_dir = os.path.join(tmp, "vfr")
        os.makedirs(vfr_dir)
        couleurs = [0, 9, 18, 27]                       # nº de couleur du décodeur `couleur()`
        durees = [0.90, 1.06, 0.03, 0.01]
        # 4 aplats à 100 i/s mis bout à bout, puis `mpdecimate` jette chaque image identique à
        # la précédente : il ne reste que les 4 changements, à 0 · 0,90 · 1,96 · 1,99 s — c'est
        # exactement ce que fait l'enregistreur d'écran de macOS.
        liste_vfr = os.path.join(vfr_dir, "l.txt")
        with open(liste_vfr, "w") as f:
            for n, d in zip(couleurs, durees):
                r, g = (n % 8) * 32, (n // 8) * 32
                seg = os.path.join(vfr_dir, f"c{n}.mp4")
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                                "-i", f"color=c=0x{r:02x}{g:02x}40:size=640x360:d={d}:r=100",
                                "-pix_fmt", "yuv420p", seg], check=True)
                f.write(f"file '{seg}'\n")
        vfr = os.path.join(vfr_dir, "vfr.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", liste_vfr,
                        "-vf", "mpdecimate", "-fps_mode", "vfr", "-video_track_timescale", "1000",
                        "-pix_fmt", "yuv420p", vfr], check=True)
        pts, _, _ = instants(vfr)
        if len(pts) != 4 or any(abs(a - b) > 0.002 for a, b in zip(pts, [0.0, 0.90, 1.96, 1.99])):
            print(f"⚪ BANC INVALIDE — la vidéo à images variables porte les PTS {pts}, attendu "
                  "0 · 0,90 · 1,96 · 1,99 : rien mesuré"); return 1
        # 1,00 s tombe dans le trou de 0,90 → 1,96 : l'écran est celui de 0,90 s. 1,97 s → celui
        # de 1,96. 2,30 s dépasse la durée (2,0 s) : le DERNIER écran, jamais rien, jamais avant.
        places_vfr = [{"debut": 1.0, "fin": 1.5, "texte": "a"}, {"debut": 1.97, "fin": 2.0, "texte": "b"},
                      {"debut": 2.3, "fin": 2.5, "texte": "c"}]
        attendus_vfr = [9, 18, 27]
        _, rattache = ecrans(vfr, places_vfr, set(), 2.0, 1, tenir(vfr_dir), os.path.join(vfr_dir, "places"))
        faux = []
        for i, s in enumerate(places_vfr):
            t_img, chemin = rattache.get(i, (None, None, None))[:2]
            n = couleur(chemin) if chemin else None
            if n != attendus_vfr[i]:
                faux.append(f"   réplique à {s['debut']} s → couleur nº{n} (attendu nº{attendus_vfr[i]}, "
                            f"l'image affichée à cet instant)")
        if faux:
            print("\n".join(faux))
            print("\n🔴 CASSÉ — sur une vidéo à images VARIABLES (tout screen record macOS), la "
                  "réplique reçoit l'écran d'APRÈS le prochain changement, pas celui qu'elle voyait.")
            return 1
        print("   ✅ images variables (PTS 0 · 0,90 · 1,96 · 1,99) : 1,00 s → l'écran de 0,90 · "
              "1,97 s → 1,96 · 2,30 s (hors durée) → le dernier")

        # ⭐⭐ TROIS BANCS DE PLUS (5e revue Codex, 12 sept. 2026), un par trou mesuré.
        # (a) LES HORODATAGES MENTENT de 0,3 s : `rendre` relit chaque image décodée contre le
        #     PTS attendu et exige d'être parti d'une image-clé CONNUE. Rien ne concorde →
        #     aucune image rendue, et surtout aucune image DEVINÉE. Un contrôle qui ne relisait
        #     que l'image finale — ou rien — laissait passer n'importe quel décalage.
        #     ⛔ DEUX MENTEURS, PAS UN (6e passe, 12 sept. 2026) : tout décalé de 0,3 s, c'est la
        #     PREMIÈRE image décodée qui trahit (elle n'est plus à un PTS d'image-clé connu), et
        #     la relecture image par image n'est jamais sollicitée — mesuré : retirer cette
        #     relecture laissait ce banc VERT. Le 2e menteur garde les images-clés justes et
        #     décale les autres de 20 ms : seule la relecture de CHAQUE image peut le voir.
        vrai_instants = instants
        menteurs = [("faux de 0,3 s", lambda p, d, c: ([x + 0.3 for x in p], d, c)),
                    ("clés justes, les autres faux de 20 ms",
                     lambda p, d, c: ([x if i in set(c) else x + 0.02 for i, x in enumerate(p)], d, c))]
        for nom_m, mentir in menteurs:
            instants = lambda v, mentir=mentir: mentir(*vrai_instants(v))
            menteur = os.path.join(tmp, "menteur-" + str(len(nom_m)))
            os.makedirs(os.path.join(menteur, "ecrans"))
            mfd = tenir(menteur)
            try:
                imgs = frames(video, [1.7], [], mfd, os.path.join(menteur, "ecrans"))
            finally:
                instants = vrai_instants
                os.close(mfd)
            if imgs or os.listdir(os.path.join(menteur, "ecrans")):
                print(f"   🔴 horodatages {nom_m} → {len(imgs)} image rendue quand même")
                print("\n🔴 CASSÉ — une image dont l'horodatage relu ne correspond pas au PTS "
                      "attendu est acceptée."); return 1
            print(f"   ✅ horodatages {nom_m} → aucune image rendue, aucune devinée")

        # (b) DEUX PISTES VIDÉO, la 2e PLUS GRANDE ET MARQUÉE `default` : sans `-map 0:v:0`,
        #     ffmpeg rendrait une mire à la place de l'écran, avec des horodatages lus sur
        #     `v:0`. ⚠️ MESURÉ sur ffmpeg 9 (6e passe, 12 sept. 2026) : sans `-map`, il ne
        #     choisit PAS la plus haute résolution, il choisit la piste `default` — et un mp4
        #     muxé par ffmpeg marque `v:0` par défaut. Le banc précédent (mire plus grande,
        #     sans disposition) laissait donc `-map` retiré VERT. La mire porte le `default`.
        deux = os.path.join(tmp, "deux.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-f", "lavfi",
                        "-i", "testsrc=size=1280x720:rate=5", "-map", "0:v", "-map", "1:v",
                        "-map", "0:a", "-c:v:0", "copy", "-c:v:1", "libx264", "-preset",
                        "ultrafast", "-pix_fmt:v:1", "yuv420p", "-c:a", "copy",
                        "-disposition:v:0", "0", "-disposition:v:1", "default", "-t", "20", deux],
                       check=True)
        larg = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                               "stream=width:stream_disposition=default", "-of", "csv=p=0", deux],
                              capture_output=True, text=True).stdout.split()
        if [l.strip(",") for l in larg] != ["640,0", "1280,1"]:
            print(f"⚪ BANC INVALIDE — `deux.mp4` porte {larg}, attendu 640 (pas default) puis "
                  "1280 (default) : rien mesuré"); return 1
        dfd = tenir(tmp)
        _, rattache = ecrans(deux, places, set(), 20.0, 7, dfd, os.path.join(tmp, "places-deux"))
        os.close(dfd)
        faux = []
        for i, s in enumerate(places):
            t_img, chemin = rattache.get(i, (None, None, None))[:2]
            n = couleur(chemin) if chemin else None
            if n != int(s["debut"] / 0.5):
                faux.append(f"   réplique à {s['debut']} s → couleur nº{n} (attendu nº{int(s['debut'] / 0.5)})")
        if faux:
            print("\n".join(faux))
            print("\n🔴 CASSÉ — avec deux pistes vidéo, l'écran rendu n'est pas celui de la "
                  "première piste (celle dont on lit les horodatages)."); return 1
        print(f"   ✅ deux pistes vidéo (la 2e plus grande) → les {len(places)} écrans viennent de la 1re")

        # (c) LE SON PART 0,7 s APRÈS L'IMAGE (le banc de Codex, `-itsoffset 0.7`). Le WAV
        #     commence à la première image AUDIO, donc « 1,5 s » pour Whisper = 2,2 s à
        #     l'écran : la demi-seconde nº 4, pas la nº 3. Le transcripteur est REMPLACÉ par un
        #     faux qui rend une réplique placée à 1,5 s (horloge du WAV) — et qui PROUVE au
        #     passage qu'il reçoit un nom RELATIF résolu dans le dossier privé.
        offset = os.path.join(tmp, "offset.mov")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-itsoffset", "0.7",
                        "-i", long_aiff, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "pcm_s16le", "-t", "20", offset], check=True)
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", offset,
                            "-map", "0:a:0", "-vn", "-af", "ashowinfo", "-frames:a", "1",
                            "-f", "null", "-"], capture_output=True)
        m = re.search(rb"pts_time:\s*(-?[0-9.]+)", r.stderr)
        a_debut = float(m.group(1)) if m else None
        _, _, depart_off = ffprobe(offset)
        o_off = onset(offset)
        if a_debut is None or abs(a_debut - 0.7) > 0.05 or abs(depart_off) > 0.05:
            print(f"⚪ BANC INVALIDE — `offset.mov` : son à {a_debut} s, start_time {depart_off} "
                  "(attendu 0,7 et 0) : le décalage n'est pas reproduit, rien mesuré"); return 1
        if o_off is None or abs(o_off - o_banc) > 0.01:
            print(f"🔴 PRÉMISSE FAUSSE — la voix attaque à {o_off} s dans le WAV du banc décalé contre "
                  f"{o_banc} s sur l'original : le WAV n'est plus à l'horloge de la première image "
                  "audio, le recalage ci-dessous serait faux"); return 1
        faux_py = os.path.join(tmp, "faux-transcripteur.py")
        open(faux_py, "w").write(
            "import json, os, sys\n"
            "audio, sortie = sys.argv[1], sys.argv[2]\n"
            "assert not os.path.isabs(audio) and os.path.isfile(audio), audio\n"
            "detail = sys.argv[sys.argv.index('--detail-json') + 1]\n"
            "open(sortie, 'w').write('phrase placee\\n')\n"
            "json.dump([{'debut': 1.5, 'fin': 2.4, 'texte': 'phrase placee'}], open(detail, 'w'))\n"
            "sys.exit(int(os.environ.get('FAUX_PLANTE', '0')))\n")
        vrai_transcrire = TRANSCRIRE
        TRANSCRIRE = faux_py
        base_off = os.path.join(tmp, "regard-offset")
        try:
            index_off = open(construire(offset, "fr", 2, base_off), errors="ignore").read()
        finally:
            TRANSCRIRE = vrai_transcrire
        m = re.search(r"\[(\d+):(\d+)\] phrase placee\n  ↳ écran ~\d+:\d+ · `([^`]+)`", index_off)
        n = couleur(m.group(3)) if m else None
        if not m or int(m.group(1)) * 60 + int(m.group(2)) != 2 or n != 4:
            print(f"   🔴 son décalé de 0,7 s : l'INDEX porte "
                  + (f"[{m.group(1)}:{m.group(2)}] et l'écran couleur nº{n}" if m else "PAS la réplique")
                  + " (attendu [00:02], couleur nº4)")
            print("\n🔴 CASSÉ — une réplique est horodatée dans l'horloge du WAV, pas dans celle de "
                  "l'écran : quand le son part après l'image, elle reçoit l'écran d'AVANT."); return 1
        print("   ✅ son décalé de 0,7 s → « 1,5 s » du WAV devient [00:02] à l'écran, demi-seconde nº4")

        base = os.path.join(tmp, "regard")
        index = construire(video, "fr", 8, base)

        # ⭐ ON VÉRIFIE CE QUE L'INDEX ANNONCE, pas ce que le code calcule de son côté.
        #    Revue Codex du 11 sept. 2026 : l'extraction était juste à 0,09 s près, et
        #    l'INDEX écrivait quand même « [00:16] » pour l'image de 17,0 s — `int()`
        #    tronquait. Une phase qui recalcule l'horodatage elle-même n'aurait jamais vu
        #    l'erreur : elle aurait mesuré le même calcul deux fois.
        annonces = re.findall(r"`\[(\d+):(\d+)\]` `([^`]+)`", open(index).read())
        if not annonces:
            print("🔴 CASSÉ — l'INDEX n'annonce aucun écran"); return 1
        pire, detail = 0.0, []
        for mm, ss, chemin in annonces:
            t = int(mm) * 60 + int(ss)
            n = couleur(chemin)
            if n is None:
                continue
            debut, fin = n * 0.5, n * 0.5 + 0.5          # ce que l'image MONTRE
            ecart = 0.0 if debut < t + 1 and fin > t else (t - fin if t >= fin else t - debut)
            pire = max(pire, abs(ecart))
            detail.append(f"   INDEX dit [{mm}:{ss}] → l'image dit {debut:>4.1f}s  {ecart:+.2f}s")
        print("\n".join(detail))
        if pire >= 0.5:
            print(f"\n🔴 CASSÉ — dérive de {pire:.2f} s entre ce que l'INDEX ANNONCE et ce "
                  "que l'image MONTRE : l'écran attaché à une réplique n'est PAS le bon, "
                  "et rien d'autre ne le signalerait.")
            return 1
        print(f"\n✅ ALIGNEMENT EXACT — dérive max {pire:.2f} s sur {len(annonces)} écrans")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def autotest_refus():
    """LES REFUS FONT-ILS ENCORE LEUR TRAVAIL ?

    ⛔ LE TROU NOMMÉ PAR LA REVUE CODEX DU 11 SEPT. 2026. L'autotest vérifiait que l'outil
      RÉUSSIT, jamais qu'il REFUSE. Mesuré : en désarmant le refus de piste muette, les
      deux phases restaient VERTES et l'outil rendait « Sous-titrage ST' 501 » sur du
      silence pur, code 0. **Un garde qu'aucun test n'exerce se retire sans bruit.**

    ⭐ 4e cas (revue « repli Claude ») : une vidéo SAINE, mais `--sortie` sur un dossier
      qui contient un fichier de JNT et pas de marqueur → code 2, fichier intact.
    ⭐⭐ DEPUIS LA 3e REVUE CODEX (12 sept. 2026), UN REFUS SE JUGE À L'EMPREINTE, PAS AU NOM :
      chaque fichier du dossier (et le témoin extérieur) est haché AVANT et APRÈS. Un mutant
      qui réécrivait `JNT` → `ECRASE` dans les notes avant de refuser passait : les noms
      existaient toujours. Et le dossier « à moi » se relance DEUX fois : un mutant qui
      n'inscrivait plus ses écrans rendait code 0 la première fois, code 2 la seconde.
    """
    global SONDE
    tmp = tempfile.mkdtemp(prefix="regarder-refus-")
    moi = os.path.abspath(__file__)

    def empreinte(dossier, *extras):
        """{chemin relatif: sha256} de tout ce que contient `dossier` (liens NON suivis : un
        lien compte pour sa cible textuelle), plus les fichiers `extras` par chemin absolu."""
        e = {}
        for racine, dirs, fichiers in os.walk(dossier):
            for nom in fichiers + [d for d in dirs if os.path.islink(os.path.join(racine, d))]:
                chemin = os.path.join(racine, nom)
                rel = os.path.relpath(chemin, dossier)
                if os.path.islink(chemin):
                    e[rel] = "lien→" + os.readlink(chemin)
                else:
                    e[rel] = hashlib.sha256(open(chemin, "rb").read()).hexdigest()
        for x in extras:
            e[x] = hashlib.sha256(open(x, "rb").read()).hexdigest() if os.path.isfile(x) else "ABSENT"
        return e

    def ident(chemin):
        """`dev:inode` de `chemin`, tel que `noter` l'inscrit (0:0 s'il n'existe pas)."""
        try:
            st = os.stat(chemin)
        except OSError:
            return "0:0"
        return f"{st.st_dev}:{st.st_ino}"

    def _registre(dossier, rels, brutes=()):
        """Écrit un registre SIGNÉ dans `dossier` : une ligne `<sha256> <dev>:<inode> <rel>` par
        nom de `rels` (empreinte et identité du fichier s'il existe, sinon celles du vide et
        `0:0`), puis les lignes `brutes` telles quelles (pour les registres altérés)."""
        lignes = [ENTETE]
        for rel in rels:
            p = os.path.join(dossier, rel)
            octets = open(p, "rb").read() if os.path.isfile(p) else b""
            lignes.append(f"{hashlib.sha256(octets).hexdigest()} {ident(p)} {rel}")
        lignes += list(brutes)
        open(os.path.join(dossier, MARQUEUR), "w").write("\n".join(lignes) + "\n")

    def sha(chemin):
        return hashlib.sha256(open(chemin, "rb").read()).hexdigest()

    try:
        v_sans_audio = os.path.join(tmp, "sans-audio.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=320x180:rate=10", "-t", "2",
                        "-pix_fmt", "yuv420p", v_sans_audio], check=True)
        v_muet = os.path.join(tmp, "micro-ferme.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=320x180:rate=10", "-f", "lavfi",
                        "-i", "anullsrc=r=16000:cl=mono", "-t", "2",
                        "-pix_fmt", "yuv420p", v_muet], check=True)
        v_sans_video = os.path.join(tmp, "audio-seul.m4a")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "sine=frequency=440:r=16000", "-t", "2",
                        "-c:a", "aac", v_sans_video], check=True)
        v_sain = os.path.join(tmp, "sain.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=320x180:rate=10", "-f", "lavfi",
                        "-i", "sine=frequency=440:r=16000", "-t", "2",
                        "-pix_fmt", "yuv420p", v_sain], check=True)
        # ⭐ 5e cas (revue Codex, 12 sept.) : un dossier SANS marqueur dont l'INDEX.md commence
        #    par « # REGARD — » → pas à moi, code 2, INDEX intact. (Depuis la 2e revue, cet
        #    INDEX ne vaut plus signature NULLE PART, même sous mon cache.)
        emprunte = os.path.join(tmp, "garde-emprunte")
        os.makedirs(emprunte, exist_ok=True)
        open(os.path.join(emprunte, "INDEX.md"), "w").write("# REGARD — écrit par JNT\n")
        # ⭐⭐ 6e cas (2e revue Codex, 12 sept.) : un dossier À MOI (marqueur) où JNT a posé
        #    SON `transcript.txt` — un fichier qui porte MON nom sans être à mon registre.
        #    Avant : effacé par nom, code 0. Maintenant : code 2, et son texte survit.
        homonyme = os.path.join(tmp, "garde-homonyme")
        os.makedirs(homonyme, exist_ok=True)
        open(os.path.join(homonyme, "INDEX.md"), "w").write("# REGARD — ancien\n")
        _registre(homonyme, ["INDEX.md"])
        perso = os.path.join(homonyme, "transcript.txt")
        open(perso, "w").write("MES notes de transcription, pas les siennes\n")
        # ⭐⭐ 7e cas (2e revue) : dans un dossier À MOI, `ecrans` est un LIEN vers un dossier
        #    de JNT qui contient `ecran-001.jpg`. Avant : l'outil suivait le lien et
        #    REMPLAÇAIT l'image de JNT, code 0. Maintenant : code 2, image intacte.
        lien = os.path.join(tmp, "garde-lien")
        os.makedirs(lien, exist_ok=True)
        externe = os.path.join(tmp, "photos-de-jnt")
        os.makedirs(externe, exist_ok=True)
        photo = os.path.join(externe, "ecran-001.jpg")
        open(photo, "wb").write(b"\xff\xd8 photo de JNT")
        os.symlink(externe, os.path.join(lien, "ecrans"))
        _registre(lien, ["ecrans/ecran-001.jpg"])       # l'empreinte est celle de SA photo
        # ⭐⭐ 8e cas (3e revue Codex, 12 sept.) : un dossier À MOI dont le registre porte une
        #    ligne `../…` vers un fichier de JNT, HORS du dossier. Avant : effacé, code 0.
        #    Maintenant : registre reconnu ALTÉRÉ, code 2, rien touché — ni dedans ni dehors.
        altere = os.path.join(tmp, "garde-altere")
        os.makedirs(altere, exist_ok=True)
        dehors = os.path.join(tmp, "important-de-jnt.md")
        open(dehors, "w").write("un fichier de JNT, HORS du dossier de sortie\n")
        open(os.path.join(altere, "INDEX.md"), "w").write("# REGARD — ancien\n")
        #    ⚠️ v11c : l'identité inscrite est la VRAIE (`ident(dehors)`), sinon c'est l'étape 3
        #    (autre inode → « COPIE ») qui refuse à la place du confinement, et un mutant qui
        #    accepte `..` restait vert (mesuré : suite de mutations v11, 2 mutants aveugles).
        _registre(altere, ["INDEX.md"], [f"{sha(dehors)} {ident(dehors)} ../important-de-jnt.md"])
        # ⭐ 8e cas bis (4e revue) : la ligne ABSOLUE seule — un mutant qui ne filtre que `..`
        #    la laissait passer, et les deux étaient dans le même cas, donc indiscernables.
        absolu = os.path.join(tmp, "garde-absolu")
        os.makedirs(absolu, exist_ok=True)
        open(os.path.join(absolu, "INDEX.md"), "w").write("# REGARD — ancien\n")
        _registre(absolu, ["INDEX.md"], [f"{sha(dehors)} {ident(dehors)} {dehors}"])
        # ⭐⭐ 10e cas (4e revue Codex, 12 sept.) : un nom INSCRIT à mon registre (`audio-1.wav`)
        #    est un LIEN vers un document de JNT. Avant : « sauté » en silence, et le run
        #    continuait ; un `os.remove` par chemin l'aurait suivi. Maintenant : registre reconnu
        #    ALTÉRÉ, code 2 avant la première suppression, document intact.
        lien_inscrit = os.path.join(tmp, "garde-lien-inscrit")
        os.makedirs(lien_inscrit, exist_ok=True)
        doc = os.path.join(tmp, "document-de-jnt.txt")
        open(doc, "w").write("un document de JNT que le lien vise\n")
        open(os.path.join(lien_inscrit, "INDEX.md"), "w").write("# REGARD — ancien\n")
        os.symlink(doc, os.path.join(lien_inscrit, "audio-1.wav"))
        _registre(lien_inscrit, ["INDEX.md", "audio-1.wav"])   # empreinte = celle du document visé
        # ⭐⭐ 14e cas (5e revue Codex, 12 sept.) : un `.regarder` SANS ma signature — JNT a nommé
        #    un fichier comme ça. Avant : l'existence du fichier valait preuve, et son INDEX.md
        #    partait. Maintenant : pas la phrase exacte en tête → pas à moi, code 2.
        sans_signature = os.path.join(tmp, "garde-sans-signature")
        os.makedirs(sans_signature, exist_ok=True)
        open(os.path.join(sans_signature, MARQUEUR), "w").write("notes de JNT\nINDEX.md\n")
        open(os.path.join(sans_signature, "INDEX.md"), "w").write("# REGARD — écrit par JNT\n")
        # ⭐⭐ 15e cas (5e revue Codex) : `--sortie` EST un lien vers un dossier de JNT. Un
        #    `islink()` le voyait — mais par chemin, avant un `tenir()` par chemin. Maintenant
        #    c'est `O_NOFOLLOW` qui tranche, dans le seul `open` du dossier.
        #    ⚠️ La cible porte un registre SIGNÉ (JNT a lié un ancien run) : sans ça, un `tenir`
        #    qui SUIT le lien refuse quand même (« pas à moi ») et le mutant restait vert — vu
        #    par la suite de mutations v8. Ici, suivre le lien effacerait l'INDEX de la cible.
        cible_jnt = os.path.join(tmp, "dossier-de-jnt-vise")
        os.makedirs(cible_jnt)
        open(os.path.join(cible_jnt, "INDEX.md"), "w").write("L'INDEX de JNT\n")
        _registre(cible_jnt, ["INDEX.md"])
        lien_sortie = os.path.join(tmp, "garde-lien-sortie")
        os.symlink(cible_jnt, lien_sortie)
        cas = [("aucune piste audio", v_sans_audio, 3),
               ("piste audio MUETTE", v_muet, 4),
               ("aucune piste vidéo", v_sans_video, 6),
               ("dossier pas à moi", v_sain, 2),
               ("INDEX emprunté, sans marqueur", v_sain, 2),
               ("MON nom, PAS mon registre", v_sain, 2),
               ("`ecrans` = lien vers JNT", v_sain, 2),
               ("registre ALTÉRÉ (`../`)", v_sain, 2),
               ("registre ALTÉRÉ (absolu)", v_sain, 2),
               ("nom INSCRIT = lien vers JNT", v_sain, 2),
               ("marqueur SANS signature", v_sain, 2),
               ("`--sortie` = lien vers JNT", v_sain, 2)]
        # ⭐ Le témoin prouve l'AUTRE moitié du refus : rien ne doit être effacé quand on
        #    dit non. Un refus qui a déjà écrasé le dossier n'est pas un refus.
        ok = True
        for nom, chemin, attendu in cas:
            garde = {"INDEX emprunté, sans marqueur": emprunte, "MON nom, PAS mon registre": homonyme,
                     "`ecrans` = lien vers JNT": lien, "registre ALTÉRÉ (`../`)": altere,
                     "registre ALTÉRÉ (absolu)": absolu, "nom INSCRIT = lien vers JNT": lien_inscrit,
                     "marqueur SANS signature": sans_signature, "`--sortie` = lien vers JNT": lien_sortie,
                     }.get(nom, os.path.join(tmp, f"garde-{attendu}"))
            os.makedirs(garde, exist_ok=True)
            temoin = os.path.join(garde, "mes-notes.md")
            open(temoin, "w").write("fichier de JNT")
            if garde == homonyme:
                temoin = perso
            elif garde == lien:
                temoin = photo
            elif garde in (altere, absolu):
                temoin = dehors
            elif garde == lien_inscrit:
                temoin = doc
            avant = empreinte(garde, temoin)
            r = subprocess.run([sys.executable, moi, chemin, "--sortie", garde],
                               capture_output=True, text=True)
            apres = empreinte(garde, temoin)
            # ⛔ Un refus qui a DÉJÀ écrit (marqueur, INDEX) n'est pas un refus : le mutant
            #    « marqueur avant le refus de piste muette » laissait `.regarder` dans un
            #    dossier de JNT sur un code 4, et l'autotest restait vert (2e revue Codex).
            #    Et un refus qui a déjà EFFACÉ ou RÉÉCRIT n'en est pas un non plus : l'empreinte
            #    du dossier entier doit être IDENTIQUE avant et après (3e revue Codex).
            ecrits = sorted(set(apres) - set(avant))
            effaces = sorted(set(avant) - set(apres))
            modifies = sorted(k for k in avant if k in apres and avant[k] != apres[k])
            bon = (r.returncode == attendu) and not ecrits and not effaces and not modifies
            ok = ok and bon
            print(f"   {'✅' if bon else '🔴'} {nom:<29} code {r.returncode} (attendu {attendu})"
                  + (f" · ⛔ ÉCRIT AVANT DE REFUSER : {ecrits}" if ecrits else "")
                  + (f" · ⛔ EFFACÉ : {effaces}" if effaces else "")
                  + (f" · ⛔ RÉÉCRIT : {modifies}" if modifies else "")
                  + (f" · {len(avant)} empreinte(s) identiques, rien touché" if bon else ""))
        if not ok:
            print("\n🔴 CASSÉ — un refus ne refuse plus, ou il écrase avant de refuser.")
            return 1
        # ⭐ Les DEUX gardes de la signature, chacun SEUL (suite de mutations v8, 12 sept.) :
        #    par le CLI, `a_moi` refuse avant que `nettoyer` ne lise le registre, et `nettoyer`
        #    refuserait si `a_moi` laissait passer — un mutant sur l'un des deux restait donc
        #    vert. Un garde jamais vu bloquer ne garde rien : on les appelle en direct.
        sfd = tenir(sans_signature)
        try:
            refuse_a_moi = not a_moi(sfd)
            try:
                nettoyer(sans_signature, sfd)
                code = 0
            except SystemExit as e:
                code = e.code
        finally:
            os.close(sfd)
        index_la = os.path.isfile(os.path.join(sans_signature, "INDEX.md"))
        # ⭐ v9 (suite de mutations) : « notes de JNT » en première ligne est aussi une ligne
        #    HORS FORMAT — le garde des lignes refusait à la place du garde de la signature, et
        #    un `nettoyer` qui ne lit plus l'en-tête restait vert. Deuxième registre : DÉCAPITÉ,
        #    c'est-à-dire des lignes `<sha256> <nom>` parfaitement formées et à jour, sans la
        #    première ligne (un `tail -n +2`, une copie qui a perdu sa 1re ligne). Seul l'en-tête
        #    peut le refuser. ⚠️ DEUX lignes, et la première nomme un fichier ABSENT : `nettoyer`
        #    lit les inscrits à partir de `lignes[1:]`, donc un mutant qui saute l'en-tête saute
        #    aussi la 1re ligne — avec une seule ligne, l'INDEX devenait un « reste non inscrit »
        #    et le garde des restes refusait à la place de la signature (mesuré : mutant vert).
        decapite = os.path.join(tmp, "garde-registre-decapite")
        os.makedirs(decapite, exist_ok=True)
        open(os.path.join(decapite, "INDEX.md"), "w").write("# REGARD — copié par JNT\n")
        #    ⚠️ v11c : lignes au format v11, avec l'identité RÉELLE de l'INDEX — au format v10
        #    (deux champs) c'est le garde des lignes qui refusait, et le mutant restait vert.
        open(os.path.join(decapite, MARQUEUR), "w").write(
            f"{hashlib.sha256(b'').hexdigest()} 0:0 transcript.txt\n"
            f"{sha(os.path.join(decapite, 'INDEX.md'))} {ident(os.path.join(decapite, 'INDEX.md'))} INDEX.md\n")
        dfd_ = tenir(decapite)
        try:
            refuse_decapite = not a_moi(dfd_)
            try:
                nettoyer(decapite, dfd_)
                code_decapite = 0
            except SystemExit as e:
                code_decapite = e.code
        finally:
            os.close(dfd_)
        decapite_la = os.path.isfile(os.path.join(decapite, "INDEX.md"))
        bon = (refuse_a_moi and code == 2 and index_la
               and refuse_decapite and code_decapite == 2 and decapite_la)
        print(f"   {'✅' if bon else '🔴'} {'signature : a_moi + nettoyer, seuls':<29} "
              f"a_moi {'refuse' if refuse_a_moi else 'ACCEPTE'} · nettoyer code {code} · "
              f"INDEX de JNT {'intact' if index_la else 'EFFACÉ'} · registre DÉCAPITÉ (lignes "
              f"valides, sans en-tête) : a_moi {'refuse' if refuse_decapite else 'ACCEPTE'} · "
              f"nettoyer code {code_decapite} · INDEX {'intact' if decapite_la else 'EFFACÉ'}")
        if not bon:
            print("\n🔴 CASSÉ — un registre sans ma signature passe pour le mien.")
            return 1
        # ⭐ `a_moi` SEUL sur une signature PROLONGÉE (suite de mutations v8d) : un `startswith`
        #    acceptait `ENTETE + " (copie de JNT)"`. La phrase est exacte ou n'est pas la mienne.
        prolonge = os.path.join(tmp, "garde-signature-prolongee")
        os.makedirs(prolonge)
        open(os.path.join(prolonge, MARQUEUR), "w").write(ENTETE + " (copie de JNT)\n")
        xfd = tenir(prolonge)
        try:
            bon = not a_moi(xfd)
        finally:
            os.close(xfd)
        print(f"   {'✅' if bon else '🔴'} {'signature prolongée : a_moi seul':<29} "
              f"{'refuse' if bon else 'ACCEPTE'}")
        if not bon:
            print("\n🔴 CASSÉ — une signature suivie d'autre chose passe pour la mienne.")
            return 1
        # ⭐ `rendre` SEUL devant une 1re image décodée qui N'EST PAS une clé (`iskey:0`) — suite
        #    de mutations v8d : la garde `not cle0` retirée restait verte, parce qu'aucun banc
        #    ne fait décoder ffmpeg depuis une non-clé. On lui présente donc un faux `showinfo`.
        vrai_run = subprocess.run

        def faux_ffmpeg(cle):
            def run(args, *a, **kw):
                stderr = (b"[Parsed_showinfo_0 @ 0x1] n:   0 pts:      0 pts_time:0       "
                          b"duration:1 duration_time:0.1 fmt:yuv420p cl:left sar:1/1 s:160x90 "
                          b"i:P iskey:" + str(cle).encode() + b" type:I checksum:0 plane_checksum:[0]\n")
                return subprocess.CompletedProcess(args, 0, stdout=b"\xff\xd8x", stderr=stderr)
            return run
        try:
            subprocess.run = faux_ffmpeg(0)
            sans_cle, motif = rendre(v_sain, [0.0, 0.1], 0.0, [0], 0)
            subprocess.run = faux_ffmpeg(1)
            avec_cle, _ = rendre(v_sain, [0.0, 0.1], 0.0, [0], 0)
        finally:
            subprocess.run = vrai_run
        bon = sans_cle is None and avec_cle == b"\xff\xd8x"
        print(f"   {'✅' if bon else '🔴'} {'rendre : 1re image décodée PAS une clé':<29} "
              f"{'refusée' if sans_cle is None else 'ACCEPTÉE'} · contrôle iskey:1 "
              f"{'rendu' if avec_cle else 'PAS RENDU'}")
        if not bon:
            print("\n🔴 CASSÉ — `rendre` compte depuis une image qui n'est pas une clé.")
            return 1
        # ⭐⭐ 9e cas (3e revue Codex, 12 sept.) : `ecrans` est REMPLACÉ PAR UN LIEN vers un dossier
        #    de JNT PENDANT l'extraction — après le contrôle, avant la première image. Le rappel
        #    `inscrire` tourne exactement à cet instant-là : il fait la substitution, sans course.
        #    Attendu : les images tombent dans le VRAI dossier (tenu par descripteur), le dossier
        #    de JNT ne reçoit rien. Avant : sa photo était écrasée, code 0.
        piege = os.path.join(tmp, "piege-ecrans")
        os.makedirs(piege)
        photos = os.path.join(tmp, "photos-de-jnt-2")
        os.makedirs(photos)
        open(os.path.join(photos, "ecran-001.jpg"), "wb").write(b"\xff\xd8 photo de JNT")
        avant = empreinte(photos)

        ecrans_piege = os.path.join(piege, "ecrans")

        def substituer(_chemin, _donnees, _st=None):
            if not os.path.islink(ecrans_piege):
                os.rename(ecrans_piege, ecrans_piege + ".vrai")
                os.symlink(photos, ecrans_piege)
        pfd = tenir(piege)
        imgs = frames(v_sain, [0.5], [], pfd, ecrans_piege, substituer)
        os.close(pfd)
        chez_jnt = empreinte(photos) != avant
        chez_moi = os.path.isfile(os.path.join(ecrans_piege + ".vrai", "ecran-001.jpg"))
        bon = bool(imgs) and not chez_jnt and chez_moi
        print(f"   {'✅' if bon else '🔴'} {'`ecrans` → lien PENDANT l’extraction':<29} "
              f"{len(imgs)} image · dossier de JNT {'TOUCHÉ' if chez_jnt else 'intact'} · "
              f"image écrite {'dans le vrai dossier' if chez_moi else 'AILLEURS'}")
        if not bon:
            print("\n🔴 CASSÉ — une substitution de `ecrans` pendant l'extraction fait écrire chez JNT.")
            return 1

        # ⭐⭐ 11e cas (4e revue Codex, 12 sept.) : la MÊME substitution, mais PENDANT LE NETTOYAGE —
        #    après tous les contrôles, juste avant la première suppression (sonde
        #    « avant-suppression »). Avant : `os.remove(base/ecrans/ecran-001.jpg)` suivait le lien
        #    et effaçait la photo de JNT. Maintenant : `unlink` par descripteur du VRAI dossier.
        course = os.path.join(tmp, "course-nettoyage")
        os.makedirs(os.path.join(course, "ecrans"))
        open(os.path.join(course, "ecrans", "ecran-001.jpg"), "wb").write(b"\xff\xd8 mienne")
        _registre(course, ["ecrans/ecran-001.jpg"])
        photos3 = os.path.join(tmp, "photos-de-jnt-3")
        os.makedirs(photos3)
        open(os.path.join(photos3, "ecran-001.jpg"), "wb").write(b"\xff\xd8 photo de JNT 3")
        avant = empreinte(photos3)

        def swap(etape, *_):
            if etape == "avant-suppression":
                os.rename(os.path.join(course, "ecrans"), os.path.join(course, "ecrans.vrai"))
                os.symlink(photos3, os.path.join(course, "ecrans"))
        SONDE = swap
        cfd = tenir(course)
        try:
            nettoyer(course, cfd)
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            SONDE = None
            os.close(cfd)
        chez_jnt = empreinte(photos3) != avant
        mienne_partie = not os.path.exists(os.path.join(course, "ecrans.vrai", "ecran-001.jpg"))
        bon = code == 0 and not chez_jnt and mienne_partie
        print(f"   {'✅' if bon else '🔴'} {'`ecrans` → lien PENDANT le nettoyage':<29} code {code} · "
              f"photo de JNT {'EFFACÉE' if chez_jnt else 'intacte'} · "
              f"la mienne {'effacée (vrai dossier)' if mienne_partie else 'TOUJOURS LÀ'}")
        if not bon:
            print("\n🔴 CASSÉ — une substitution de `ecrans` pendant le nettoyage efface chez JNT.")
            return 1

        # ⭐⭐ 12e cas (4e revue) : un LIEN posé à MON nom (`ecrans/ecran-001.jpg` → photo de JNT)
        #    juste après l'ouverture de `ecrans`, avant ffmpeg (sonde « ecrans-ouvert »). Écrire
        #    « à travers » remplacerait la photo. Attendu : refus code 2, photo intacte.
        plante = os.path.join(tmp, "lien-a-mon-nom")
        os.makedirs(plante)
        photo4 = os.path.join(tmp, "photo-de-jnt-4.jpg")
        open(photo4, "wb").write(b"\xff\xd8 photo de JNT 4")
        avant = hashlib.sha256(open(photo4, "rb").read()).hexdigest()

        def planter(etape, *_):
            if etape == "ecrans-ouvert":
                os.symlink(photo4, os.path.join(plante, "ecrans", "ecran-001.jpg"))
        SONDE = planter
        pfd = tenir(plante)
        try:
            frames(v_sain, [0.5], [], pfd, os.path.join(plante, "ecrans"))
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            SONDE = None
            os.close(pfd)
        intacte = hashlib.sha256(open(photo4, "rb").read()).hexdigest() == avant
        bon = code == 2 and intacte
        print(f"   {'✅' if bon else '🔴'} {'lien à MON nom pendant l’extraction':<29} code {code} "
              f"(attendu 2) · photo de JNT {'intacte' if intacte else 'ÉCRASÉE'}")
        if not bon:
            print("\n🔴 CASSÉ — un lien posé à mon nom pendant l'extraction fait écrire chez JNT.")
            return 1

        # ⭐ 12e cas bis : `ecrans` remplacé par un lien entre sa CRÉATION et son OUVERTURE
        #    (sonde « ecrans-cree ») — c'est le `O_NOFOLLOW` de l'ouverture qui doit mordre.
        #    Attendu : code 2, dossier de JNT intact.
        entre = os.path.join(tmp, "entre-creation-et-ouverture")
        os.makedirs(entre)
        photos5 = os.path.join(tmp, "photos-de-jnt-5")
        os.makedirs(photos5)
        open(os.path.join(photos5, "ecran-001.jpg"), "wb").write(b"\xff\xd8 photo de JNT 5")
        avant = empreinte(photos5)

        def remplacer(etape, *_):
            if etape == "ecrans-cree":
                os.rmdir(os.path.join(entre, "ecrans"))
                os.symlink(photos5, os.path.join(entre, "ecrans"))
        SONDE = remplacer
        efd_ = tenir(entre)
        try:
            frames(v_sain, [0.5], [], efd_, os.path.join(entre, "ecrans"))
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            SONDE = None
            os.close(efd_)
        intact = empreinte(photos5) == avant
        bon = code == 2 and intact
        print(f"   {'✅' if bon else '🔴'} {'`ecrans` → lien AVANT son ouverture':<29} code {code} "
              f"(attendu 2) · dossier de JNT {'intact' if intact else 'TOUCHÉ'}")
        if not bon:
            print("\n🔴 CASSÉ — un lien posé sur `ecrans` avant son ouverture est suivi.")
            return 1

        # ⭐ 12e cas ter : ffprobe ne rend AUCUN horodatage → refus (code 2), jamais un repli
        #    sur `-ss t` qui rendrait l'écran d'APRÈS. `instants` est remplacée le temps du cas.
        global instants
        vrai_instants = instants
        instants = lambda _v: ([], 0.0, [])
        vide = os.path.join(tmp, "sans-pts")
        os.makedirs(vide)
        vfd = tenir(vide)
        try:
            frames(v_sain, [0.5], [], vfd, os.path.join(vide, "ecrans"))
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            instants = vrai_instants
            os.close(vfd)
        aucune = not os.listdir(os.path.join(vide, "ecrans"))
        bon = code == 2 and aucune
        print(f"   {'✅' if bon else '🔴'} {'aucun horodatage lisible':<29} code {code} "
              f"(attendu 2) · {'aucune image devinée' if aucune else 'DES IMAGES DEVINÉES'}")
        if not bon:
            print("\n🔴 CASSÉ — sans horodatages, l'outil devine des écrans au lieu de refuser.")
            return 1
        # ⭐⭐ 16e cas (5e revue Codex, 12 sept.) : le transcripteur ÉCRIT SON JSON PUIS PLANTE
        #    (code 1). Avant : « rc ≠ 0 OU pas de JSON » — le JSON existait, le run continuait
        #    sur un transcript peut-être tronqué, code 0. Maintenant : code 2, rien copié.
        global TRANSCRIRE
        faux_py = os.path.join(tmp, "faux-transcripteur.py")
        # Boutons (variables d'environnement) : FAUX_DEBUT (début de la réplique, 0,2 s),
        # FAUX_VIDE_SUR (ce WAV rend `[]`), FAUX_JSON_VIDE_SUR (ce WAV rend un JSON de 0 octet,
        # code 0), FAUX_JSON_FORME_SUR + FAUX_JSON_FORME (ce WAV rend ce texte tel quel comme
        # JSON), FAUX_SANS_TXT_SUR (ce WAV n'écrit pas le .txt), FAUX_PLANTE_SUR (ce WAV plante
        # après son JSON), FAUX_PLANTE (code de sortie).
        open(faux_py, "w").write(
            "import json, os, sys\n"
            "detail = sys.argv[sys.argv.index('--detail-json') + 1]\n"
            "wav = os.path.basename(sys.argv[1])\n"
            "debut = float(os.environ.get('FAUX_DEBUT', '0.2'))\n"
            "segs = [] if wav == os.environ.get('FAUX_VIDE_SUR') else "
            "[{'debut': debut, 'fin': debut + 0.8, 'texte': 'phrase placee'}]\n"
            "if wav != os.environ.get('FAUX_SANS_TXT_SUR'):\n"
            "    open(sys.argv[2], 'w').write('phrase placee\\n' if segs else '')\n"
            "if wav == os.environ.get('FAUX_JSON_VIDE_SUR'):\n"
            "    open(detail, 'w').close()\n"
            "elif wav == os.environ.get('FAUX_JSON_FORME_SUR'):\n"
            "    open(detail, 'w').write(os.environ['FAUX_JSON_FORME'])\n"
            "else:\n"
            "    json.dump(segs, open(detail, 'w'))\n"
            "if wav == os.environ.get('FAUX_BRUIT_SUR'):\n"
            "    sys.stderr.buffer.write(b'bruit \\xff illisible\\ndeuxieme ligne\\n')\n"
            "    sys.stderr.buffer.flush()\n"
            "if wav == os.environ.get('FAUX_PLANTE_SUR'):\n"
            "    sys.exit(1)\n"
            "sys.exit(int(os.environ.get('FAUX_PLANTE', '0')))\n")

        def construire_faux(video, sortie, env=None):
            """`construire` avec le faux transcripteur ; rend le code de sortie."""
            global TRANSCRIRE
            vrai_transcrire, TRANSCRIRE = TRANSCRIRE, faux_py
            for k, v in (env or {}).items():
                os.environ[k] = v
            try:
                construire(video, "fr", 2, sortie)
                return 0
            except SystemExit as e:
                return e.code
            except Exception as e:                  # une trace d'appel n'est PAS un refus
                import traceback
                traceback.print_exc()
                return f"CRASH:{type(e).__name__}"
            finally:
                TRANSCRIRE = vrai_transcrire
                for k in (env or {}):
                    del os.environ[k]
        plante_tr = os.path.join(tmp, "garde-transcripteur-plante")
        code = construire_faux(v_sain, plante_tr, {"FAUX_PLANTE": "1"})
        copies = sorted(n for n in os.listdir(plante_tr) if n.startswith("transcript"))
        bon = code == 2 and not copies
        print(f"   {'✅' if bon else '🔴'} {'transcripteur planté après son JSON':<29} code {code} "
              f"(attendu 2) · {'rien copié' if not copies else f'COPIÉ QUAND MÊME : {copies}'}")
        if not bon:
            print("\n🔴 CASSÉ — un transcripteur qui plante après avoir écrit son JSON passe pour réussi.")
            return 1
        # ⭐⭐ 18e cas (6e revue Codex, 12 sept.) : DEUX pistes audio, la 2e fait planter le
        #    transcripteur. Avant : les transcripts bruts de la 1re étaient DÉJÀ copiés dans la
        #    sortie — « code 2, rien copié » était faux. Maintenant : rien n'entre tant que
        #    toutes les pistes n'ont pas rendu. Contrôle : sans plantage, les deux entrent.
        v_deux = os.path.join(tmp, "deux-pistes.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=320x180:rate=10", "-f", "lavfi",
                        "-i", "sine=frequency=440:r=16000", "-f", "lavfi",
                        "-i", "sine=frequency=880:r=16000", "-map", "0:v", "-map", "1:a",
                        "-map", "2:a", "-t", "2", "-pix_fmt", "yuv420p", v_deux], check=True)
        deux_plante = os.path.join(tmp, "garde-deux-pistes-plante")
        code = construire_faux(v_deux, deux_plante, {"FAUX_PLANTE_SUR": "audio-2.wav"})
        copies = sorted(n for n in os.listdir(deux_plante) if n.startswith("transcript"))
        deux_ok = os.path.join(tmp, "garde-deux-pistes-ok")
        code_ok = construire_faux(v_deux, deux_ok)
        entres = sorted(n for n in os.listdir(deux_ok) if n.startswith("transcript-piste"))
        bon = code == 2 and not copies and code_ok == 0 and \
            entres == ["transcript-piste-1.json", "transcript-piste-1.txt",
                       "transcript-piste-2.json", "transcript-piste-2.txt"]
        print(f"   {'✅' if bon else '🔴'} {'2 pistes, la 2e plante':<29} code {code} (attendu 2) · "
              f"{'rien copié' if not copies else f'COPIÉ QUAND MÊME : {copies}'} · contrôle sans "
              f"plantage code {code_ok}, {len(entres)} transcripts bruts")
        if not bon:
            print("\n🔴 CASSÉ — les transcripts d'une piste entrent avant que toutes aient rendu.")
            return 1
        # ⭐⭐ 19e cas (6e revue Codex) : un LIEN PHYSIQUE posé à `transcript.txt` vers un document
        #    de JNT, juste avant l'écriture (sonde « avant-transcript »). `O_NOFOLLOW` ne voit
        #    rien — les deux noms SONT le même fichier — et `O_TRUNC` vidait le document. Attendu :
        #    refus code 2, document intact.
        dur = os.path.join(tmp, "garde-lien-physique")
        doc_dur = os.path.join(tmp, "document-de-jnt-lie.txt")
        open(doc_dur, "w").write("le document de JNT, lié en dur\n")
        avant = sha(doc_dur)

        def lier(etape, *_):
            if etape == "avant-transcript":
                os.link(doc_dur, os.path.join(dur, "transcript.txt"))
        SONDE = lier
        try:
            code = construire_faux(v_sain, dur)
        finally:
            SONDE = None
        intact = sha(doc_dur) == avant
        bon = code == 2 and intact
        print(f"   {'✅' if bon else '🔴'} {'lien PHYSIQUE à mon nom pendant le run':<29} code {code} "
              f"(attendu 2) · document de JNT {'intact' if intact else 'VIDÉ'}")
        if not bon:
            print("\n🔴 CASSÉ — un lien physique posé à mon nom fait écrire dans le document de JNT.")
            return 1
        # ⭐⭐ 20e cas (6e revue Codex) : un run dont JNT a ANNOTÉ l'INDEX.md SUR PLACE (même inode),
        #    relancé sur le même dossier. Le registre est signé, les noms et les inodes y sont :
        #    seule l'EMPREINTE ne colle plus → pas à moi, code 2, INDEX annoté intact.
        #    ⚠️ v11c : annoté SUR PLACE, plus sur une copie `cp -R` — depuis que le registre porte
        #    l'inode, la copie est refusée pour son inode (cas S) avant que l'empreinte ne soit
        #    lue, et un mutant sans contrôle d'empreinte restait vert (suite de mutations v11).
        origine = os.path.join(tmp, "garde-annote-sur-place")
        code0 = construire_faux(v_sain, origine)
        with open(os.path.join(origine, "INDEX.md"), "a") as f:
            f.write("\nNOTE DE JNT : garder cette version.\n")
        avant = empreinte(origine)
        code = construire_faux(v_sain, origine)
        intact = empreinte(origine) == avant
        bon = code0 == 0 and code == 2 and intact
        print(f"   {'✅' if bon else '🔴'} {'INDEX annoté SUR PLACE par JNT':<29} code {code} "
              f"(attendu 2) · dossier {'intact' if intact else 'TOUCHÉ'}")
        if not bon:
            print("\n🔴 CASSÉ — un fichier inscrit mais MODIFIÉ par JNT est encore effacé.")
            return 1
        # ⭐ 21e cas (6e revue Codex) : un fichier ÉTRANGER à mon nom (`transcript.json`) posé dans le
        #    dossier PRIVÉ dès sa création, puis le transcripteur plante. Avant : le `finally`
        #    effaçait tout nom à moi trouvé là — le sien aussi. Maintenant : seuls les noms que
        #    ce run a créés partent, le fichier survit, le dossier reste (et on le dit).
        prive_etr = os.path.join(tmp, "garde-prive-etranger")
        prives_vus = []

        def glisser(etape, *info):
            if etape == "prive-cree":
                prives_vus.append(info[0])
                open(os.path.join(info[0], "transcript.json"), "w").write("le json de JNT\n")
        SONDE = glisser
        try:
            code = construire_faux(v_sain, prive_etr, {"FAUX_PLANTE": "1"})
        finally:
            SONDE = None
        survit = bool(prives_vus) and os.path.isfile(os.path.join(prives_vus[0], "transcript.json")) \
            and open(os.path.join(prives_vus[0], "transcript.json")).read() == "le json de JNT\n"
        restes = sorted(os.listdir(prives_vus[0])) if prives_vus and os.path.isdir(prives_vus[0]) else []
        for p in prives_vus:
            shutil.rmtree(p, ignore_errors=True)
        bon = code == 2 and survit and restes == ["transcript.json"]
        print(f"   {'✅' if bon else '🔴'} {'fichier étranger dans le dossier privé':<29} code {code} "
              f"(attendu 2) · {'survit, seul' if bon else f'EFFACÉ ou pas seul : {restes}'}")
        if not bon:
            print("\n🔴 CASSÉ — le nettoyage du dossier privé efface un fichier que je n'ai pas créé.")
            return 1
        # ⭐ 22e cas (6e revue Codex) : un VRAI dossier de JNT (pas un lien) glissé à la place
        #    d'`ecrans` entre sa création et son ouverture, avec SA photo `ecran-001.jpg` dedans.
        #    `O_NOFOLLOW` ne voit rien. Attendu : code 2, photo intacte.
        vrai_dir = os.path.join(tmp, "garde-vrai-dossier")
        os.makedirs(vrai_dir)
        photo6 = os.path.join(tmp, "photos-de-jnt-6", "ecran-001.jpg")

        def glisser_dossier(etape, *_):
            if etape == "ecrans-cree":
                os.rename(os.path.join(vrai_dir, "ecrans"), os.path.join(vrai_dir, "ecrans.mien"))
                os.makedirs(os.path.join(vrai_dir, "ecrans"))
                open(os.path.join(vrai_dir, "ecrans", "ecran-001.jpg"), "wb").write(b"\xff\xd8 photo de JNT 6")
        SONDE = glisser_dossier
        gfd = tenir(vrai_dir)
        try:
            frames(v_sain, [0.5], [], gfd, os.path.join(vrai_dir, "ecrans"))
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            SONDE = None
            os.close(gfd)
        intacte = open(os.path.join(vrai_dir, "ecrans", "ecran-001.jpg"), "rb").read() == b"\xff\xd8 photo de JNT 6"
        bon = code == 2 and intacte
        print(f"   {'✅' if bon else '🔴'} {'VRAI dossier glissé à `ecrans`':<29} code {code} "
              f"(attendu 2) · photo de JNT {'intacte' if intacte else 'ÉCRASÉE'}")
        if not bon:
            print("\n🔴 CASSÉ — un vrai dossier de JNT glissé à `ecrans` reçoit mes écrans par-dessus les siens.")
            return 1

        # ⭐ 22e cas bis — SUITE DE MUTATIONS v9 : le 22e cas est tenu par TROIS gardes en série
        #    (`O_NOFOLLOW` à l'ouverture, « restes à mon nom » après, `O_EXCL` à l'écriture) qui se
        #    masquent l'un l'autre — le mutant qui ignore les restes passait, `O_EXCL` refusant
        #    l'écrasement à sa place. Ici la photo de JNT porte un nom à moi que JE N'ÉCRIRAIS PAS
        #    (`ecran-005.jpg`, une seule image visée) : seul le garde « restes » peut refuser ;
        #    sans lui, `ecran-001.jpg` NAÎT dans le dossier de JNT, code 0. Attendu : code 2,
        #    contenu du dossier inchangé.
        autre_nom = os.path.join(tmp, "garde-restes-autre-nom")
        os.makedirs(autre_nom)

        def glisser_autre(etape, *_):
            if etape == "ecrans-cree":
                os.rename(os.path.join(autre_nom, "ecrans"), os.path.join(autre_nom, "ecrans.mien"))
                os.makedirs(os.path.join(autre_nom, "ecrans"))
                open(os.path.join(autre_nom, "ecrans", "ecran-005.jpg"), "wb").write(b"\xff\xd8 photo de JNT 7")
        SONDE = glisser_autre
        afd = tenir(autre_nom)
        try:
            frames(v_sain, [0.5], [], afd, os.path.join(autre_nom, "ecrans"))
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            SONDE = None
            os.close(afd)
        contenu = sorted(os.listdir(os.path.join(autre_nom, "ecrans")))
        inchange = contenu == ["ecran-005.jpg"]
        bon = code == 2 and inchange
        print(f"   {'✅' if bon else '🔴'} {'dossier de JNT, autre nom à moi':<29} code {code} "
              f"(attendu 2) · contenu {'inchangé' if inchange else 'MODIFIÉ : ' + ', '.join(contenu)}")
        if not bon:
            print("\n🔴 CASSÉ — un dossier de JNT qui porte un nom à moi reçoit quand même mes écrans.")
            return 1

        # ⭐ 12e cas bis-bis — SUITE DE MUTATIONS v9 : même masquage pour `O_NOFOLLOW` à l'ouverture
        #    d'`ecrans`. Le 12e cas bis pose un lien vers un dossier de JNT qui contient
        #    `ecran-001.jpg` : sans `O_NOFOLLOW`, le garde « restes » refusait à sa place. Ici le
        #    dossier de JNT ne contient AUCUN nom à moi (`photo.jpg`) : sans `O_NOFOLLOW`, le lien
        #    est suivi et `ecran-001.jpg` NAÎT chez JNT, code 0. Attendu : code 2, dossier inchangé.
        lien_vierge = os.path.join(tmp, "garde-lien-dossier-vierge")
        os.makedirs(lien_vierge)
        photos8 = os.path.join(tmp, "photos-de-jnt-8")
        os.makedirs(photos8)
        open(os.path.join(photos8, "photo.jpg"), "wb").write(b"\xff\xd8 photo de JNT 8")

        def lier_vierge(etape, *_):
            if etape == "ecrans-cree":
                os.rmdir(os.path.join(lien_vierge, "ecrans"))
                os.symlink(photos8, os.path.join(lien_vierge, "ecrans"))
        SONDE = lier_vierge
        lfd = tenir(lien_vierge)
        try:
            frames(v_sain, [0.5], [], lfd, os.path.join(lien_vierge, "ecrans"))
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            SONDE = None
            os.close(lfd)
        contenu = sorted(os.listdir(photos8))
        inchange = contenu == ["photo.jpg"]
        bon = code == 2 and inchange
        print(f"   {'✅' if bon else '🔴'} {'`ecrans` → lien, dossier SANS mes noms':<29} code {code} "
              f"(attendu 2) · dossier de JNT {'inchangé' if inchange else 'MODIFIÉ : ' + ', '.join(contenu)}")
        if not bon:
            print("\n🔴 CASSÉ — un lien posé sur `ecrans` vers un dossier sans mes noms est suivi, mes écrans naissent chez JNT.")
            return 1
        # ⭐ 23e cas (6e revue Codex) : au nettoyage, `ecrans` (le mien, vidé) est remplacé par un
        #    dossier VIDE de JNT juste avant la suppression. Avant : `os.rmdir("ecrans")` l'effaçait.
        #    Maintenant : `ecrans` n'est jamais retiré. Attendu : code 0, le dossier de JNT est là.
        rm_dir = os.path.join(tmp, "garde-rmdir")
        os.makedirs(os.path.join(rm_dir, "ecrans"))
        open(os.path.join(rm_dir, "ecrans", "ecran-001.jpg"), "wb").write(b"\xff\xd8 mienne")
        _registre(rm_dir, ["ecrans/ecran-001.jpg"])

        def glisser_vide(etape, *_):
            if etape == "avant-suppression":
                os.rename(os.path.join(rm_dir, "ecrans"), os.path.join(rm_dir, "ecrans.mien"))
                os.makedirs(os.path.join(rm_dir, "ecrans"))
        SONDE = glisser_vide
        rfd = tenir(rm_dir)
        try:
            nettoyer(rm_dir, rfd)
            code = 0
        except SystemExit as e:
            code = e.code
        finally:
            SONDE = None
            os.close(rfd)
        reste = os.path.isdir(os.path.join(rm_dir, "ecrans"))
        bon = code == 0 and reste
        print(f"   {'✅' if bon else '🔴'} {'dossier VIDE de JNT glissé à `ecrans`':<29} code {code} · "
              f"{'toujours là' if reste else 'EFFACÉ'}")
        if not bon:
            print("\n🔴 CASSÉ — le nettoyage retire un dossier vide qui n'est pas le mien.")
            return 1
        # ⭐⭐ 6e cas (revue Codex, 12 sept. 2026) : un dossier À MOI (marqueur) où JNT a posé
        #    sa vidéo ET un fichier à lui. L'outil doit ACCEPTER (c'est son dossier) et
        #    NE TOUCHER NI À L'UN NI À L'AUTRE. Avant : `rmtree` — la vidéo partait avant
        #    d'être transcrite, code 1, source perdue.
        if shutil.which("say"):
            mien = os.path.join(tmp, "garde-mien")
            os.makedirs(mien, exist_ok=True)
            open(os.path.join(mien, "INDEX.md"), "w").write("# REGARD — ancien\n")
            _registre(mien, ["INDEX.md"])
            temoin = os.path.join(mien, "mes-notes.md")
            open(temoin, "w").write("fichier de JNT")
            aiff = _voix(tmp, "dedans", "Le bouton bleu doit devenir vert.")
            v_dedans = os.path.join(mien, "ma-video.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                            "-i", "testsrc=size=320x180:rate=10", "-i", aiff, "-shortest",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", v_dedans], check=True)
            de_jnt = {k: v for k, v in empreinte(mien).items() if k in ("mes-notes.md", "ma-video.mp4")}
            # ⭐ DEUX runs de suite (3e revue Codex) : le 2e ne réussit que si le 1er a inscrit
            #    TOUT ce qu'il a écrit — un écran non inscrit fait refuser le 2e run en code 2.
            codes, registres = [], []
            for _ in range(2):
                r = subprocess.run([sys.executable, moi, v_dedans, "--sortie", mien],
                                   capture_output=True, text=True)
                codes.append(r.returncode)
                inscrits = set(l.split(" ", 2)[2] for l in open(os.path.join(mien, MARQUEUR)).read().splitlines()[1:]
                               if l.count(" ") >= 2) if os.path.isfile(os.path.join(mien, MARQUEUR)) else set()
                miens = [k for k in empreinte(mien) if k != MARQUEUR and k not in de_jnt]
                registres.append(sorted(k for k in miens if k not in inscrits))
            apres = {k: v for k, v in empreinte(mien).items() if k in de_jnt}
            survie = apres == de_jnt
            index_neuf = "bouton" in open(os.path.join(mien, "INDEX.md"), errors="ignore").read().lower() \
                if os.path.exists(os.path.join(mien, "INDEX.md")) else False
            bon = codes == [0, 0] and survie and index_neuf and not any(registres)
            print(f"   {'✅' if bon else '🔴'} {'vidéo + notes DANS mon dossier, 2 runs':<22} codes {codes} "
                  f"(attendu [0, 0]) · vidéo et notes {'intactes (mêmes empreintes)' if survie else 'TOUCHÉES'} · "
                  f"INDEX {'refait' if index_neuf else 'PAS REFAIT'} · "
                  + (f"⛔ écrits SANS être inscrits : {registres}" if any(registres)
                     else f"{len(miens)} fichiers écrits, tous inscrits au registre"))
            if not bon:
                print("\n🔴 CASSÉ — l'outil efface ce qui n'est pas à lui dans son propre dossier, "
                      "n'y refait plus son INDEX, ou écrit sans inscrire (et se refuse au run suivant).")
                return 1
            # ⭐⭐ 13e cas (4e revue Codex, 12 sept.) : le DOSSIER DE SORTIE ENTIER est renommé et
            #    remplacé par un lien vers un dossier de JNT (qui contient SON `transcript.txt`)
            #    juste avant l'écriture du transcript (sonde « avant-transcript »). Avant :
            #    `open(base/transcript.txt, "w")` suivait le lien — son texte partait, code 0.
            #    Maintenant : tout s'écrit par le descripteur du VRAI dossier.
            detourne = os.path.join(tmp, "garde-detourne")
            os.makedirs(detourne)
            notes_jnt = os.path.join(tmp, "notes-de-jnt")
            os.makedirs(notes_jnt)
            open(os.path.join(notes_jnt, "transcript.txt"), "w").write("LE transcript de JNT\n")
            open(os.path.join(notes_jnt, "INDEX.md"), "w").write("L'INDEX de JNT\n")
            avant = empreinte(notes_jnt)

            def detourner(etape, *_):
                if etape == "avant-transcript" and not os.path.islink(detourne):
                    os.rename(detourne, detourne + ".vrai")
                    os.symlink(notes_jnt, detourne)
            SONDE = detourner
            try:
                construire(v_dedans, "fr", 2, detourne)
                code = 0
            except SystemExit as e:
                code = e.code
            finally:
                SONDE = None
            chez_jnt = empreinte(notes_jnt) != avant
            vrai = detourne + ".vrai"
            chez_moi = os.path.isfile(os.path.join(vrai, "transcript.txt")) and \
                os.path.isfile(os.path.join(vrai, "INDEX.md")) and \
                "bouton" in open(os.path.join(vrai, "INDEX.md"), errors="ignore").read().lower()
            bon = code == 0 and not chez_jnt and chez_moi
            print(f"   {'✅' if bon else '🔴'} {'dossier de sortie → lien PENDANT le run':<22} code {code} · "
                  f"notes de JNT {'RÉÉCRITES' if chez_jnt else 'intactes'} · "
                  f"transcript et INDEX {'dans le vrai dossier' if chez_moi else 'AILLEURS'}")
            if not bon:
                print("\n🔴 CASSÉ — remplacer le dossier de sortie par un lien pendant le run fait "
                      "écrire chez JNT.")
                return 1
            # ⭐⭐ 17e cas (5e revue Codex, 12 sept.) : le DOSSIER PRIVÉ (WAV, transcripts bruts)
            #    est remplacé par un lien vers un dossier de JNT dès sa création (sonde
            #    « prive-cree »). Avant : ffmpeg écrivait `audio-1.wav` par chemin → chez JNT,
            #    et le transcript brut aussi. Maintenant : ils naissent par descripteur, JNT
            #    ne reçoit rien, et le run réussit quand même.
            prive_jnt = os.path.join(tmp, "prive-de-jnt")
            os.makedirs(prive_jnt)
            open(os.path.join(prive_jnt, "audio-1.wav"), "wb").write(b"RIFF le wav de JNT")
            open(os.path.join(prive_jnt, "transcript-piste-1.txt"), "w").write("le texte de JNT\n")
            avant = empreinte(prive_jnt)
            prives = []

            def detourner_prive(etape, *info):
                if etape == "prive-cree":
                    prives.append(info[0])
                    os.rename(info[0], info[0] + ".vrai")
                    os.symlink(prive_jnt, info[0])
            SONDE = detourner_prive
            sortie_pv = os.path.join(tmp, "garde-prive")
            try:
                construire(v_dedans, "fr", 2, sortie_pv)
                code = 0
            except SystemExit as e:
                code = e.code
            finally:
                SONDE = None
                for p in prives:
                    if os.path.islink(p):
                        os.unlink(p)
                    shutil.rmtree(p + ".vrai", ignore_errors=True)
            chez_jnt = empreinte(prive_jnt) != avant
            index_pv = os.path.join(sortie_pv, "INDEX.md")
            fait = os.path.isfile(index_pv) and "bouton" in open(index_pv, errors="ignore").read().lower()
            bon = code == 0 and not chez_jnt and fait and len(prives) == 1
            print(f"   {'✅' if bon else '🔴'} {'dossier PRIVÉ → lien PENDANT le run':<22} code {code} · "
                  f"dossier de JNT {'TOUCHÉ' if chez_jnt else 'intact'} · INDEX {'refait' if fait else 'PAS FAIT'}")
            if not bon:
                print("\n🔴 CASSÉ — remplacer le dossier privé par un lien pendant le run fait écrire "
                      "le WAV ou le transcript chez JNT.")
                return 1
        else:
            print("   ⚪ cas « vidéo DANS mon dossier » NON REJOUÉ (`say` absent)")

        # ══ 7e REVUE CODEX (12 sept. 2026) — cas A à L. Chaque garde neuf a SON cas, placé là
        #    où aucun autre garde ne peut refuser à sa place (sinon le mutant est aveugle).
        def juger(titre, bon, code, attendu, note, casse):
            print(f"   {'✅' if bon else '🔴'} {titre:<38} code {code} (attendu {attendu}) · {note}")
            if not bon:
                print(f"\n🔴 CASSÉ — {casse}")
            return bon

        def lancer(video, sortie, sonde=None, env=None, err=None):
            """`err` : un io.StringIO qui reçoit ce que `construire` dit sur stderr."""
            global SONDE
            SONDE = sonde
            vrai_err = sys.stderr
            if err is not None:
                sys.stderr = err
            try:
                return construire_faux(video, sortie, env)
            finally:
                SONDE = None
                sys.stderr = vrai_err

        def contenu(chemin, binaire=False):
            try:
                return open(chemin, "rb" if binaire else "r").read()
            except OSError:
                return None

        # A. Le REGISTRE est remplacé pendant le run (sonde « avant-transcript ») : le mien est
        #    renommé, et un LIEN PHYSIQUE vers une note de JNT prend son nom. Avant : `noter`
        #    rouvrait `.regarder` par nom → mes lignes dans la note, code 0. Attendu : code 0,
        #    note intacte, mes lignes dans MON fichier renommé, et le dossier refusé au run suivant.
        note_a = os.path.join(tmp, "note-de-jnt.md")
        open(note_a, "w").write("une note\n")
        sortie_a = os.path.join(tmp, "garde-registre-remplace")

        def remplacer_registre(etape, *_):
            if etape == "avant-transcript":
                os.rename(os.path.join(sortie_a, MARQUEUR), os.path.join(sortie_a, MARQUEUR + ".mien"))
                os.link(note_a, os.path.join(sortie_a, MARQUEUR))
        err_a = io.StringIO()
        code = lancer(v_sain, sortie_a, remplacer_registre, err=err_a)
        lignes_a = (contenu(os.path.join(sortie_a, MARQUEUR + ".mien")) or "").splitlines()
        note_ok = contenu(note_a) == "une note\n"
        dit_a = "REMPLACÉ pendant le run" in err_a.getvalue()
        code2 = lancer(v_sain, sortie_a)
        note_ok2 = contenu(note_a) == "une note\n"
        bon = (code == 0 and note_ok and lignes_a[:1] == [ENTETE] and dit_a
               and any(l.endswith(" INDEX.md") for l in lignes_a) and code2 == 2 and note_ok2)
        if not juger("registre REMPLACÉ pendant le run", bon, f"{code} puis {code2}", "0 puis 2",
                     f"note de JNT {'intacte' if note_ok and note_ok2 else 'TOUCHÉE'} · mes lignes "
                     f"{'chez moi' if any(l.endswith(' INDEX.md') for l in lignes_a) else 'PERDUES'}"
                     f" · {'dit' if dit_a else 'PAS DIT'}",
                     "un registre rouvert par nom écrit mes lignes dans un fichier de JNT."):
            return 1

        # B. Entre le contrôle et l'effacement du nettoyage (sonde « avant-suppression »), mon
        #    INDEX.md vérifié est renommé et un INDEX.md de JNT prend son nom. Avant : `unlink`
        #    par nom effaçait le sien. Attendu : code 2, le sien reste.
        sortie_b = os.path.join(tmp, "garde-index-remplace-nettoyage")
        if lancer(v_sain, sortie_b) != 0:
            print("\n🔴 CASSÉ — le run de préparation du cas B a échoué.")
            return 1

        def remplacer_index(etape, *_):
            if etape == "avant-suppression":
                os.rename(os.path.join(sortie_b, "INDEX.md"), os.path.join(sortie_b, "INDEX.md.mien"))
                open(os.path.join(sortie_b, "INDEX.md"), "w").write("l'index de JNT\n")
        code = lancer(v_sain, sortie_b, remplacer_index)
        intact = contenu(os.path.join(sortie_b, "INDEX.md")) == "l'index de JNT\n"
        if not juger("INDEX REMPLACÉ pendant le nettoyage", code == 2 and intact, code, 2,
                     f"INDEX de JNT {'intact' if intact else 'EFFACÉ ou modifié'}",
                     "le nettoyage efface par nom un fichier posé après le contrôle."):
            return 1

        # C. Même fenêtre, mais l'INDEX.md est ANNOTÉ SUR PLACE (même inode). Avant : effacé.
        #    Attendu : code 2, et le fichier annoté est toujours là, tel quel.
        sortie_c = os.path.join(tmp, "garde-index-annote-nettoyage")
        if lancer(v_sain, sortie_c) != 0:
            print("\n🔴 CASSÉ — le run de préparation du cas C a échoué.")
            return 1
        index_c = os.path.join(sortie_c, "INDEX.md")
        avant_c = contenu(index_c)

        def annoter_index(etape, *_):
            if etape == "avant-suppression":
                open(index_c, "a").write("note de JNT ajoutée\n")
        code = lancer(v_sain, sortie_c, annoter_index)
        apres_c = contenu(index_c)
        intact = apres_c == avant_c + "note de JNT ajoutée\n"
        if not juger("INDEX ANNOTÉ pendant le nettoyage", code == 2 and intact, code, 2,
                     f"INDEX annoté {'restauré tel quel' if intact else 'PERDU ou altéré'}",
                     "un fichier modifié entre le contrôle et l'effacement part avec l'annotation."):
            return 1

        # D. Un `transcript.txt` de JNT glissé dans la sortie juste avant l'écriture du mien
        #    (sonde « avant-transcript »). Le refus existait (O_EXCL) — mais le registre portait
        #    DÉJÀ une ligne `transcript.txt` (inscrit avant d'écrire). Attendu : code 2, fichier
        #    intact, et AUCUNE ligne `transcript.txt` au registre.
        sortie_d = os.path.join(tmp, "garde-transcript-glisse")
        transcript_d = os.path.join(sortie_d, "transcript.txt")

        def glisser_transcript(etape, *_):
            if etape == "avant-transcript":
                open(transcript_d, "w").write("le transcript de JNT\n")
        code = lancer(v_sain, sortie_d, glisser_transcript)
        intact = contenu(transcript_d) == "le transcript de JNT\n"
        inscrit = any(l.endswith(" transcript.txt")
                      for l in (contenu(os.path.join(sortie_d, MARQUEUR)) or "").splitlines())
        if not juger("refus d'écriture → rien au registre", code == 2 and intact and not inscrit,
                     code, 2, f"fichier {'intact' if intact else 'TOUCHÉ'} · registre "
                     f"{'sans sa ligne' if not inscrit else 'PORTE SA LIGNE (un run suivant effacerait le fichier)'}",
                     "un fichier de JNT refusé à l'écriture est quand même inscrit comme mien."):
            return 1

        # D2. Même garde, sur un ÉCRAN : `ecran-001.jpg` de JNT glissé dans `ecrans/` à la sonde
        #    « ecran-rendu », après le garde des restes et avant `ecrire`. Le mutant « écrans
        #    inscrits AVANT d'être écrits » restait vert sans ce cas. Attendu : code 2, image
        #    de JNT intacte, AUCUNE ligne `ecrans/ecran-001.jpg` au registre.
        sortie_d2 = os.path.join(tmp, "garde-ecran-glisse")
        ecran_d2 = os.path.join(sortie_d2, "ecrans", "ecran-001.jpg")

        def glisser_ecran(etape, *info):
            if etape == "ecran-rendu" and info and info[0] == "ecran-001.jpg":
                open(ecran_d2, "wb").write(b"la photo de JNT")
        code = lancer(v_sain, sortie_d2, glisser_ecran)
        intact = contenu(ecran_d2, True) == b"la photo de JNT"
        inscrit = any(l.endswith(" ecrans/ecran-001.jpg")
                      for l in (contenu(os.path.join(sortie_d2, MARQUEUR)) or "").splitlines())
        if not juger("refus d'écriture d'un écran → rien au registre", code == 2 and intact and not inscrit,
                     code, 2, f"photo {'intacte' if intact else 'TOUCHÉE'} · registre "
                     f"{'sans sa ligne' if not inscrit else 'PORTE SA LIGNE (un run suivant effacerait la photo)'}",
                     "un écran de JNT refusé à l'écriture est quand même inscrit comme mien."):
            return 1

        # E. Un LIEN PHYSIQUE posé sur mon INDEX.md entre sa création et son premier octet
        #    (sonde « fichier-cree »). Le contrôle `st_nlink` existait depuis la 6e revue mais
        #    n'avait jamais été vu bloquer. Attendu : code 2, l'alias reste VIDE.
        sortie_e = os.path.join(tmp, "garde-lien-physique-a-la-creation")
        alias_e = os.path.join(sortie_e, "alias-de-jnt")

        def lier_index(etape, *info):
            if etape == "fichier-cree" and info and info[0] == "INDEX.md":
                os.link(os.path.join(sortie_e, "INDEX.md"), alias_e)
        code = lancer(v_sain, sortie_e, lier_index)
        vide = os.path.isfile(alias_e) and os.path.getsize(alias_e) == 0
        if not juger("lien physique posé à la création", code == 2 and vide, code, 2,
                     f"alias {'vide' if vide else 'REMPLI ou absent'}",
                     "un fichier à deux noms au moment d'écrire reçoit quand même mes octets."):
            return 1

        # F. Un registre qui inscrit DEUX fois le même nom (6e revue : « altéré ») — le garde
        #    n'avait pas de cas. Attendu : code 2, l'INDEX reste.
        sortie_f = os.path.join(tmp, "garde-registre-double")
        os.makedirs(sortie_f)
        index_f = os.path.join(sortie_f, "INDEX.md")
        open(index_f, "w").write("# REGARD — vieux\n")
        _registre(sortie_f, ["INDEX.md"], brutes=[f"{sha(index_f)} {ident(index_f)} INDEX.md"])
        code = lancer(v_sain, sortie_f)
        intact = contenu(index_f) == "# REGARD — vieux\n"
        if not juger("nom en DOUBLE au registre", code == 2 and intact, code, 2,
                     f"INDEX {'intact' if intact else 'EFFACÉ'}",
                     "un registre qui inscrit deux fois un nom est accepté comme le mien."):
            return 1

        # G. Un VRAI fichier de JNT à `audio-1.wav` dans le dossier privé dès sa création (sonde
        #    « prive-cree »). Avant : ffmpeg (`-y`, par nom) l'écrasait. Attendu : code 2, intact.
        prives_g = []

        def planter_wav(etape, *info):
            if etape == "prive-cree":
                prives_g.append(info[0])
                open(os.path.join(info[0], "audio-1.wav"), "wb").write(b"RIFF le wav de JNT")
        code = lancer(v_sain, os.path.join(tmp, "garde-wav-plante"), planter_wav)
        wav_g = os.path.join(prives_g[0], "audio-1.wav") if prives_g else ""
        intact = contenu(wav_g, binaire=True) == b"RIFF le wav de JNT"
        for p in prives_g:
            shutil.rmtree(p, ignore_errors=True)
        if not juger("WAV de JNT déjà dans le privé", code == 2 and intact, code, 2,
                     f"wav {'intact' if intact else 'ÉCRASÉ'}",
                     "ffmpeg écrase un fichier qui existait à mon nom dans le dossier privé."):
            return 1

        # G2. Mon WAV créé, puis — avant que ffmpeg parte (sonde « wav-cree ») — renommé, et un
        #    LIEN PHYSIQUE vers un WAV de JNT posé à son nom. Avant : ffmpeg écrivait par nom →
        #    dans le fichier de JNT. Attendu : ffmpeg écrit par MON descripteur, le fichier de
        #    JNT est intact, et le nom qui ne porte plus mon inode fait refuser (code 2).
        wav_jnt = os.path.join(tmp, "wav-de-jnt.wav")
        open(wav_jnt, "wb").write(b"RIFF le wav de JNT")
        prives_g2 = []

        def detourner_wav(etape, *info):
            if etape == "prive-cree":
                prives_g2.append(info[0])
            elif etape == "wav-cree" and prives_g2:
                p = os.path.join(prives_g2[0], info[0])
                os.rename(p, p + ".mien")
                os.link(wav_jnt, p)
        code = lancer(v_sain, os.path.join(tmp, "garde-wav-detourne"), detourner_wav)
        intact = contenu(wav_jnt, binaire=True) == b"RIFF le wav de JNT"
        for p in prives_g2:
            shutil.rmtree(p, ignore_errors=True)
        if not juger("WAV détourné par lien physique", code == 2 and intact, code, 2,
                     f"wav de JNT {'intact' if intact else 'ÉCRASÉ'}",
                     "ffmpeg écrit le WAV par nom : un lien physique l'envoie chez JNT."):
            return 1

        # G3. Mon WAV créé, puis (sonde « wav-cree ») REMPLACÉ par un vrai fichier de JNT au
        #    même nom (une copie, un seul nom — `st_nlink` ne voit rien). ffmpeg écrit par mon
        #    descripteur, dans le fichier renommé ; c'est celui de JNT qui porte le nom. Sans le
        #    contrôle d'inode de `_ouvrir_prive`, le transcripteur transcrirait LE SIEN, code 0.
        #    Attendu : code 2, fichier intact.
        prives_g3 = []

        def substituer_wav(etape, *info):
            if etape == "prive-cree":
                prives_g3.append(info[0])
            elif etape == "wav-cree" and prives_g3:
                p = os.path.join(prives_g3[0], info[0])
                os.rename(p, p + ".mien")
                open(p, "wb").write(b"RIFF le wav de JNT")
        code = lancer(v_sain, os.path.join(tmp, "garde-wav-substitue"), substituer_wav)
        wav_g3 = os.path.join(prives_g3[0], "audio-1.wav") if prives_g3 else ""
        intact = contenu(wav_g3, binaire=True) == b"RIFF le wav de JNT"
        for p in prives_g3:
            shutil.rmtree(p, ignore_errors=True)
        if not juger("WAV substitué par un vrai fichier", code == 2 and intact, code, 2,
                     f"wav de JNT {'intact' if intact else 'TOUCHÉ'}",
                     "un nom du privé qui ne porte plus mon inode est lu comme le mien."):
            return 1

        # H. Un LIEN PHYSIQUE vers un JSON de JNT posé à `transcript-piste-1.json` dans le privé
        #    avant que le transcripteur parte. Il écrit par nom (`open(..., "w")`) → le JSON de
        #    JNT vidé. Attendu : code 2 AVANT qu'il parte, JSON intact.
        json_jnt = os.path.join(tmp, "json-de-jnt.json")
        open(json_jnt, "w").write("le json de JNT\n")
        prives_h = []

        def lier_json(etape, *info):
            if etape == "prive-cree":
                prives_h.append(info[0])
                os.link(json_jnt, os.path.join(info[0], "transcript-piste-1.json"))
        code = lancer(v_sain, os.path.join(tmp, "garde-json-lie"), lier_json)
        intact = contenu(json_jnt) == "le json de JNT\n"
        for p in prives_h:
            shutil.rmtree(p, ignore_errors=True)
        # H'. La même chose sur `transcript-piste-1.txt` (8e revue : la branche `.txt` n'avait
        #     aucun cas — un garde qui ne vérifie que le `.json` y laissait ÉCRASER le document).
        txt_jnt = os.path.join(tmp, "texte-de-jnt.txt")
        open(txt_jnt, "w").write("le document de JNT, trente et un\n")
        prives_h2 = []

        def lier_txt(etape, *info):
            if etape == "prive-cree":
                prives_h2.append(info[0])
                os.link(txt_jnt, os.path.join(info[0], "transcript-piste-1.txt"))
        code_h2 = lancer(v_sain, os.path.join(tmp, "garde-txt-lie"), lier_txt)
        intact_h2 = contenu(txt_jnt) == "le document de JNT, trente et un\n"
        for p in prives_h2:
            shutil.rmtree(p, ignore_errors=True)
        if not juger("sortie `.txt` déjà liée (H')", code_h2 == 2 and intact_h2, code_h2, 2,
                     "document intact" if intact_h2 else "DOCUMENT DE JNT ÉCRASÉ",
                     "un lien physique sur la sortie `.txt` du transcripteur fait écraser un document de JNT."):
            return 1
        if not juger("sortie du transcripteur déjà liée", code == 2 and intact, code, 2,
                     f"json de JNT {'intact' if intact else 'ÉCRASÉ'}",
                     "le transcripteur écrit par nom sur un lien physique vers un fichier de JNT."):
            return 1

        # I. Un fichier de JNT DÉPLACÉ à `transcript-piste-1.json` dans le privé après que je
        #    l'ai lu (sonde « avant-transcript »). Avant : l'effacement final, par nom, le
        #    retirait. Attendu : code 0, le fichier survit (inode inconnu → pas à moi).
        fichier_i = os.path.join(tmp, "fichier-de-jnt.json")
        open(fichier_i, "w").write("le fichier de JNT\n")
        prives_i = []

        def glisser_json(etape, *info):
            if etape == "prive-cree":
                prives_i.append(info[0])
            elif etape == "avant-transcript" and prives_i:
                os.rename(fichier_i, os.path.join(prives_i[0], "transcript-piste-1.json"))
        code = lancer(v_sain, os.path.join(tmp, "garde-json-glisse"), glisser_json)
        survit = bool(prives_i) and contenu(os.path.join(prives_i[0], "transcript-piste-1.json")) \
            == "le fichier de JNT\n"
        for p in prives_i:
            shutil.rmtree(p, ignore_errors=True)
        if not juger("fichier de JNT glissé à mon nom (privé)", code == 0 and survit, code, 0,
                     f"fichier {'survit' if survit else 'EFFACÉ'}",
                     "l'effacement du dossier privé retire par nom un fichier qui n'est pas le mien."):
            return 1

        # J. Une vidéo dont l'IMAGE commence 2 s APRÈS le son : à 0,2 s, aucune image n'existe,
        #    la réplique reçoit la 1re image (2,0 s) — celle d'APRÈS. Avant : sans un mot.
        #    Attendu : l'INDEX le dit (« écran d'APRÈS »).
        v_tard = os.path.join(tmp, "image-en-retard.mov")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=duration=4",
                        "-itsoffset", "2", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=10:duration=2",
                        "-map", "1:v", "-map", "0:a", "-c:v", "libx264", "-g", "10",
                        "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", v_tard], check=True)
        sortie_j = os.path.join(tmp, "garde-ecran-d-apres")
        code = lancer(v_tard, sortie_j)
        index_j = contenu(os.path.join(sortie_j, "INDEX.md")) or ""
        dit = "écran d'APRÈS" in index_j
        if not juger("image qui commence APRÈS le son", code == 0 and dit, code, 0,
                     f"INDEX {'le dit' if dit else 'NE LE DIT PAS'}",
                     "une réplique reçoit l'écran d'après sans que l'INDEX le signale."):
            return 1

        # K. Une vidéo à HORLOGE NÉGATIVE (start −0,5 s) : l'image 0 ne se décode pas depuis
        #    une clé connue, mais l'image 20 (clé à 20) doit se rendre — en comptant depuis SA
        #    clé, pas depuis 0. Avant : « compter depuis 0 » passait pour équivalent.
        v_neg = os.path.join(tmp, "horloge-negative.mov")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc2=size=160x90:rate=10:duration=4", "-f", "lavfi",
                        "-i", "aevalsrc=sin(440*2*PI*t):s=48000:d=4", "-c:v", "libx264", "-g", "10",
                        "-c:a", "pcm_s16le", "-avoid_negative_ts", "disabled",
                        "-output_ts_offset", "-0.5", v_neg], check=True)
        pts_k, depart_k, cles_k = instants(v_neg)
        jpeg_k, motif_k = rendre(v_neg, pts_k, depart_k, cles_k, 20) if len(pts_k) > 20 else (None, "trop court")
        bon = jpeg_k is not None and 20 in cles_k
        if not juger("image 20 comptée depuis SA clé", bon, "—", "—",
                     "rendue" if bon else f"PAS RENDUE : {motif_k}",
                     "une image se compte depuis 0 au lieu de sa clé : rien ne sort sur une horloge décalée."):
            return 1

        # L. DEUX pistes audio, la 2e décalée de 0,7 s : son début doit se lire sur ELLE.
        #    Avant : lu sur la piste 0 pour toutes — le micro prenait l'horloge du système.
        v_deux_dec = os.path.join(tmp, "deux-pistes-decalees.mov")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc2=size=160x90:rate=10:duration=3", "-f", "lavfi",
                        "-i", "sine=duration=3", "-itsoffset", "0.7", "-f", "lavfi",
                        "-i", "sine=frequency=600:duration=2.3", "-map", "0:v", "-map", "1:a",
                        "-map", "2:a", "-c:v", "libx264", "-g", "10", "-c:a", "pcm_s16le",
                        v_deux_dec], check=True)
        d0, d1 = debut_piste(v_deux_dec, 0), debut_piste(v_deux_dec, 1)
        bon = abs(d0) < 0.05 and abs(d1 - 0.7) < 0.05
        if not juger("début lu sur SA piste", bon, "—", "—", f"piste 1 : {d0:.3f} s · piste 2 : {d1:.3f} s",
                     "le début de la 2e piste est lu sur la 1re : le micro prend l'horloge du système."):
            return 1

        # ══ 8e REVUE CODEX (12 sept. 2026) — cas M à V. Chaque défaut trouvé a SON cas.
        def preparer(nom):
            """Un dossier de sortie À MOI (un run propre), pour un 2e run qui NETTOIE."""
            sortie = os.path.join(tmp, nom)
            if lancer(v_sain, sortie) != 0:
                print(f"\n🔴 CASSÉ — le run de préparation de `{nom}` a échoué.")
                return None
            return sortie

        # M. Au moment du RETRAIT de mon INDEX.md (sonde « avant-retrait »), il est renommé et
        #    un fichier de JNT prend son nom. `_a_part` l'emporte, l'inode n'est pas le mien →
        #    il est REMIS à son nom (`_remettre`), refus. Attendu : code 2, le fichier de JNT
        #    à `INDEX.md`, intact — pas sous un nom privé.
        sortie_m = preparer("garde-retrait-remplace")
        if sortie_m is None:
            return 1
        de_jnt = os.path.join(tmp, "index-de-jnt.md")

        def remplacer_au_retrait(etape, *info):
            if etape == "avant-retrait" and info and info[0] == "INDEX.md":
                os.rename(os.path.join(sortie_m, "INDEX.md"), os.path.join(sortie_m, "INDEX.md.mien"))
                open(de_jnt, "w").write("à JNT\n")
                os.rename(de_jnt, os.path.join(sortie_m, "INDEX.md"))
        err_m = io.StringIO()
        code = lancer(v_sain, sortie_m, remplacer_au_retrait, err=err_m)
        intact = contenu(os.path.join(sortie_m, "INDEX.md")) == "à JNT\n"
        dit = "REMPLACÉ pendant le nettoyage" in err_m.getvalue()
        prives_m = [n for n in os.listdir(sortie_m) if ".regarder-efface-" in n or ".recupere-" in n]
        if not juger("REMPLACÉ à l'instant du retrait", code == 2 and intact and dit and not prives_m,
                     code, 2, f"fichier de JNT {'à son nom, intact' if intact else 'PERDU ou DÉPLACÉ'}"
                     f"{' · resté sous ' + str(prives_m) if prives_m else ''}",
                     "un fichier de JNT posé à mon nom à l'instant du retrait part, ou reste sous un nom privé."):
            return 1

        # M2. LA FENÊTRE lstat→unlink (8e revue : 1 perte sur 29 essais). Sonde « mis-a-part » :
        #    mon fichier vient d'être renommé, le nom public est LIBRE, un fichier de JNT s'y
        #    pose. Attendu : mon nom privé part, le sien reste (code 2 : `INDEX.md` existe déjà
        #    quand j'écris le mien — O_EXCL). Un `unlink` par nom public l'aurait effacé, code 0.
        sortie_m2 = preparer("garde-fenetre-retrait")
        if sortie_m2 is None:
            return 1

        def glisser_apres_mise_a_part(etape, *info):
            if etape == "mis-a-part" and info and info[0] == "INDEX.md":
                open(os.path.join(sortie_m2, "INDEX.md"), "w").write("à JNT, dans la fenêtre\n")
        code = lancer(v_sain, sortie_m2, glisser_apres_mise_a_part)
        intact = contenu(os.path.join(sortie_m2, "INDEX.md")) == "à JNT, dans la fenêtre\n"
        if not juger("fenêtre lstat→unlink FERMÉE", code == 2 and intact, code, 2,
                     f"fichier de JNT {'intact' if intact else 'EFFACÉ'}",
                     "un fichier de JNT posé à mon nom ENTRE le contrôle et l'unlink est effacé."):
            return 1

        # N. Le REGISTRE lui-même, remplacé à l'instant de SON retrait (sonde « avant-retrait »,
        #    nom `.regarder`). Avant : `unlink(.regarder)` par nom. Attendu : code 2, le `.regarder`
        #    de JNT à son nom, intact.
        sortie_n = preparer("garde-registre-remplace-au-retrait")
        if sortie_n is None:
            return 1

        def remplacer_registre_au_retrait(etape, *info):
            if etape == "avant-retrait" and info and info[0] == MARQUEUR:
                os.rename(os.path.join(sortie_n, MARQUEUR), os.path.join(sortie_n, MARQUEUR + ".mien"))
                open(os.path.join(sortie_n, MARQUEUR), "w").write("notes de JNT\n")
        code = lancer(v_sain, sortie_n, remplacer_registre_au_retrait)
        intact = contenu(os.path.join(sortie_n, MARQUEUR)) == "notes de JNT\n"
        if not juger("registre REMPLACÉ à son retrait", code == 2 and intact, code, 2,
                     f"`.regarder` de JNT {'intact' if intact else 'PERDU'}",
                     "le registre part par un unlink sur son nom public : un fichier de JNT à ce nom part avec."):
            return 1

        # O. TROIS NOMS PRIS + modification par DESCRIPTEUR après mon unlink : à « avant-retrait »,
        #    JNT ouvre mon INDEX.md (descripteur gardé) et pose les deux noms de récupération ;
        #    à « apres-retrait », il y écrit par ce descripteur et recrée `INDEX.md`. Avant : ses
        #    octets mouraient en mémoire (« IMPOSSIBLE à restaurer »). Attendu : code 2, et un
        #    fichier `INDEX.md.regarder-recupere-*` dans le dossier avec ses octets.
        sortie_o = preparer("garde-trois-noms-pris")
        if sortie_o is None:
            return 1
        index_o = os.path.join(sortie_o, "INDEX.md")
        avant_o = contenu(index_o, binaire=True)
        tenus_o = []

        def annoter_par_descripteur(etape, *info):
            if etape == "avant-retrait" and info and info[0] == "INDEX.md":
                tenus_o.append(open(index_o, "ab"))
                open(index_o + ".recupere-par-regarder", "w").write("pris\n")
                open(index_o + f".recupere-{os.getpid()}", "w").write("pris\n")
            if etape == "apres-retrait" and info and info[0] == "INDEX.md":
                tenus_o[0].write(b"annotation de JNT\n")
                tenus_o[0].flush()
                open(index_o, "w").write("le nouveau de JNT\n")
        err_o = io.StringIO()
        code = lancer(v_sain, sortie_o, annoter_par_descripteur, err=err_o)
        for f in tenus_o:
            f.close()
        recuperes = [n for n in os.listdir(sortie_o) if n.startswith("INDEX.md.regarder-recupere-")]
        octets_ok = bool(recuperes) and contenu(os.path.join(sortie_o, recuperes[0]), binaire=True) \
            == (avant_o or b"") + b"annotation de JNT\n"
        autres_ok = (contenu(index_o) == "le nouveau de JNT\n"
                     and contenu(index_o + ".recupere-par-regarder") == "pris\n")
        if not juger("3 noms pris → mkstemp", code == 2 and octets_ok and autres_ok, code, 2,
                     f"{'annotation sauvée sous ' + recuperes[0] if octets_ok else 'annotation PERDUE'}"
                     f"{'' if autres_ok else ' · un fichier de JNT TOUCHÉ'}",
                     "avec trois noms pris, les octets de JNT restent en mémoire et meurent avec le processus."):
            return 1

        # P. Mon DOSSIER PRIVÉ remplacé pendant le run (sonde « fichier-cree » INDEX.md) : le mien
        #    est renommé, un dossier VIDE de JNT prend son chemin. Avant : `os.rmdir(prive)` par
        #    chemin retirait le sien. Attendu : code 0, son dossier toujours là, et je le dis.
        chemin_p = []

        def remplacer_prive(etape, *info):
            if etape == "prive-cree":
                chemin_p.append(info[0])
            if etape == "fichier-cree" and info and info[0] == "INDEX.md" and chemin_p:
                os.rename(chemin_p[0], chemin_p[0] + ".deplace")
                os.mkdir(chemin_p[0])
        err_p = io.StringIO()
        code = lancer(v_sain, os.path.join(tmp, "garde-prive-remplace"), remplacer_prive, err=err_p)
        la = bool(chemin_p) and os.path.isdir(chemin_p[0])
        dit = "n'est plus à" in err_p.getvalue()
        for d in ([chemin_p[0], chemin_p[0] + ".deplace"] if chemin_p else []):
            shutil.rmtree(d, ignore_errors=True)
        if not juger("dossier privé REMPLACÉ", code == 0 and la and dit, code, 0,
                     f"dossier de JNT {'toujours là' if la else 'RETIRÉ'} · {'dit' if dit else 'PAS DIT'}",
                     "un dossier vide de JNT posé au chemin de mon dossier privé est retiré par `rmdir`."):
            return 1

        # Q. Le transcripteur rend code 0 et un JSON de 0 OCTET. Avant : trace d'appel de
        #    `json.loads`, code 1. Attendu : code 2, une ligne, aucune trace.
        err_q = io.StringIO()
        code = lancer(v_sain, os.path.join(tmp, "garde-json-vide"), env={"FAUX_JSON_VIDE_SUR": "audio-1.wav"},
                      err=err_q)
        propre = "Traceback" not in err_q.getvalue() and "JSON illisible" in err_q.getvalue()
        if not juger("JSON de 0 octet", code == 2 and propre, code, 2,
                     "refus en une ligne" if propre else "TRACE D'APPEL ou message absent",
                     "un JSON vide fait planter le run (trace d'appel, code 1) au lieu d'un refus."):
            return 1

        # R. Un FIFO au nom du registre. Avant : `open` bloquait POUR TOUJOURS (>180 s, muet).
        #    Attendu : code 2 en moins de 5 s — mesuré dans un fil, pour que l'autotest ne
        #    bloque pas lui-même si ça régresse.
        sortie_r = os.path.join(tmp, "garde-fifo")
        os.makedirs(sortie_r)
        os.mkfifo(os.path.join(sortie_r, MARQUEUR))
        resultat_r = []
        fil = threading.Thread(target=lambda: resultat_r.append(lancer(v_sain, sortie_r)), daemon=True)
        t0 = time.monotonic()
        fil.start()
        fil.join(5)
        duree_r = time.monotonic() - t0
        code = resultat_r[0] if resultat_r else "BLOQUÉ"
        if not juger("FIFO au nom du registre", code == 2 and duree_r < 5, code, 2,
                     f"{duree_r:.1f} s", "un FIFO au nom du registre bloque le run pour toujours."):
            return 1
        # R2. Un DOSSIER au nom du registre. Avant : `fdopen` plantait (IsADirectoryError, code 1,
        #     trace d'appel) — le dossier de JNT n'était pas touché, mais rien ne le disait.
        sortie_r2 = os.path.join(tmp, "garde-registre-dossier")
        os.makedirs(os.path.join(sortie_r2, MARQUEUR))
        open(os.path.join(sortie_r2, MARQUEUR, "note.txt"), "w").write("note de JNT\n")
        err_r2 = io.StringIO()
        code = lancer(v_sain, sortie_r2, err=err_r2)
        reste_r2 = os.path.isdir(os.path.join(sortie_r2, MARQUEUR)) and \
            contenu(os.path.join(sortie_r2, MARQUEUR, "note.txt")) == "note de JNT\n"
        if not juger("DOSSIER au nom du registre", code == 2 and reste_r2 and "Traceback" not in err_r2.getvalue(),
                     code, 2, "dossier de JNT intact, refus en une ligne" if reste_r2 else "DOSSIER TOUCHÉ",
                     "un dossier `.regarder` fait planter le run (trace d'appel) au lieu d'un refus."):
            return 1

        # S. Une COPIE (`cp -R`) d'une de mes sorties — mêmes octets, même registre, AUTRES inodes.
        #    Avant : nettoyée et réécrite, code 0. Attendu : code 2 « COPIE », rien touché.
        #    Contrôle : un `mv` (mêmes inodes) reste relançable, code 0.
        sortie_s = preparer("garde-copie")
        if sortie_s is None:
            return 1
        copie_s = os.path.join(tmp, "garde-copie-cp-R")
        shutil.copytree(sortie_s, copie_s)
        avant_s = sha(os.path.join(copie_s, "INDEX.md"))
        err_s = io.StringIO()
        code = lancer(v_sain, copie_s, err=err_s)
        intact = sha(os.path.join(copie_s, "INDEX.md")) == avant_s
        dit = "COPIE" in err_s.getvalue()
        deplace_s = os.path.join(tmp, "garde-copie-mv")
        os.rename(sortie_s, deplace_s)
        code_mv = lancer(v_sain, deplace_s)
        if not juger("COPIE d'une sortie refusée, mv accepté", code == 2 and intact and dit and code_mv == 0,
                     f"{code} · mv {code_mv}", "2 · mv 0",
                     f"copie {'intacte' if intact else 'TOUCHÉE'} · {'dite' if dit else 'PAS DITE'}",
                     "une copie d'une de mes sorties passe pour ma sortie : effacée et réécrite."):
            return 1

        # T. J2 — la TOLÉRANCE : réplique à 1,98 s, première image à 2,0 s (20 ms plus tard).
        #    Avant : 0,001 laissait passer 20 ms sans un mot, et l'écart s'écrivait « +0,0 s ».
        #    Attendu : « écran d'APRÈS » ET l'écart en millisecondes.
        sortie_t = os.path.join(tmp, "garde-ecran-d-apres-20ms")
        code = lancer(v_tard, sortie_t, env={"FAUX_DEBUT": "1.98"})
        index_t = contenu(os.path.join(sortie_t, "INDEX.md")) or ""
        dit = "écran d'APRÈS" in index_t and re.search(r"\+[1-9]\d* ms", index_t) is not None
        if not juger("écran d'APRÈS à 20 ms", code == 0 and dit, code, 0,
                     "dit, en ms" if dit else "PAS DIT ou pas en ms",
                     "un écran rendu 20 ms après l'instant visé passe pour exact, ou s'écrit « +0,0 s »."):
            return 1

        # T2. La MÊME avance, mais de 20 µs (11e revue Codex) : l'INDEX écrivait « +0 ms »,
        #     qui se lit « aucune avance » — l'avertissement disait donc le contraire de la mesure.
        sortie_t2 = os.path.join(tmp, "garde-ecran-d-apres-20us")
        code = lancer(v_tard, sortie_t2, env={"FAUX_DEBUT": "1.99998"})
        index_t2 = contenu(os.path.join(sortie_t2, "INDEX.md")) or ""
        dit = "écran d'APRÈS" in index_t2 and re.search(r"\+[1-9]\d* µs", index_t2) is not None
        if not juger("écran d'APRÈS à 20 µs", code == 0 and dit, code, 0,
                     "dit, en µs" if dit else "PAS DIT ou arrondi à zéro",
                     "une avance sous la milliseconde s'écrit « +0 ms » : l'INDEX dit le contraire "
                     "de ce qu'il mesure."):
            return 1

        # U. L'image visée ne se rend pas, la PRÉCÉDENTE la remplace : `frames` doit rendre le
        #    PTS de celle qui a VRAIMENT été rendue (pts[k_]), pas celui visé (pts[k]).
        #    Avant : `return pts[k]` passait les mutants — l'INDEX aurait menti sur l'écart.
        pts_u, _, _ = instants(v_sain)
        k_u = min(5, len(pts_u) - 1)
        vrai_rendre = rendre

        def rendre_sauf_k(video, pts, depart, cles, k):
            if k == k_u:
                return None, "refusé par le test"
            return vrai_rendre(video, pts, depart, cles, k)
        sortie_u = os.path.join(tmp, "garde-pts-rendu")
        os.makedirs(sortie_u)
        bfd_u = tenir(sortie_u)
        globals()["rendre"] = rendre_sauf_k
        err_u = io.StringIO()
        vrai_err = sys.stderr
        sys.stderr = err_u
        try:
            faits_u = frames(v_sain, [pts_u[k_u]], [], bfd_u, os.path.join(sortie_u, "ecrans"))
        finally:
            sys.stderr = vrai_err
            globals()["rendre"] = vrai_rendre
            os.close(bfd_u)
        rendu_u = faits_u[0][2] if faits_u else None
        bon = k_u >= 1 and rendu_u == pts_u[k_u - 1]
        if not juger("PTS rendu = image VRAIMENT rendue", bon, "—", "—",
                     f"visé {pts_u[k_u]:.3f} s · rendu {rendu_u} (attendu {pts_u[k_u - 1]:.3f} s)",
                     "l'INDEX reçoit le PTS visé, pas celui de l'image qui l'a remplacé."):
            return 1

        # V. DEUX pistes actives, le modèle ne rend RIEN sur la 2e. Avant : une ligne sur stdout,
        #    code 0, INDEX muet. Attendu : ⚠️ sur stderr ET une ligne « piste 2 ABSENTE » dans l'INDEX.
        sortie_v = os.path.join(tmp, "garde-piste-absente")
        err_v = io.StringIO()
        code = lancer(v_deux, sortie_v, env={"FAUX_VIDE_SUR": "audio-2.wav"}, err=err_v)
        index_v = contenu(os.path.join(sortie_v, "INDEX.md")) or ""
        dit = "ABSENTE" in err_v.getvalue() and "piste 2 ABSENTE" in index_v
        if not juger("piste active SANS réplique", code == 0 and dit, code, 0,
                     "dite, stderr + INDEX" if dit else "PAS DITE",
                     "une voix que le modèle n'a pas rendue disparaît sans un mot."):
            return 1

        # ── 9e revue Codex (12 sept. 2026) ──
        # W. Un FIFO au nom d'un fichier INSCRIT (INDEX.md). Avant : l'`open` de l'étape 3 du
        #    nettoyage bloquait POUR TOUJOURS (mesuré : tué à 5 s, muet). Attendu : code 2 en
        #    moins de 5 s, le FIFO et le registre toujours là — mesuré dans un fil.
        sortie_w = preparer("garde-fifo-inscrit")
        if sortie_w is None:
            return 1
        index_w = os.path.join(sortie_w, "INDEX.md")
        os.unlink(index_w)
        os.mkfifo(index_w)
        resultat_w = []
        err_w = io.StringIO()
        fil = threading.Thread(target=lambda: resultat_w.append(lancer(v_sain, sortie_w, err=err_w)),
                               daemon=True)
        t0 = time.monotonic()
        fil.start()
        fil.join(5)
        duree_w = time.monotonic() - t0
        code = resultat_w[0] if resultat_w else "BLOQUÉ"
        reste_w = (stat.S_ISFIFO(os.lstat(index_w).st_mode)
                   and os.path.isfile(os.path.join(sortie_w, MARQUEUR)))
        if not juger("FIFO au nom d'un fichier INSCRIT", code == 2 and duree_w < 5 and reste_w, code, 2,
                     f"{duree_w:.1f} s · {'FIFO et registre là' if reste_w else 'TOUCHÉ'}",
                     "un FIFO au nom d'un de mes fichiers bloque le nettoyage pour toujours."):
            return 1

        # X. Un FIFO À MON NOM dans le dossier PRIVÉ : à « wav-cree », mon `audio-1.wav` (que ffmpeg
        #    remplit par descripteur) est renommé et un FIFO prend son nom. Avant : `_ouvrir_prive`
        #    bloquait pour toujours. Attendu : code 2 en moins de 10 s.
        sortie_x = os.path.join(tmp, "garde-fifo-prive")
        prive_x = []

        def fifo_prive(etape, *info):
            if etape == "prive-cree":
                prive_x.append(info[0])
            if etape == "wav-cree" and info and info[0] == "audio-1.wav" and prive_x:
                vrai = os.path.join(prive_x[0], "audio-1.wav")
                os.rename(vrai, vrai + ".vrai")
                os.mkfifo(vrai)
        resultat_x = []
        err_x = io.StringIO()
        fil = threading.Thread(target=lambda: resultat_x.append(lancer(v_sain, sortie_x, fifo_prive, err=err_x)),
                               daemon=True)
        t0 = time.monotonic()
        fil.start()
        fil.join(10)
        duree_x = time.monotonic() - t0
        code = resultat_x[0] if resultat_x else "BLOQUÉ"
        for p in prive_x:                       # `.vrai` empêche le rmdir : je ramasse (nom privé compris)
            parent = os.path.dirname(p)
            for n in os.listdir(parent):
                if n.startswith(os.path.basename(p)):
                    shutil.rmtree(os.path.join(parent, n), ignore_errors=True)
        if not juger("FIFO à mon nom dans le dossier privé", code == 2 and duree_x < 10, code, 2,
                     f"{duree_x:.1f} s", "un FIFO à mon nom dans mon dossier privé bloque le run pour toujours."):
            return 1

        # Y. Le nom PRIVÉ visé : à « mis-a-part », JNT renomme sa note PAR-DESSUS mon nom
        #    `INDEX.md.regarder-efface-*` (il se lit dans un `ls`). Mon inode reste sous `fd`, sans
        #    nom : l'inode collait, l'`unlink` effaçait SA note (mesuré : 24 → 0 octets, code 0).
        #    Attendu : code 2 « REMPLACÉ », sa note à `INDEX.md`, octet pour octet.
        sortie_y = preparer("garde-nom-prive-vise")
        if sortie_y is None:
            return 1
        index_y = os.path.join(sortie_y, "INDEX.md")
        note_y = b"la note de JNT, 24 octets\n"

        def viser_prive(etape, *info):
            if etape == "mis-a-part" and info and info[0] == "INDEX.md":
                prives_y = [n for n in os.listdir(sortie_y) if n.startswith("INDEX.md.regarder-efface-")]
                open(os.path.join(sortie_y, "note.tmp"), "wb").write(note_y)
                os.rename(os.path.join(sortie_y, "note.tmp"), os.path.join(sortie_y, prives_y[0]))
        err_y = io.StringIO()
        code = lancer(v_sain, sortie_y, viser_prive, err=err_y)
        chez_y = contenu(index_y, binaire=True)
        dit = "REMPLACÉ" in err_y.getvalue()
        if not juger("nom privé visé par un rename", code == 2 and chez_y == note_y and dit, code, 2,
                     f"note {'intacte à INDEX.md' if chez_y == note_y else 'PERDUE'} · {'dite' if dit else 'PAS DITE'}",
                     "un rename par-dessus mon nom privé fait effacer le fichier de JNT, inode « vérifié »."):
            return 1

        # Z. Le registre porte le bon inode mais un AUTRE `dev` (mutant m1 de la 9e revue : une
        #    identité qui ne compare que l'inode accepte un fichier d'un autre volume).
        #    Attendu : code 2 « COPIE », INDEX intact.
        sortie_z = preparer("garde-autre-dev")
        if sortie_z is None:
            return 1
        reg_z = os.path.join(sortie_z, MARQUEUR)
        index_z = os.path.join(sortie_z, "INDEX.md")
        avant_z = sha(index_z)

        def autre_dev(ligne):
            m = re.match(rb"^([0-9a-f]{64}) (\d+):(\d+) (.*)$", ligne)
            if not m:
                return ligne
            return b"%s %d:%s %s" % (m.group(1), int(m.group(2)) + 1, m.group(3), m.group(4))
        lignes_z = open(reg_z, "rb").read().split(b"\n")     # lu AVANT le "wb" (qui tronque)
        open(reg_z, "wb").write(b"\n".join(autre_dev(l) for l in lignes_z))
        err_z = io.StringIO()
        code = lancer(v_sain, sortie_z, err=err_z)
        intact = os.path.isfile(index_z) and sha(index_z) == avant_z
        dit = "COPIE" in err_z.getvalue()
        if not juger("registre : même inode, AUTRE dev", code == 2 and intact and dit, code, 2,
                     f"INDEX {'intact' if intact else 'TOUCHÉ'} · {'dite' if dit else 'PAS DITE'}",
                     "une identité qui ne lit que l'inode accepte un fichier d'un autre volume."):
            return 1

        # O2. `_sauver` sous un nom LIBRE (mutant m3 de la 9e revue : un `_sauver` qui écrivait un
        #     fichier VIDE passait le cas O, où c'est `mkstemp` qui sauve). Ici `INDEX.md` reste libre
        #     après mon unlink : l'annotation écrite par descripteur doit y être, octet pour octet.
        sortie_o2 = preparer("garde-sauver-nom-libre")
        if sortie_o2 is None:
            return 1
        index_o2 = os.path.join(sortie_o2, "INDEX.md")
        avant_o2 = contenu(index_o2, binaire=True)
        tenus_o2 = []

        def annoter_nom_libre(etape, *info):
            if etape == "avant-retrait" and info and info[0] == "INDEX.md":
                tenus_o2.append(open(index_o2, "ab"))
            if etape == "apres-retrait" and info and info[0] == "INDEX.md":
                tenus_o2[0].write(b"annotation de JNT\n")
                tenus_o2[0].flush()
        err_o2 = io.StringIO()
        code = lancer(v_sain, sortie_o2, annoter_nom_libre, err=err_o2)
        for f in tenus_o2:
            f.close()
        octets_ok = contenu(index_o2, binaire=True) == (avant_o2 or b"") + b"annotation de JNT\n"
        dit = "restauré" in err_o2.getvalue()
        if not juger("annotation restaurée sous le nom LIBRE", code == 2 and octets_ok and dit, code, 2,
                     f"{'octets à INDEX.md' if octets_ok else 'octets PERDUS ou tronqués'} · {'dit' if dit else 'PAS DIT'}",
                     "sous un nom libre, `_sauver` peut écrire autre chose que les octets de JNT sans être vu."):
            return 1

        # AA. Le nom privé visé par LIEN puis RENAME (10e revue Codex, 12 sept. 2026) : à
        #    « mis-a-part », JNT pose un lien physique vers mon fichier (le compte de noms ne
        #    baisse plus), PUIS renomme sa note par-dessus mon nom privé. Le garde de la 9e revue
        #    comparait les comptes de noms : égaux → l'`unlink` effaçait SA note (24 → 0, code 0).
        #    Attendu : code 2 « REMPLACÉ », sa note à `INDEX.md`, son lien vers le mien intact.
        sortie_aa = preparer("garde-lien-puis-rename")
        if sortie_aa is None:
            return 1
        index_aa = os.path.join(sortie_aa, "INDEX.md")
        alias_aa = os.path.join(sortie_aa, "alias-de-jnt")
        note_aa = b"la note de JNT, 24 octets\n"
        mien_aa = []

        def lier_puis_viser(etape, *info):
            if etape == "mis-a-part" and info and info[0] == "INDEX.md":
                p = [n for n in os.listdir(sortie_aa) if n.startswith("INDEX.md.regarder-efface-")][0]
                os.link(os.path.join(sortie_aa, p), alias_aa)
                mien_aa.append(open(alias_aa, "rb").read())
                open(os.path.join(sortie_aa, "note.tmp"), "wb").write(note_aa)
                os.rename(os.path.join(sortie_aa, "note.tmp"), os.path.join(sortie_aa, p))
        err_aa = io.StringIO()
        code = lancer(v_sain, sortie_aa, lier_puis_viser, err=err_aa)
        chez_aa = contenu(index_aa, binaire=True)
        alias_ok = bool(mien_aa) and contenu(alias_aa, binaire=True) == mien_aa[0]
        dit = "REMPLACÉ" in err_aa.getvalue()
        if not juger("nom privé visé par LIEN puis rename", code == 2 and chez_aa == note_aa and alias_ok and dit,
                     code, 2, f"note {'intacte à INDEX.md' if chez_aa == note_aa else 'PERDUE'} · "
                     f"lien {'intact' if alias_ok else 'PERDU'} · {'dit' if dit else 'PAS DIT'}",
                     "un lien physique masque le rename par-dessus mon nom privé : la note de JNT part, code 0."):
            return 1

        # AB. CONTRÔLE du même garde : le lien SEUL (rien renommé par-dessus) ne doit PAS refuser —
        #    ce qui est sous mon nom privé est encore mon inode. Attendu : code 0, le lien de JNT
        #    garde mes octets, l'INDEX retiré.
        sortie_ab = preparer("garde-lien-seul")
        if sortie_ab is None:
            return 1
        alias_ab = os.path.join(sortie_ab, "alias-de-jnt")
        mien_ab = []

        def lier_seulement(etape, *info):
            if etape == "mis-a-part" and info and info[0] == "INDEX.md":
                p = [n for n in os.listdir(sortie_ab) if n.startswith("INDEX.md.regarder-efface-")][0]
                os.link(os.path.join(sortie_ab, p), alias_ab)
                mien_ab.append(open(alias_ab, "rb").read())
        code = lancer(v_sain, sortie_ab, lier_seulement)
        alias_ok = bool(mien_ab) and contenu(alias_ab, binaire=True) == mien_ab[0]
        if not juger("lien seul sur mon nom privé (contrôle)", code == 0 and alias_ok, code, 0,
                     f"lien {'intact' if alias_ok else 'PERDU'}",
                     "le garde d'identité refuse un run sain dès qu'un lien existe : il ne mesure pas ce qu'il dit."):
            return 1

        # AC. JSON VALIDE mais pas de la forme attendue (10e revue) : `{}`, un segment SANS
        #    `debut`, `fin` null, `debut` en chaîne, booléen, NaN, `texte` non chaîne, pas un objet.
        #    Avant : `json.loads` passait, KeyError/TypeError plus loin — trace, code 1 ; `{}` passait
        #    pour une piste sans parole. Attendu : code 2 « JSON illisible », une ligne, aucune trace.
        formes = ('{}', '[{"fin": 1, "texte": "x"}]', '[{"debut": 0, "fin": null, "texte": "x"}]',
                  '[{"debut": "0", "fin": 1, "texte": "x"}]', '[{"debut": 0, "fin": true, "texte": "x"}]',
                  '[{"debut": NaN, "fin": 1, "texte": "x"}]', '[{"debut": 0, "fin": 1, "texte": 3}]', '[1]',
                  # ⛔ 11e revue Codex (12 sept. 2026) : HORS BORNES et TROP PROFOND. `math.isfinite`
                  #    laissait passer 1e308 — puis `fin / 0,1` valait l'infini dans `segments_muets`
                  #    (OverflowError) ; il LEVAIT lui-même sur un entier de 400 chiffres ; et 3 000
                  #    crochets imbriqués faisaient lever `json.loads` (RecursionError). Trace
                  #    d'appel et code 1 dans les trois cas, là où un refus tient en une ligne.
                  '[{"debut": 0, "fin": 1e308, "texte": "x"}]',
                  '[{"debut": ' + "9" * 400 + ', "fin": 1, "texte": "x"}]',
                  '[{"debut": -0.2, "fin": 1, "texte": "x"}]',
                  # ⛔ 12e revue Codex (13 sept. 2026) : un surrogat isolé passait la forme puis
                  #    faisait lever `UnicodeEncodeError` à l'écriture de l'INDEX (trace, code 1,
                  #    aucune sortie) ; un `texte` ABSENT passait pour une réplique vide (code 5) ;
                  #    et rien ne tenait le plafond de secondes à sa valeur.
                  '[{"debut": 0, "fin": 1, "texte": "\\ud800"}]',
                  '[{"debut": 0, "fin": 1}]',
                  '[{"debut": 0, "fin": 1000000001, "texte": "x"}]',
                  "[" * 3000 + "]" * 3000)
        for i, forme in enumerate(formes):
            err_ac = io.StringIO()
            code = lancer(v_sain, os.path.join(tmp, f"garde-json-forme-{i}"),
                          env={"FAUX_JSON_FORME_SUR": "audio-1.wav", "FAUX_JSON_FORME": forme}, err=err_ac)
            propre = "Traceback" not in err_ac.getvalue() and "JSON illisible" in err_ac.getvalue()
            if not juger(f"JSON de forme {forme[:24]}", code == 2 and propre, code, 2,
                         "refus en une ligne" if propre else "TRACE D'APPEL ou message absent",
                         "un JSON valide mais mal formé plante le run (trace, code 1) au lieu d'un refus."):
                return 1

        # AD. Le transcripteur rend code 0 et son JSON, mais PAS le `.txt` (10e revue). Avant :
        #    FileNotFoundError en le relisant — trace, code 1. Attendu : code 2, une ligne.
        err_ad = io.StringIO()
        code = lancer(v_sain, os.path.join(tmp, "garde-sans-txt"), env={"FAUX_SANS_TXT_SUR": "audio-1.wav"},
                      err=err_ad)
        propre = "Traceback" not in err_ad.getvalue() and "sans écrire" in err_ad.getvalue()
        if not juger("JSON présent, .txt ABSENT", code == 2 and propre, code, 2,
                     "refus en une ligne" if propre else "TRACE D'APPEL ou message absent",
                     "un .txt manquant plante le run (trace, code 1) au lieu d'un refus."):
            return 1

        # AE. JSON aux bornes ENTIÈRES (11e revue Codex, 12 sept. 2026) : `debut` et `fin`
        #     sont des entiers JSON, pas des flottants. C'est le CONTRÔLE du garde de forme —
        #     un garde qui n'accepterait que `float` jetterait une vraie transcription, et le
        #     mutant qui le fait passait vert. Attendu : code 0, la réplique dans l'INDEX.
        sortie_ae = os.path.join(tmp, "garde-json-entiers")
        code = lancer(v_sain, sortie_ae, env={"FAUX_JSON_FORME_SUR": "audio-1.wav",
                                              "FAUX_JSON_FORME": '[{"debut": 0, "fin": 1, "texte": "aux entiers"}]'})
        dedans = "aux entiers" in (contenu(os.path.join(sortie_ae, "INDEX.md")) or "")
        sortie_ae2 = os.path.join(tmp, "garde-json-plafond-pile")
        code2 = lancer(v_sain, sortie_ae2, env={"FAUX_JSON_FORME_SUR": "audio-1.wav",
                                                "FAUX_JSON_FORME": '[{"debut": 0, "fin": 1000000000, "texte": "au plafond pile"}]'})
        dedans = dedans and code2 == 0 and "au plafond pile" in (contenu(os.path.join(sortie_ae2, "INDEX.md")) or "")
        if not juger("JSON aux bornes ENTIÈRES (contrôle)", code == 0 and dedans, code, 0,
                     "réplique dans l'INDEX" if dedans else "RÉPLIQUE PERDUE",
                     "le garde de forme refuse un `debut` entier : une vraie transcription est jetée."):
            return 1

        # AF. MODIFIÉ *puis* REMPLACÉ (11e revue, repli Claude) : JNT annote mon fichier par un
        #     descripteur ouvert AVANT, et sa note prend la place de mon nom privé. La v13 rendait
        #     sa note à `INDEX.md` (bien), mais MON inode annoté n'avait plus de nom et mourait à
        #     la fermeture du descripteur — 782 octets de JNT perdus, sous un message qui disait
        #     « il reste tel quel ». Attendu : code 2, sa note à `INDEX.md`, ET les octets annotés
        #     retrouvés quelque part dans le dossier.
        sortie_af = preparer("garde-modifie-puis-remplace")
        if sortie_af is None:
            return 1
        index_af = os.path.join(sortie_af, "INDEX.md")
        avant_af = contenu(index_af, binaire=True) or b""
        note_af = b"la note de JNT, 24 octets\n"
        tenus_af = []

        def annoter_puis_remplacer(etape, *info):
            if etape == "avant-retrait" and info and info[0] == "INDEX.md":
                tenus_af.append(open(index_af, "ab"))
            elif etape == "mis-a-part" and info and info[0] == "INDEX.md":
                tenus_af[0].write(b"annotation de JNT\n")
                tenus_af[0].flush()
                p = [n for n in os.listdir(sortie_af) if n.startswith("INDEX.md.regarder-efface-")][0]
                open(os.path.join(sortie_af, "note.tmp"), "wb").write(note_af)
                os.rename(os.path.join(sortie_af, "note.tmp"), os.path.join(sortie_af, p))
        err_af = io.StringIO()
        code = lancer(v_sain, sortie_af, annoter_puis_remplacer, err=err_af)
        for f in tenus_af:
            f.close()
        annote_af = avant_af + b"annotation de JNT\n"
        retrouve = any(contenu(os.path.join(sortie_af, n), binaire=True) == annote_af
                       for n in os.listdir(sortie_af))
        chez_af = contenu(index_af, binaire=True)
        dit = "REMPLACÉ" in err_af.getvalue()
        if not juger("MODIFIÉ puis REMPLACÉ : les deux survivent",
                     code == 2 and chez_af == note_af and retrouve and dit, code, 2,
                     f"note {'intacte' if chez_af == note_af else 'PERDUE'} · "
                     f"annotation {'restaurée' if retrouve else 'PERDUE'} · {'dit' if dit else 'PAS DIT'}",
                     "les octets qu'un descripteur a écrits dans mon inode meurent avec lui pendant "
                     "que le message dit qu'ils restent."):
            return 1

        # AG. L'identité sous le nom privé se relit APRÈS l'empreinte (11e revue Codex) : à la
        #     sonde « empreinte-relue » — donc après `_sha_fd`, qui relit TOUT le fichier — sa note
        #     est renommée par-dessus mon nom privé. Une identité lue plus tôt serait PÉRIMÉE et
        #     l'`unlink` emporterait sa note (mesuré sur le mutant : 24 → 0 octets, code 0).
        #     Attendu : code 2 « REMPLACÉ », sa note à `INDEX.md`.
        sortie_ag = preparer("garde-vise-apres-empreinte")
        if sortie_ag is None:
            return 1
        index_ag = os.path.join(sortie_ag, "INDEX.md")
        note_ag = b"la note de JNT, 24 octets\n"

        def viser_apres_empreinte(etape, *info):
            if etape == "empreinte-relue" and info and info[0] == "INDEX.md":
                p = [n for n in os.listdir(sortie_ag) if n.startswith("INDEX.md.regarder-efface-")][0]
                open(os.path.join(sortie_ag, "note.tmp"), "wb").write(note_ag)
                os.rename(os.path.join(sortie_ag, "note.tmp"), os.path.join(sortie_ag, p))
        err_ag = io.StringIO()
        code = lancer(v_sain, sortie_ag, viser_apres_empreinte, err=err_ag)
        chez_ag = contenu(index_ag, binaire=True)
        dit = "REMPLACÉ" in err_ag.getvalue()
        if not juger("nom privé visé APRÈS l'empreinte", code == 2 and chez_ag == note_ag and dit,
                     code, 2, f"note {'intacte à INDEX.md' if chez_ag == note_ag else 'PERDUE'} · "
                     f"{'dit' if dit else 'PAS DIT'}",
                     "l'identité du nom privé est lue avant l'empreinte : elle est périmée à l'`unlink`."):
            return 1

        # AH. `_sauver` quand PLUS RIEN n'est inscriptible (11e revue Codex) : l'annotation arrive
        #     après l'`unlink`, et le dossier de sortie ET le dossier temporaire passent en lecture
        #     seule. Avant : `_Altere` remontait jusqu'en haut — trace d'appel, code 1, octets
        #     perdus sans un mot. Attendu : le dossier PERSONNEL les reçoit (3e destination),
        #     code 2 ; et quand lui non plus n'accepte rien, un refus en une ligne, jamais une trace.
        for maison_ouverte in (True, False):
            nom_ah = "garde-sauver-" + ("chez-moi" if maison_ouverte else "nulle-part")
            sortie_ah = preparer(nom_ah)
            if sortie_ah is None:
                return 1
            index_ah = os.path.join(sortie_ah, "INDEX.md")
            avant_ah = contenu(index_ah, binaire=True) or b""
            maison = os.path.join(tmp, "maison-" + nom_ah)
            refuge = os.path.join(tmp, "refuge-" + nom_ah)
            os.makedirs(maison)
            os.makedirs(refuge)
            tenus_ah = []

            def fermer_les_portes(etape, *info):
                if etape == "avant-retrait" and info and info[0] == "INDEX.md":
                    tenus_ah.append(open(index_ah, "ab"))
                elif etape == "apres-retrait" and info and info[0] == "INDEX.md":
                    tenus_ah[0].write(b"annotation de JNT\n")
                    tenus_ah[0].flush()
                    os.chmod(sortie_ah, 0o500)
                    os.chmod(refuge, 0o500)
                    if not maison_ouverte:
                        os.chmod(maison, 0o500)
            vrai_tmpdir, tempfile.tempdir = tempfile.tempdir, refuge
            vrai_maison = os.environ.get("HOME")
            os.environ["HOME"] = maison
            err_ah = io.StringIO()
            try:
                code = lancer(v_sain, sortie_ah, fermer_les_portes, err=err_ah)
            finally:
                tempfile.tempdir = vrai_tmpdir
                if vrai_maison is None:
                    del os.environ["HOME"]
                else:
                    os.environ["HOME"] = vrai_maison
                for d in (sortie_ah, refuge, maison):
                    os.chmod(d, 0o755)
                for f in tenus_ah:
                    f.close()
            annote_ah = avant_ah + b"annotation de JNT\n"
            chez_moi = [n for n in os.listdir(maison)
                        if contenu(os.path.join(maison, n), binaire=True) == annote_ah]
            propre = "Traceback" not in err_ah.getvalue()
            bon = code == 2 and propre and bool(chez_moi) == maison_ouverte
            if not juger("plus rien d'inscriptible : " + ("dossier personnel" if maison_ouverte
                                                          else "refus en une ligne"),
                         bon, code, 2,
                         f"{'octets chez moi' if chez_moi else 'octets PERDUS'} · "
                         f"{'une ligne' if propre else 'TRACE D APPEL'}",
                         "quand aucune destination n'accepte les octets de JNT, le refus devient une "
                         "trace d'appel (code 1) et personne ne sait ce qui est parti."):
                return 1

        # AI. Les TROIS images visées refusées par ffmpeg (11e revue Codex) : la réplique reçoit
        #     l'écran le plus PROCHE, code 0 — et l'INDEX n'en disait rien (l'avertissement ne vit
        #     que sur stderr). Celui qui lit l'artefact voit un écran d'un autre moment sans le
        #     savoir : « ce bouton-là » désigne le mauvais bouton. Attendu : l'INDEX le dit.
        sortie_ai = os.path.join(tmp, "garde-repli-ecran")
        pts_ai, _, _ = instants(v_sain)
        k_ai = max(0, bisect.bisect_right(pts_ai, 0.5 + 1e-6) - 1)
        vrai_rendre_ai = rendre

        def rendre_refuse(video, pts, depart, cles, k):
            if k in (k_ai, k_ai - 1, k_ai - 2):
                return None, "refusé par le test"
            return vrai_rendre_ai(video, pts, depart, cles, k)
        err_ai = io.StringIO()
        globals()["rendre"] = rendre_refuse
        try:
            code = lancer(v_sain, sortie_ai, env={"FAUX_DEBUT": "0.5"}, err=err_ai)
        finally:
            globals()["rendre"] = vrai_rendre_ai
        index_ai = contenu(os.path.join(sortie_ai, "INDEX.md")) or ""
        dit = "AUCUNE image RENDUE" in index_ai
        if not juger("les 3 images visées refusées", code == 0 and dit, code, 0,
                     "l'INDEX le dit" if dit else "INDEX MUET",
                     "la réplique prend l'écran d'un autre moment et l'INDEX n'en dit rien."):
            return 1

        # AJ. L'annotation qui arrive APRÈS la première empreinte (12e revue Codex, 13 sept.
        #     2026) : à « empreinte-relue », JNT écrit dans mon fichier par un descripteur ouvert
        #     AVANT, puis renomme sa note par-dessus mon nom privé. L'empreinte avait déjà été
        #     lue (égale), donc on passait par `remplace` — qui rendait sa note (24/24) et
        #     laissait mourir son annotation : **24 → 0 octet**, sous un message qui ne la
        #     nommait même pas. Attendu : code 2, sa note à `INDEX.md`, ET les octets annotés
        #     restaurés et NOMMÉS dans le message.
        sortie_aj = preparer("garde-annote-apres-empreinte")
        if sortie_aj is None:
            return 1
        index_aj = os.path.join(sortie_aj, "INDEX.md")
        avant_aj = contenu(index_aj, binaire=True) or b""
        note_aj = b"la note de JNT, 24 octets\n"
        tenus_aj = []

        def annoter_apres_empreinte(etape, *info):
            if etape == "avant-retrait" and info and info[0] == "INDEX.md":
                tenus_aj.append(open(index_aj, "ab"))
            elif etape == "empreinte-relue" and info and info[0] == "INDEX.md":
                tenus_aj[0].write(b"annotation de JNT\n")
                tenus_aj[0].flush()
                p = [n for n in os.listdir(sortie_aj) if n.startswith("INDEX.md.regarder-efface-")][0]
                open(os.path.join(sortie_aj, "note.tmp"), "wb").write(note_aj)
                os.rename(os.path.join(sortie_aj, "note.tmp"), os.path.join(sortie_aj, p))
        err_aj = io.StringIO()
        code = lancer(v_sain, sortie_aj, annoter_apres_empreinte, err=err_aj)
        for f in tenus_aj:
            f.close()
        annote_aj = avant_aj + b"annotation de JNT\n"
        garde_aj = [n for n in os.listdir(sortie_aj)
                    if contenu(os.path.join(sortie_aj, n), binaire=True) == annote_aj]
        chez_aj = contenu(index_aj, binaire=True)
        dit = bool(garde_aj) and garde_aj[0] in err_aj.getvalue() and "MODIFIÉS" in err_aj.getvalue()
        if not juger("annotée APRÈS l'empreinte, puis remplacée",
                     code == 2 and chez_aj == note_aj and dit, code, 2,
                     f"note {'intacte' if chez_aj == note_aj else 'PERDUE'} · "
                     f"annotation {'restaurée et nommée' if dit else 'PERDUE ou PAS NOMMÉE'}",
                     "l'annotation écrite après la première empreinte meurt avec mon descripteur, "
                     "et le message ne la nomme même pas."):
            return 1

        # AK. Le repli d'écran quand la réplique PARTAGE son écran avec la précédente (12e revue
        #     Codex) : la ligne « ↳ écran » ne s'écrivait pas — donc l'avertissement non plus, et
        #     l'artefact redevenait muet. Deux répliques (0,2 s et 0,5 s), les trois images de la
        #     seconde refusées. Attendu : code 0, DEUX lignes « ↳ écran » et l'avertissement.
        sortie_ak = os.path.join(tmp, "garde-repli-ecran-partage")
        pts_ak, _, _ = instants(v_sain)
        k_ak = max(0, bisect.bisect_right(pts_ak, 0.5 + 1e-6) - 1)
        vrai_rendre_ak = rendre

        def rendre_refuse_ak(video, pts, depart, cles, k):
            if k in (k_ak, k_ak - 1, k_ak - 2):
                return None, "refusé par le test"
            return vrai_rendre_ak(video, pts, depart, cles, k)
        err_ak = io.StringIO()
        globals()["rendre"] = rendre_refuse_ak
        try:
            code = lancer(v_sain, sortie_ak, err=err_ak,
                          env={"FAUX_JSON_FORME_SUR": "audio-1.wav",
                               "FAUX_JSON_FORME": '[{"debut": 0.2, "fin": 0.4, "texte": "un"}, '
                                                  '{"debut": 0.5, "fin": 0.7, "texte": "deux"}]'})
        finally:
            globals()["rendre"] = vrai_rendre_ak
        index_ak = contenu(os.path.join(sortie_ak, "INDEX.md")) or ""
        deux = index_ak.count("↳ écran") == 2 and "AUCUNE image RENDUE" in index_ak
        if not juger("repli sur l'écran DÉJÀ montré", code == 0 and deux, code, 0,
                     "les deux lignes, et l'avertissement" if deux else "LIGNE AVALÉE par le dédoublonnage",
                     "une réplique qui partage l'écran de la précédente perd son avertissement de repli."):
            return 1

        # AL. Le transcripteur écrit un octet NON DÉCODABLE (0xff) sur stderr (12e revue Codex) :
        #     `text=True` le décodait en UTF-8 strict AVANT même qu'on regarde son code de retour —
        #     `UnicodeDecodeError`, trace d'appel, code 1, aucun INDEX. Attendu : code 2 en UNE
        #     ligne quand il plante, et code 0 avec son INDEX quand il réussit malgré son bruit.
        err_al = io.StringIO()
        code = lancer(v_sain, os.path.join(tmp, "garde-bruit-illisible"),
                      env={"FAUX_BRUIT_SUR": "audio-1.wav", "FAUX_PLANTE": "1"}, err=err_al)
        refus = [l for l in err_al.getvalue().splitlines() if l.startswith("⛔")]
        propre = ("Traceback" not in err_al.getvalue() and len(refus) == 1
                  and "bruit" in refus[0] and "deuxieme ligne" in refus[0])
        sortie_al2 = os.path.join(tmp, "garde-bruit-mais-bon")
        code2 = lancer(v_sain, sortie_al2, env={"FAUX_BRUIT_SUR": "audio-1.wav"})
        marche = code2 == 0 and contenu(os.path.join(sortie_al2, "INDEX.md")) is not None
        if not juger("stderr NON DÉCODABLE du transcripteur", code == 2 and propre and marche,
                     f"{code} · sain {code2}", "2 · sain 0",
                     f"{'refus en une ligne' if propre else 'TRACE ou message éclaté'} · "
                     f"{'run sain intact' if marche else 'RUN SAIN CASSÉ'}",
                     "un octet illisible sur stderr fait planter le run avant même qu'on lise le "
                     "code de retour du transcripteur."):
            return 1

        # AN. Ce qui est DÉPOSÉ est ce qui a été VALIDÉ (12e revue Codex) : le JSON était relu une
        #     3e fois pour être copié. Tronqué entre les deux lectures, l'INDEX se bâtissait sur
        #     40 octets et la preuve brute déposée en faisait 0 — code 0, stderr vide. Le banc
        #     tronque le JSON privé à TOUTE ouverture après celle qui a validé : s'il n'y en a
        #     plus, le fichier déposé est intact. Attendu : code 0 et les octets VALIDÉS déposés.
        sortie_an = os.path.join(tmp, "garde-json-depose")
        forme_an = '[{"debut": 0.2, "fin": 1.0, "texte": "les memes octets"}]'
        vrai_ouvrir_an = _ouvrir_prive
        vus_an = []

        def ouvrir_puis_tronquer(pfd_, nom_, prives_, attendu=None):
            fd_ = vrai_ouvrir_an(pfd_, nom_, prives_, attendu)
            if nom_.endswith(".json"):
                vus_an.append(nom_)
                if len(vus_an) >= 3:
                    os.close(os.open(nom_, os.O_WRONLY | os.O_TRUNC, dir_fd=pfd_))
            return fd_
        globals()["_ouvrir_prive"] = ouvrir_puis_tronquer
        try:
            code = lancer(v_sain, sortie_an, env={"FAUX_JSON_FORME_SUR": "audio-1.wav",
                                                  "FAUX_JSON_FORME": forme_an})
        finally:
            globals()["_ouvrir_prive"] = vrai_ouvrir_an
        depose = contenu(os.path.join(sortie_an, "transcript-piste-1.json"))
        if not juger("le JSON déposé est celui qui a été validé", code == 0 and depose == forme_an,
                     code, 0, f"{len(depose or '')} octets déposés (attendu {len(forme_an)})",
                     "la preuve brute déposée n'est pas celle qui a bâti l'INDEX : relue, donc "
                     "remplaçable entre les deux."):
            return 1

        # AO. LE CODE 8 — un transcript obtenu, ZÉRO écran rendu (trouvé par Kimi, 20 sept. 2026).
        #     ⛔ LE TROU EXACT : le code 8 est né CE JOUR-LÀ et `grep "attendu 8"` rendait VIDE.
        #     Un garde que rien n'exerce se retire sans bruit — c'est la règle nº 1 de la
        #     maison, et elle était violée par le garde le plus récent du fichier. Un renommage
        #     de variable dans ce chemin rendrait une trace Python au lieu du refus, et
        #     l'autotest resterait 7/7.
        #     ⭐ ON SIMULE LA CAUSE QUE LE MESSAGE NOMME (« piste vidéo illisible ? ffmpeg trop
        #     vieux ? ») : `rendre` échoue sur TOUTE image, comme quand le décodeur ne rend rien.
        #     Attendu : code 8, ET l'INDEX écrit quand même — c'est la PREUVE qu'on laisse
        #     derrière, et le seul refus du fichier qui écrit avant de refuser, volontairement.
        #     ⚠️ Il vérifie AUSSI l'avertissement par réplique : sans écran, « ce bouton-LÀ »
        #     ne se résout pas, et l'INDEX doit le DIRE ligne par ligne au lieu de se taire.
        sortie_8 = os.path.join(tmp, "garde-code-8")
        vrai_rendre = rendre
        globals()["rendre"] = lambda *a, **k: (None, "banc : piste vidéo illisible")
        try:
            code = lancer(v_sain, sortie_8)
        finally:
            globals()["rendre"] = vrai_rendre
        index_8 = contenu(os.path.join(sortie_8, "INDEX.md")) or ""
        ecrans_8 = os.path.join(sortie_8, "ecrans")
        restes_8 = [n for n in (os.listdir(ecrans_8) if os.path.isdir(ecrans_8) else []) if n.endswith(".jpg")]
        if not juger("code 8 : zéro écran, INDEX écrit quand même",
                     code == 8 and "AUCUN ÉCRAN" in index_8 and not restes_8,
                     code, 8,
                     f"{len(index_8)} octets d'INDEX · {len(restes_8)} image(s) · "
                     f"avertissement par réplique {'présent' if 'AUCUN ÉCRAN' in index_8 else 'ABSENT'}",
                     "un rapport SANS LA MOITIÉ IMAGE se rend comme un rapport réussi : c'est "
                     "exactement le succès silencieux que cet outil existe pour empêcher."):
            return 1

        print("\n✅ LES REFUS MORDENT, aucun ne touche à un octet avant de dire non, et mon dossier "
              "ne perd que MES fichiers — inscrits, donc relançable")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def autotest_hallucination():
    """LE MARQUEUR 🚫 INVENTÉE MORD-IL ENCORE — SUR UN VRAI SOUFFLE DE MICRO ?

    ⛔ On ne demande pas à Whisper d'halluciner sur commande : il le fait quand il veut,
      et un test qui dépend de son humeur est un test qui clignote. On fabrique donc le
      SON (3 s de parole · 20 s de souffle faible à -63 dBFS · 3 s de parole FAIBLE, vers
      -35 dBFS · 20 s de souffle faible · 12 s de souffle de micro à -43 dBFS · 3 s de
      silence numérique) et on lui présente des répliques PLACÉES : une sur chaque parole,
      une sur chaque souffle, une sur le silence. Le garde doit marquer les trois du
      souffle et du silence, jamais les deux paroles. Le souffle à -43 dBFS est LE cas qui
      rendait le garde à seuil fixe aveugle ; le souffle qui CHANGE au milieu, celui qui
      rendait le garde à plancher GLOBAL aveugle (revue Codex, 12 sept. 2026 : 6 sur 9
      acceptées) ; ⭐ la parole FAIBLE, celle qui distingue une médiane d'un `max` — avec
      un `max`, le plancher monte jusqu'à la voix elle-même, et une vraie phrase dite bas
      est marquée inventée (2e revue Codex, même jour : ce mutant passait l'autotest).
    """
    if not shutil.which("say"):
        print("⚪ NON REJOUÉ — `say` absent (macOS requis)"); return 3
    tmp = tempfile.mkdtemp(prefix="regarder-hallu-")
    try:
        aiff = _voix(tmp, "p", "Regarde le bouton orange en haut.")
        aiff2 = _voix(tmp, "q", "Le bouton bleu doit devenir vert.")
        wav = os.path.join(tmp, "banc.wav")
        # parole (0-3 s) → souffle FAIBLE -63 dBFS (3-23 s) → parole FAIBLE ~-35 dBFS (23-26 s)
        # → souffle faible (26-46 s) → souffle -43 dBFS (46-58 s) → silence numérique (58-61 s).
        # ⛔ Le souffle qui CHANGE au milieu est le cas de la revue Codex du 12 sept. : avec
        #    un plancher lu sur le fichier entier, le passage calme fixait le seuil, et les
        #    hallucinations du passage bruyant passaient pour dites. ⚠️ Le passage calme
        #    doit DOMINER (40 s contre 12) : sinon même une médiane GLOBALE tombe juste, et
        #    la mutation « plancher global » passait l'autotest — vu le 12 sept.
        # ⚠️ `say` rend ~1,8 s, pas 3 : `apad=whole_dur=3` cale chaque zone à la seconde près,
        #    sinon toutes les zones glissent et une réplique « sur le silence » tombe HORS du
        #    fichier (vu le 12 sept. : segment 4 non marqué parce que sa tranche était vide).
        # ⭐ La parole FAIBLE (volume ÷ 60, vers -36 dBFS) tombe entre le plancher + 8 et le plafond -30 :
        #    une médiane la garde, un `max` la marque. C'est ce qui rend le mutant rouge.
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", aiff, "-i", aiff2,
                        "-f", "lavfi", "-i", "anoisesrc=colour=white:amplitude=0.0007:r=16000:seed=1",
                        "-f", "lavfi", "-i", "anoisesrc=colour=white:amplitude=0.007:r=16000:seed=2",
                        "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
                        "-filter_complex",
                        "[0:a]atrim=0:3,apad=whole_dur=3,asetpts=N/SR/TB,aformat=sample_rates=16000:channel_layouts=mono[a];"
                        "[2:a]atrim=0:20,asetpts=N/SR/TB,aformat=sample_rates=16000:channel_layouts=mono[b];"
                        "[1:a]atrim=0:3,apad=whole_dur=3,asetpts=N/SR/TB,volume=0.017,aformat=sample_rates=16000:channel_layouts=mono[f];"
                        "[2:a]atrim=20:40,asetpts=N/SR/TB,aformat=sample_rates=16000:channel_layouts=mono[g];"
                        "[3:a]atrim=0:12,asetpts=N/SR/TB,aformat=sample_rates=16000:channel_layouts=mono[c];"
                        "[4:a]atrim=0:3,asetpts=N/SR/TB,aformat=sample_rates=16000:channel_layouts=mono[d];"
                        "[a][b][f][g][c][d]concat=n=6:v=0:a=1[out]",
                        "-map", "[out]", "-ac", "1", "-ar", "16000", wav], check=True)
        segs = [{"debut": 0.2, "fin": 2.8, "texte": "Regarde le bouton orange en haut."},
                {"debut": 7.0, "fin": 9.0, "texte": "Merci."},
                {"debut": 23.2, "fin": 25.8, "texte": "Le bouton bleu doit devenir vert."},
                {"debut": 50.0, "fin": 52.0, "texte": "Merci."},
                {"debut": 58.8, "fin": 60.5, "texte": "Merci."}]
        pics = pics_par_fenetre(wav)
        res = segments_muets(pics, segs)
        if not res:
            print("🔴 CASSÉ — amplitude non mesurable sur un WAV que je viens d'écrire"); return 1
        muets, p_min, p_max = res
        val, fen = pics
        crete_faible = max(val[int(23.2 / fen):int(25.8 / fen) + 1])
        # ⛔ Le banc se contrôle lui-même : si la parole faible n'est pas ENTRE plancher + 8 et
        #    le plafond, elle ne distingue plus rien, et le vert ne prouverait rien.
        if not (-63.0 + SEUIL_DESSUS_PLANCHER_DB + 3.0 < crete_faible < PLAFOND_MUET_DBFS - 2.0):
            print(f"🔴 BANC INVALIDE — la parole faible culmine à {crete_faible:.1f} dB, hors de la "
                  f"fenêtre qui sépare une médiane d'un max"); return 1
        print(f"   planchers locaux {p_min:.1f}…{p_max:.1f} dB · parole faible à {crete_faible:.1f} dB · "
              f"marquées : {sorted(muets)} (attendu [1, 3, 4] : souffle faible, souffle fort, silence)")
        if muets != {1, 3, 4}:
            print("\n🔴 CASSÉ — le marqueur INVENTÉE ne distingue plus la parole du souffle "
                  "de micro : Whisper pourra de nouveau me faire lire des phrases inventées.")
            return 1
        print("\n✅ LE MARQUEUR INVENTÉE MORD sur le souffle ET sur le silence, pas sur la parole")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def autotest_pistes():
    """DEUX VOIX EN MÊME TEMPS, SUR DEUX PISTES : LES DEUX REVIENNENT-ELLES ?

    ⛔ Le cas réel : le site joue une vidéo (piste système) pendant que JNT dit sa consigne
      (piste micro, plus faible). Mélangées, Whisper ne gardait que la plus forte, et la
      consigne disparaissait SANS ERREUR. On fabrique exactement ça — la piste 2 à -18 dB
      sous la piste 1, en même temps — et on exige les mots de CHAQUE piste, avec
      l'étiquette de la bonne piste.
    """
    if not shutil.which("say"):
        print("⚪ NON REJOUÉ — `say` absent (macOS requis)"); return 3
    tmp = tempfile.mkdtemp(prefix="regarder-pistes-")
    try:
        systeme = _voix(tmp, "sys", "Bienvenue sur notre site, découvrez nos services "
                                    "de rénovation résidentielle et commerciale.", "Thomas")
        micro = _voix(tmp, "mic", "Le logo en haut est trop petit, agrandis-le.", "Amélie")
        video = os.path.join(tmp, "deux-pistes.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=320x180:rate=10", "-i", systeme, "-i", micro,
                        "-filter_complex", "[2:a]volume=-18dB[m]",
                        "-map", "0:v", "-map", "1:a", "-map", "[m]", "-t", "7",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", video], check=True)
        base = os.path.join(tmp, "regard")
        construire(video, "fr", 4, base)
        lignes = open(os.path.join(base, "transcript.txt")).read().lower().splitlines()
        p1 = " ".join(l for l in lignes if "(piste 1)" in l)
        p2 = " ".join(l for l in lignes if "(piste 2)" in l)
        print("   piste 1 :", p1[:100]); print("   piste 2 :", p2[:100])
        if "rénovation" not in p1 and "renovation" not in p1:
            print("\n🔴 CASSÉ — la piste 1 (système) n'est pas revenue"); return 1
        if "logo" not in p2:
            print("\n🔴 CASSÉ — la consigne de JNT sur la piste 2 (micro, -18 dB, en même "
                  "temps) a DISPARU : c'est exactement le défaut du mélange."); return 1
        print("\n✅ LES DEUX VOIX REVIENNENT, chacune sur sa piste")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def autotest_debut():
    """UNE RÉPLIQUE QUI SUIT UN SILENCE COMMENCE-T-ELLE QUAND LA VOIX COMMENCE ?

    ⛔ Trouvé le 14 sept. 2026 sur un faux screen record de trois consignes : sans
      `word_timestamps=True` dans `transcrire()`, Whisper date le début d'un segment sur sa
      FENÊTRE de 30 s, pas sur la voix. « Dans le pied de page… », dit à 32,4 s après 8 s de
      silence, était daté 30,0 s — et l'INDEX y attachait l'écran de la section d'AVANT,
      avec un horodatage qui avait l'air juste. Les 5 autres phases passaient avec et sans.
      On rejoue exactement ce banc et on exige un début à moins de 0,8 s de la vraie voix.
    """
    if not shutil.which("say"):
        print("⚪ NON REJOUÉ — `say` absent (macOS requis)"); return 3
    tmp = tempfile.mkdtemp(prefix="regarder-debut-")
    try:
        phrases = [
            "Bon, sur la page d'accueil, le bouton Demander une soumission en haut à droite "
            "est trop petit. Agrandis-le et mets-le orange.",
            "Ensuite dans la section des services, la photo de la toiture est floue, "
            "remplace-la par celle du chantier de Laval.",
            "Pis finalement dans le pied de page, le numéro de téléphone est pas le bon. "
            "C'est le quatre cinq zéro, cinq cinq cinq, douze trente-quatre."]
        wavs = []
        for i, ph in enumerate(phrases):
            w = os.path.join(tmp, f"p{i}.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", _voix(tmp, f"p{i}", ph, "Amélie"),
                            "-ar", "48000", "-ac", "1", w], check=True)
            wavs.append(w)
        blanc = os.path.join(tmp, "blanc.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                        "anullsrc=r=48000:cl=mono", "-t", "4", blanc], check=True)
        ordre = [blanc, wavs[0], blanc, blanc, wavs[1], blanc, blanc, wavs[2], blanc]
        with open(os.path.join(tmp, "liste.txt"), "w") as f:
            f.writelines(f"file '{w}'\n" for w in ordre)
        audio = os.path.join(tmp, "audio.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                        "-i", os.path.join(tmp, "liste.txt"), audio], check=True)
        duree = lambda p: float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
            capture_output=True, text=True, check=True).stdout)
        vraie = sum(duree(w) for w in ordre[:7])          # instant où la 3e voix part
        video = os.path.join(tmp, "trois-consignes.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=320x180:rate=10", "-i", audio, "-shortest",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", video], check=True)
        base = os.path.join(tmp, "regard")
        construire(video, "fr", 8, base)
        segs = json.load(open(os.path.join(base, "transcript-piste-1.json")))
        pied = [s for s in segs if "pied" in s["texte"].lower()]
        if not pied:
            print("\n🔴 CASSÉ — la consigne « pied de page » n'est pas revenue du son"); return 1
        ecart = pied[0]["debut"] - vraie
        print(f"   voix à {vraie:.2f} s · réplique datée {pied[0]['debut']:.2f} s · écart {ecart:+.2f} s")
        if abs(ecart) > 0.8:
            print("\n🔴 CASSÉ — le début de la réplique n'est pas celui de la voix : l'écran "
                  "attaché est celui d'un AUTRE moment. `word_timestamps=True` a-t-il sauté "
                  "de `transcrire()` ?"); return 1
        print("\n✅ LA RÉPLIQUE COMMENCE AVEC LA VOIX, pas avec la fenêtre de 30 s")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def essai_langue(video, secondes):
    """Les N premières secondes, transcrites en FR et en EN, côte à côte.

    ⛔ CE QU'IL RÈGLE : `--langue` ne se devine pas, et se tromper ne rate pas
       bruyamment — Whisper rend un texte plausible et faux, avec des horodatages
       corrects. La seule façon de trancher est de LIRE les deux et de choisir.
    ⚠️ Il n'écrit AUCUN index et ne touche pas au dossier de sortie : c'est une sonde,
       pas un run. Tout vit dans un dossier temporaire qu'il efface lui-même.
    """
    tmp = tempfile.mkdtemp(prefix="regarder-langue-")
    try:
        wav = os.path.join(tmp, "essai.wav")
        r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-t", str(secondes),
                            "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav],
                           capture_output=True)
        if r.returncode != 0 or not os.path.exists(wav) or os.path.getsize(wav) < 1000:
            # ⛔ Un essai de langue qui échoue DOIT refuser : rendre « aucun texte » pour
            #    les deux langues se lirait « la vidéo est muette », et on choisirait une
            #    langue au hasard sur cette fausse lecture.
            sortir(3, "aucun son extractible de cette vidéo — l'essai de langue ne peut "
                      "rien trancher.\n   " +
                      " ".join((r.stderr or b"").decode(errors="replace").split())[:300])
        print(f"🎧 {secondes:.0f} premières secondes, transcrites dans LES DEUX langues.")
        print("⛔ Aucune des deux n'est « la bonne » d'office : c'est TOI qui lis et qui "
              "tranches.\n")
        casse = 0
        for langue in ("fr", "en"):
            txt = os.path.join(tmp, f"essai-{langue}.txt")
            t = subprocess.run([sys.executable, TRANSCRIRE, wav, txt, "--langue", langue],
                               capture_output=True)
            print(f"── --langue {langue} " + "─" * 55)
            if t.returncode != 0 or not os.path.exists(txt):
                dit = " ".join(((t.stderr or t.stdout) or b"").decode(errors="replace").split())
                print(f"   🔴 échec (code {t.returncode}) : {dit[:300]}")
                casse = 1
                continue
            # ⛔ TROUVÉ PAR KIMI (20 sept. 2026) : CE CHEMIN RENDAIT UN TRANSCRIPT SANS
            #    JAMAIS DIRE QUI L'AVAIT FAIT. Le marqueur `MOTEUR-VOIX[…]` partait bien
            #    dans stderr — capturé ici, puis JETÉ. Le chemin principal nomme son moteur
            #    à l'écran ET dans l'INDEX ; cette sonde-ci, non. ⭐ C'est la MÊME famille de
            #    défaut que tout le reste du fichier combat : une dégradation NON DITE.
            #    ⚠️ Et elle compte : on tranche une LANGUE là-dessus, et les deux moteurs
            #    n'entendent pas pareil un passage limite.
            m = re.search(r"MOTEUR-VOIX\[([^\]]{1,120})\]",
                          " ".join((t.stderr or b"").decode(errors="replace").split()))
            qui = m.group(1).strip() if m else "moteur inconnu — il ne l'a pas dit"
            print(f"   (transcrit par {qui})")
            texte = io.open(txt, encoding="utf-8", errors="replace").read().strip()
            print("   " + (texte.replace("\n", "\n   ") if texte else
                           "⚠️ AUCUN TEXTE — ce n'est PAS une preuve que la langue est "
                           "mauvaise : ça peut être un passage sans parole."))
            print()
        print("👉 La bonne langue est celle qui rend des MOTS, pas du son transcrit de "
              "travers.\n   Relancer ensuite sans `--essai-langue`, avec `--langue <la "
              "bonne>`.")
        return casse
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def preflight():
    """Ce que la machine doit avoir AVANT qu'on touche à la vidéo. Code 7.

    ⛔ LE TROU QU'IL BOUCHE, MESURÉ LE 20 SEPTEMBRE 2026 en simulant une machine neuve
       (paquet public, `HOME` factice, `PATH` sans Homebrew) : sans `ffprobe`, l'outil
       mourait sur une TRACE PYTHON de 12 lignes finissant par
       `FileNotFoundError: [Errno 2] ... 'ffprobe'`. Techniquement un échec — mais
       illisible, et surtout impossible à distinguer d'un vrai défaut de l'outil pour
       qui vient de l'installer. Un nouvel arrivant conclut « ça marche pas », pas
       « il me manque ffmpeg ».

    ⭐ POURQUOI UN CODE À PART (7) ET PAS LE 2. Le 2 dit « ta commande ou ton dossier
       ne va pas » — on corrige la COMMANDE. Le 7 dit « la MACHINE n'est pas équipée »
       — on lance l'installeur. Les fondre ferait chercher au mauvais endroit, ce qui
       est exactement le genre de temps perdu que cet outil existe pour éviter.

    ⚠️ Il ne vérifie QUE la présence, jamais que ça marche : `mlx-whisper` présent mais
       sans puce graphique visible (bac à sable Codex) passe ici et échoue plus loin,
       bruyamment. Une présence n'est pas une preuve — c'est `--autotest` qui tranche.
    """
    manque = [b for b in ("ffmpeg", "ffprobe") if shutil.which(b) is None]
    if manque:
        sortir(7, "il manque " + " et ".join(manque) + " sur cette machine.\n"
                  "   macOS  : brew install ffmpeg\n"
                  "   Linux  : sudo apt install ffmpeg\n"
                  "   (ou lancer l'installeur du paquet : ./installer.sh)")


def main():
    # ⛔ WINDOWS NATIF : REFUS PROPRE, PAS UNE TRACE (trouvé par Kimi, 20 sept. 2026).
    #    L'INSTALLEUR refusait déjà en nommant WSL2 — mais le README invite à lancer le
    #    script DIRECTEMENT, et là il n'y avait AUCUNE détection : `dir_fd`, `O_NOFOLLOW`,
    #    `preexec_fn` et `pass_fds` (60 occurrences sur 19 fonctions, compté par Kimi)
    #    n'existent pas sous Windows, et la première d'entre elles mourait sur un
    #    `NotImplementedError` brut. ⭐ Une trace Python se lit « cet outil est cassé »,
    #    jamais « ta plateforme n'est pas supportée, voici quoi faire ».
    if os.name == "nt":
        sortir(7, "Windows NATIF n'est pas supporté, et ce n'est pas le moteur de voix qui "
                  "bloque : c'est la couche d'écriture sûre (dir_fd, O_NOFOLLOW, "
                  "preexec_fn), qui n'a pas d'équivalent Windows.\n"
                  "   👉 WSL2 le fait tourner tel quel, avec le moteur processeur :\n"
                  "      1. PowerShell en administrateur : `wsl --install`\n"
                  "      2. redémarrer, ouvrir « Ubuntu », puis y relancer l'installeur.")
    p = argparse.ArgumentParser()
    p.add_argument("video", nargs="?")
    p.add_argument("--langue", default="fr")
    p.add_argument("--images", type=int, default=36)
    p.add_argument("--sortie", default=None)
    p.add_argument("--autotest", action="store_true")
    # ⛔ TROUVÉ PAR KIMI LE 20 SEPT. 2026 : LA PROCÉDURE ÉTAIT ÉCRITE, PAS EXÉCUTABLE.
    #    `SKILL.md` et le README disaient tous deux « dans le doute, transcrire 90 s dans
    #    les DEUX langues » — et aucun drapeau ne le permettait. Il fallait appeler
    #    `transcrire-fichier.py` à la main, ce qu'aucun des deux documents n'expliquait.
    #    ⭐ Une consigne non exécutable ne se lit pas comme absente : elle se lit comme
    #    faite. On coche « j'ai vérifié la langue » sans l'avoir vérifiée — et forcer la
    #    mauvaise langue ne rate pas bruyamment, Whisper rend un texte PLAUSIBLE ET FAUX,
    #    horodatages corrects, sur lequel la modification du client se bâtit.
    p.add_argument("--essai-langue", nargs="?", type=float, const=90.0, default=None,
                   metavar="SECONDES",
                   help="transcrit les N premières secondes en fr ET en en, côte à côte, "
                        "puis s'arrête (aucun INDEX). Défaut : 90 s.")
    a = p.parse_args()

    preflight()

    if a.autotest:
        phases = [("LE SON : une phrase indevinable doit revenir", autotest),
                  ("L'ALIGNEMENT : l'écran de [mm:ss] est-il celui de [mm:ss] ?", autotest_alignement),
                  ("LES REFUS : disent-ils encore non, sans rien écraser ?", autotest_refus),
                  ("L'HALLUCINATION : le souffle de micro est-il marqué INVENTÉE ?", autotest_hallucination),
                  ("LES PISTES : deux voix en même temps, les deux reviennent ?", autotest_pistes),
                  ("LE DÉBUT : une réplique après un silence part-elle avec la voix ?", autotest_debut),
                  ("LE 2e MOTEUR : celui que cette machine n'utilise pas marche-t-il ?", autotest_second_moteur)]
        codes = []
        for i, (titre, fn) in enumerate(phases, 1):
            print(f"\n── {i}/{len(phases)} · {titre} ──")
            codes.append(fn())
        # ⛔ TROIS ISSUES, JAMAIS DEUX (20 sept. 2026). `if c` était vrai pour 1 ET pour
        #    3 : une phase NON REJOUÉE (voix absente, `say` absent) s'affichait
        #    « 🔴 AUTOTEST CASSÉ ». C'est un FAUX ROUGE — et un faux rouge coûte aussi
        #    cher qu'un faux vert : on cesse de lire le garde. ⚠️ Le code de sortie,
        #    lui, était déjà juste : c'est l'AFFICHAGE qui mentait, donc ce que l'humain
        #    lit. Les deux doivent dire la même chose.
        casses = [f"{i}" for i, c in enumerate(codes, 1) if c == 1]
        sautees = [f"{i}" for i, c in enumerate(codes, 1) if c == 3]
        if casses:
            verdict = "🔴 AUTOTEST CASSÉ — phase(s) " + ", ".join(casses)
            if sautees:
                verdict += " · ⚪ non rejouée(s) : " + ", ".join(sautees)
        elif sautees:
            verdict = ("⚪ AUTOTEST NON CONCLUANT — phase(s) " + ", ".join(sautees) +
                       " n'ont PAS pu être rejouées (rien n'est cassé, rien n'est prouvé "
                       "non plus : il manque de quoi sur cette machine)")
        else:
            verdict = f"✅ AUTOTEST — {len(phases)}/{len(phases)} phases passées"
        print(f"\n{verdict}")
        # 1 = une phase a vu l'outil CASSÉ · 3 = rien de cassé, mais une phase n'a pas pu
        # être rejouée (`say` absent) — et un 3 ne cache jamais un 1.
        sys.exit(1 if 1 in codes else (3 if 3 in codes else 0))
    if not a.video:
        sortir(2, "il faut un fichier vidéo (ou --autotest).")

    # ⛔ UNE URL N'ARRIVE PAS ICI PAR ERREUR — ELLE ARRIVE PARCE QUE L'AIGUILLAGE A
    #    ÉCHOUÉ (20 sept. 2026). Cet outil ne télécharge rien, et c'est voulu : il est
    #    fait pour un fichier qu'on a déjà, avec une voix dessus. Mais le laisser dire
    #    « introuvable : https://… » envoie chercher un problème de CHEMIN, alors que
    #    la vraie question est « quel outil pour cette vidéo-là ». Un message qui fait
    #    chercher au mauvais endroit coûte plus cher que pas de message du tout.
    #    ⚠️ ET LE PIÈGE EST DANS LES DEUX SENS : un screen record hébergé (Loom, Drive,
    #    un envoi WeTransfer) passé à `/watch` revient EN IMAGES SEULES, sans erreur,
    #    parce qu'il n'a aucun sous-titre natif. On télécharge d'abord, on regarde après.
    if re.match(r"^(https?|ftp)://", a.video.strip(), re.I):
        sortir(2, "c'est une URL, et cet outil ne télécharge rien (voulu).\n"
                  "   · VIDÉO EN LIGNE à ANALYSER (montage, rythme, hook) → le skill `/watch`\n"
                  "     (claude-watch) : il avale les URL et lit les sous-titres natifs.\n"
                  "   · SCREEN RECORD HÉBERGÉ (Loom, Drive, WeTransfer) où quelqu'un PARLE →\n"
                  "     ⛔ surtout pas `/watch` : sans sous-titres, il rend les images EN\n"
                  "     SILENCE. Télécharger d'abord, puis relancer ici :\n"
                  "         yt-dlp -o ~/Downloads/video.mp4 \"<URL>\"\n"
                  "         python3 " + os.path.abspath(__file__) + " ~/Downloads/video.mp4")

    video = os.path.abspath(os.path.expanduser(a.video))
    if not os.path.exists(video):
        sortir(2, f"introuvable : {video}")

    if a.essai_langue is not None:
        sys.exit(essai_langue(video, a.essai_langue))

    slug = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(video))[0].lower())
    base = a.sortie or os.path.join(CACHE, slug.strip("-"))
    construire(video, a.langue, a.images, base)   # ⛔ c'est `construire` qui efface, APRÈS ses refus


if __name__ == "__main__":
    main()
