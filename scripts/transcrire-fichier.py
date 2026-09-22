#!/usr/bin/env python3
"""
TRANSCRIRE-FICHIER — le pont entre `regarder.py` et le moteur de voix local.

`regarder.py` l'appelle en sous-processus (pas en import) pour une raison : le moteur
vit dans un environnement Python à lui (`~/.venvs/transcription`), et ce fichier s'y
RELANCE tout seul à la première ligne. Sans ça, il faudrait installer `mlx-whisper`
dans le Python du système — ce qu'on ne veut pas imposer.

⛔⛔ `--langue` NE SE DEVINE PAS, ET IL EST OBLIGATOIRE. Forcer la mauvaise langue ne
   rate pas bruyamment : Whisper rend un texte PLAUSIBLE ET FAUX, avec des horodatages
   corrects, et la demande de modification se bâtit dessus. Prouvé le 3 septembre 2026 :
   en `en`, la traduction inventait « top-up » là où le français disait « Residential
   Services ». Rien dans la sortie ne signale l'erreur.
   👉 Le drapeau se prouve en transcrivant 90 s dans les DEUX langues avant d'exploiter
   le texte — c'est à ça que servent `--debut` / `--duree`.

── USAGE ───────────────────────────────────────────────────────────────────────
  python3 transcrire-fichier.py <audio> <sortie.txt> --langue fr
  python3 transcrire-fichier.py <audio> sonde-fr.txt --langue fr --debut 0 --duree 90
"""
import argparse, os, subprocess, sys

_VENV = os.path.expanduser("~/.venvs/transcription")
if os.path.exists(os.path.join(_VENV, "bin", "python")) and sys.prefix != _VENV:
    _py = os.path.join(_VENV, "bin", "python")
    os.execv(_py, [_py, os.path.abspath(__file__)] + sys.argv[1:])

p = argparse.ArgumentParser()
p.add_argument("audio"); p.add_argument("sortie")
p.add_argument("--langue", required=True)
p.add_argument("--debut", default=None); p.add_argument("--duree", default=None)
p.add_argument("--detail-json", default=None,
               help="JSON par segment : debut/fin en flottant, no_speech_prob, avg_logprob")
a = p.parse_args()

src = a.audio
if a.debut is not None or a.duree is not None:
    src = a.sortie + "-extrait.wav"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if a.debut: cmd += ["-ss", a.debut]
    cmd += ["-i", a.audio]
    if a.duree: cmd += ["-t", a.duree]
    cmd += [src]
    subprocess.run(cmd, check=True)

_ICI = os.path.dirname(os.path.abspath(__file__))
# ⛔ Le chemin ABSOLU, pas « ./installer.sh ». Mesuré le 20 sept. 2026 : le message
#    relatif suppose que la personne est dans le dossier du paquet — or elle vient
#    de lancer l'outil depuis son projet, et « ./installer.sh » n'y existe pas.
#    Un message d'erreur qu'on ne peut pas suivre vaut un message absent.
_INSTALLEUR = os.path.join(os.path.dirname(_ICI), "installer.sh")

sys.path.insert(0, _ICI)
try:
    import transcription
except ImportError as e:  # pragma: no cover
    sys.exit(f"🔴 moteur de voix introuvable ({e}).\n   Lancer : {_INSTALLEUR}")

try:
    n = transcription.transcrire(src, a.sortie, a.langue, detail_json=a.detail_json)
# ⛔ `ImportError`, PAS `ModuleNotFoundError` (corrigé le 20 sept. 2026, trouvé par une
#    revue aveugle). `ModuleNotFoundError` est une SOUS-CLASSE : quand AUCUN des deux
#    moteurs n'est installé, `moteur_voix()` lève un `ImportError` nu qui passait à côté
#    de ce filet. Résultat mesuré : une trace Python brute, que `regarder.py` tronque
#    ensuite à 400 caractères — l'utilisateur ne voyait JAMAIS « lancer l'installeur ».
#    ⭐ Attraper la sous-classe au lieu de la classe, c'est un filet troué : il attrape
#    le cas courant et laisse passer le cas total, qui est le plus grave des deux.
except ImportError as e:
    manquant = getattr(e, "name", None) or "le moteur de voix"
    sys.exit(f"🔴 `{manquant}` n'est pas installé dans {_VENV}.\n"
             f"   {e}\n"
             f"   Lancer : {_INSTALLEUR}")
finally:
    if src != a.audio:
        try: os.remove(src)
        except OSError: pass

print(f"{n} segments → {a.sortie}")
