#!/usr/bin/env python3
"""
TRANSCRIPTION — la voix, en local, sur la puce graphique. Aucune clé API.

⛔ CE FICHIER EST EXTRAIT AUTOMATIQUEMENT, IL NE SE MODIFIE PAS À LA MAIN.
   Il est découpé de `ghl-appel.py` par le script de publication du dépôt source
   (qui ne fait PAS partie de ce paquet). Une correction se fait dans la source, puis
   on relance ce script. Édité ici, le changement est perdu à la prochaine sync — et
   pire, les deux versions marchent toutes les deux en disant des choses
   différentes, ce qui ne se remarque jamais.

DEUX MOTEURS, et il DIT lequel il a pris (ligne `MOTEUR-VOIX:` sur stderr) :
  · `mlx-whisper`     — puce graphique, Mac Apple Silicon. Le plus rapide.
  · `faster-whisper`  — processeur : Mac Intel, Linux, WSL2. Partout, plus lent.
⛔ Le repli n'est JAMAIS silencieux : un moteur qui change sans le dire, c'est le défaut
   qu'on combat sous un autre nom (deux moteurs, ni la même vitesse ni la même sortie,
   et un transcript qui ne porte aucune trace de ce qui l'a produit).

Il demande aussi `ffmpeg`.
"""
import os, subprocess, sys

_MODELE = "mlx-community/whisper-large-v3-turbo"


def transcrire(wav, sortie_txt, langue="fr", detail_json=None):
    """mlx-whisper, avec horodatage par ligne. Rend le nombre de segments.

    ⭐ `detail_json` (12 sept. 2026, AJOUT PUREMENT ADDITIF — rien ne change sans lui) :
      écrit à côté un JSON avec, par segment, `debut`/`fin` EN FLOTTANT (le .txt tronque
      à la seconde), le texte, et les `no_speech_prob` / `avg_logprob` du modèle.
      C'est ce que `regarder.py` consomme pour attacher l'écran de la bonne fraction de
      seconde à chaque réplique, et pour fusionner plusieurs pistes dans l'ordre du temps.
      ⛔ CE QUE `no_speech_prob` NE FAIT PAS : détecter les hallucinations. On l'a cru
      en l'ajoutant, et on l'a MESURÉ le 12 sept. 2026 sur 9 « Merci. » inventés par
      Whisper sur 290 s de silence : **0,000 sur chacun**, identique aux vraies
      répliques. Le modèle ne sait pas qu'il invente. Il reste dans le JSON pour qu'on
      puisse le revérifier un jour, pas parce qu'il sert. L'hallucination se détecte à
      l'amplitude, contre le plancher de bruit du fichier — voir `regarder.segments_muets`.

    ⛔ LA LANGUE NE SE DEVINE PAS, ELLE SE DONNE. Forcer « fr » sur un appel anglais
      ne rate PAS bruyamment : Whisper rend du français plausible et faux, ligne après
      ligne, avec des horodatages corrects. Rien dans la sortie ne signale l'erreur, et
      l'offre se bâtit sur une transcription inventée. Vu le 14 août 2026 sur un appel 100 % anglais. Défaut inchangé à « fr » : les appels en français ne bougent pas.
    """
    seize = os.path.splitext(wav)[0] + "-16k.wav"
    # 16 kHz mono : c'est ce que le modèle consomme, et ça évite qu'il rééchantillonne lui-même.
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-ac", "1", "-ar", "16000", seize],
                       check=True)
        return _transcrire_seize(seize, sortie_txt, langue, detail_json)
    finally:
        # ⚠️ Sans `finally`, un MLX qui plante (« No Metal device available » dans le bac à
        #   sable de Codex, 14 sept. 2026) laissait le WAV 16 kHz derrière lui. ffmpeg est
        #   DANS le `try` (il peut écrire un bout de fichier puis échouer), et un refus de
        #   suppression est avalé : il ne doit jamais REMPLACER l'erreur d'origine (revue Codex).
        try:
            os.remove(seize)
        except OSError:
            pass


# ⛔⛔ DEUX MOTEURS, ET LE MOTEUR SE NOMME — JAMAIS ON NE LE SUPPOSE (20 sept. 2026).
#    JNT : « est-ce qu'il y aurait moyen que même les ordis Intel ou les PC Windows
#    puissent l'utiliser ? ». `mlx` ne tourne que sur la puce graphique d'un Mac Apple
#    Silicon. `faster-whisper` (CTranslate2) tourne sur le PROCESSEUR, donc partout.
#    ⭐ MAIS UN REPLI SILENCIEUX EST LE DÉFAUT QU'ON COMBAT, SOUS UN AUTRE NOM. Un
#    moteur qui change sans le dire, c'est la leçon payée le 11 sept. sur `relecteur.sh` :
#    la revue sortait, elle était bonne, et rien ne disait QUI l'avait écrite — on croyait
#    avoir deux avis indépendants avec le même cerveau. Ici ce serait pire : les deux
#    moteurs n'ont ni la même vitesse ni exactement la même sortie, et un transcript ne
#    porte aucune trace de ce qui l'a produit. **Donc le moteur retenu est IMPRIMÉ, et il
#    remonte jusque dans l'INDEX.**
#    ⚠️ L'ordre n'est pas un goût : mlx d'abord parce qu'il est ~10× plus rapide sur la
#    machine où il tourne. Le repli n'est jamais « aussi bon », il est « disponible ».
_MOTEURS = ("mlx-whisper (puce graphique Apple)", "faster-whisper (processeur, toutes plateformes)")


def moteur_voix():
    """Lequel des deux est installé ? Rend (clé, nom lisible) — ou lève.

    ⭐ `REGARDER_MOTEUR=cpu|mlx` FORCE le choix. Ça existe pour UNE raison : sans ça,
       le 2e moteur n'est JAMAIS exercé sur la machine qui a le 1er — donc jamais
       prouvé, donc du code multiplateforme qui n'a jamais tourné. C'est exactement
       comme ça qu'un vestige `import mlx_whisper` a survécu dans l'installeur et tué
       Mac Intel, Linux et WSL2 sans que rien ici ne puisse le voir (20 sept. 2026).
    ⚠️ Forcer un moteur ABSENT doit échouer BRUYAMMENT, jamais retomber en silence sur
       l'autre : un repli non demandé rendrait le test vert sans avoir rien testé.
    """
    force = (os.environ.get("REGARDER_MOTEUR") or "").strip().lower()
    if force in ("cpu", "faster", "faster-whisper"):
        import faster_whisper  # noqa: F401  (l'ImportError remonte : voulu)
        return "cpu", _MOTEURS[1]
    if force in ("mlx", "mlx-whisper"):
        import mlx_whisper  # noqa: F401
        return "mlx", _MOTEURS[0]
    if force:
        raise ImportError(f"REGARDER_MOTEUR={force!r} n'est pas un moteur connu "
                          "(valeurs : cpu, mlx)")
    try:
        import mlx_whisper  # noqa: F401
        return "mlx", _MOTEURS[0]
    except ImportError:
        pass
    try:
        import faster_whisper  # noqa: F401
        return "cpu", _MOTEURS[1]
    except ImportError:
        raise ImportError(
            "aucun moteur de voix installé. Lancer l'installeur du paquet.\n"
            "   · Mac Apple Silicon : mlx-whisper\n"
            "   · Mac Intel, Linux, WSL2 : faster-whisper")


# Le modèle CPU : même famille, format CTranslate2 (mlx ne lit pas ce format, et
# l'inverse non plus — chacun télécharge le sien, une fois).
_MODELE_CPU = "deepdml/faster-whisper-large-v3-turbo-ct2"


def _transcrire_cpu(seize, langue):
    """faster-whisper, rendu dans EXACTEMENT la forme que rend mlx.

    ⛔ La forme est un CONTRAT : `regarder.py` lit `debut`, `fin`, `texte`,
       `prob_sans_parole` et `logprob_moyen`. Un repli qui rend une forme voisine
       casserait le marqueur INVENTÉE en silence — et le marqueur est ce qui empêche
       de lire une phrase fabriquée comme une vraie.
    """
    from faster_whisper import WhisperModel
    m = WhisperModel(_MODELE_CPU, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(seize, language=langue, word_timestamps=True)
    return [{"start": s.start, "end": s.end, "text": s.text,
             "no_speech_prob": s.no_speech_prob, "avg_logprob": s.avg_logprob}
            for s in segs]


def _transcrire_seize(seize, sortie_txt, langue, detail_json):
    cle, nom = moteur_voix()
    # ⭐ La ligne qui empêche le repli silencieux. Elle part sur stderr : `regarder.py`
    #    la relaie à l'écran ET dans l'INDEX, pour que l'artefact dise avec quoi il a
    #    été fait, des jours plus tard, quand plus personne ne s'en souvient.
    # ⚠️ BORNÉ PAR DES CROCHETS, et ce n'est pas cosmétique : `regarder.py` aplatit tout
    #    le stderr du transcripteur sur UNE ligne (les sauts de ligne disparaissent), et
    #    les barres de progression de Hugging Face s'y déversent. Sans borne de fin, le
    #    nom du moteur avalait 200 caractères de « Fetching 4 files: 100%|███… » jusque
    #    DANS l'INDEX. Mesuré. Une borne de début sans borne de fin n'est pas une borne.
    print(f"MOTEUR-VOIX[{nom}]", file=sys.stderr)
    if cle == "cpu":
        segments = _transcrire_cpu(seize, langue)
        return _ecrire_segments(segments, sortie_txt, detail_json)
    import mlx_whisper
    # ⛔ `word_timestamps=True` N'EST PAS UN LUXE (14 sept. 2026). Sans lui, le début d'un
    #   segment est calé sur la FENÊTRE de 30 s du modèle, pas sur la voix : sur un faux
    #   screen record, « dans le pied de page… » dit à 32,1 s était daté 30,0 s, et
    #   `regarder.py` y attachait l'écran de la section d'AVANT. Avec lui : 32,1 s, bon
    #   écran, même texte, +0,5 s de calcul sur 44 s. Mesuré aussi : `whisper-large-v3`
    #   complet, 17× plus lent et PAS meilleur (« Agrandis l'émail orange »).
    r = mlx_whisper.transcribe(seize, path_or_hf_repo=_MODELE, language=langue, verbose=False,
                               word_timestamps=True)
    segments = r.get("segments", [])
    return _ecrire_segments(segments, sortie_txt, detail_json)


def _ecrire_segments(segments, sortie_txt, detail_json):
    """Le rendu, commun aux DEUX moteurs — écrit une seule fois, donc jamais divergent."""
    with open(sortie_txt, "w") as f:
        for s in segments:
            minutes, secondes = divmod(int(s["start"]), 60)
            f.write(f"[{minutes:02d}:{secondes:02d}] {s['text'].strip()}\n")
    if detail_json:
        import json as _json
        with open(detail_json, "w") as f:
            _json.dump([{"debut": s.get("start"), "fin": s.get("end"),
                         "texte": (s.get("text") or "").strip(),
                         "prob_sans_parole": s.get("no_speech_prob"),
                         "logprob_moyen": s.get("avg_logprob")} for s in segments],
                       f, ensure_ascii=False, indent=1)
    return len(segments)
