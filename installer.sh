#!/usr/bin/env bash
# INSTALLER — ffmpeg + le moteur de voix local. Une fois, puis plus jamais.
#
# Ce que ça met sur la machine :
#   · ffmpeg / ffprobe      (Homebrew) — découpe l'écran et le son
#   · ~/.venvs/transcription — un Python à part, avec `mlx-whisper` dedans
#
# ⭐⭐ DEUX MOTEURS DEPUIS LE 20 SEPT. 2026 — l'installeur CHOISIT, il ne refuse plus :
#    · Mac Apple Silicon (M1+)  → `mlx-whisper`, sur la puce graphique. Le plus rapide.
#    · Mac Intel, Linux, WSL2   → `faster-whisper`, sur le processeur. Partout, plus lent.
#    Les deux sont gratuits, hors ligne, sans aucune clé API.
# ⛔ Windows NATIF reste refusé, et ce n'est pas le moteur qui bloque : `regarder.py`
#    tient ses garanties d'écriture avec 49 appels POSIX (`dir_fd`, `O_NOFOLLOW`,
#    `O_DIRECTORY`…) qui n'existent pas sur Windows. Les réécrire voudrait dire livrer
#    des gardes JAMAIS PROUVÉS — exactement ce que cet outil existe pour éviter.
#    👉 WSL2 est la réponse, et c'en est une vraie : c'est du Linux, donc la voie
#       `faster-whisper` ci-dessous, sans une ligne de code en moins.
set -euo pipefail

echo "── 1/3 · la machine ──────────────────────────────────────────────"
SYS="$(uname -s)"
case "$SYS" in
  MINGW*|MSYS*|CYGWIN*|Windows_NT)
    echo "🔴 REFUS : Windows natif."
    echo "   Ce n'est PAS le moteur de voix — c'est que les gardes d'écriture de"
    echo "   l'outil (49 appels POSIX) n'existent pas sur Windows. Les remplacer"
    echo "   par des gardes non testés serait pire que ce refus."
    echo "   👉 LA SOLUTION, et elle marche à 100 % : WSL2 (Windows Subsystem for"
    echo "      Linux). Dans PowerShell, en admin :"
    echo "          wsl --install"
    echo "      puis, dans le terminal Ubuntu qui s'ouvre, relancer cet installeur."
    exit 2 ;;
esac
MOTEUR=""
if [ "$SYS" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
  MOTEUR="mlx-whisper"
  echo "   ✅ macOS $(sw_vers -productVersion), Apple Silicon ($(uname -m))"
  echo "      → moteur mlx-whisper (puce graphique) — le plus rapide"
elif [ "$SYS" = "Darwin" ]; then
  MOTEUR="faster-whisper"
  echo "   ✅ macOS $(sw_vers -productVersion), Intel ($(uname -m))"
  echo "      → moteur faster-whisper (processeur) — plus lent, mais complet"
elif [ "$SYS" = "Linux" ]; then
  MOTEUR="faster-whisper"
  grep -qi microsoft /proc/version 2>/dev/null \
    && echo "   ✅ Linux sous WSL2 ($(uname -m))" \
    || echo "   ✅ Linux ($(uname -m))"
  echo "      → moteur faster-whisper (processeur)"
else
  echo "🔴 REFUS : système non reconnu ($SYS $(uname -m))."
  echo "   Rien n'a été installé — mieux vaut ce refus qu'un outil qui rend"
  echo "   les images sans le son, ce qui se lit comme un succès."
  exit 2
fi

echo "── 2/3 · ffmpeg ──────────────────────────────────────────────────"
if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  echo "   ✅ déjà là : $(ffmpeg -version | head -1 | cut -c1-40)"
else
  # ⛔ Homebrew n'existe pas sur Linux : chercher brew là-bas et refuser faute de
  #    l'avoir trouvé enverrait installer le MAUVAIS outil. Chaque système a le sien.
  if [ "$SYS" = "Darwin" ]; then
    command -v brew >/dev/null 2>&1 || {
      echo "🔴 Homebrew manquant. Installe-le d'abord : https://brew.sh"; exit 3; }
    echo "   installation…"; brew install ffmpeg
  elif command -v apt-get >/dev/null 2>&1; then
    echo "   installation (apt)…"; sudo apt-get update -qq && sudo apt-get install -y ffmpeg
  elif command -v dnf >/dev/null 2>&1; then
    echo "   installation (dnf)…"; sudo dnf install -y ffmpeg
  elif command -v pacman >/dev/null 2>&1; then
    echo "   installation (pacman)…"; sudo pacman -S --noconfirm ffmpeg
  else
    echo "🔴 ffmpeg manquant et aucun gestionnaire de paquets reconnu."
    echo "   L'installer à la main, puis relancer : https://ffmpeg.org/download.html"
    exit 3
  fi
fi

echo "── 3/3 · le moteur de voix ───────────────────────────────────────"
VENV="$HOME/.venvs/transcription"
# ⛔ REVUE AVEUGLE, 20 SEPT. 2026 — `python3` N'ÉTAIT JAMAIS VÉRIFIÉ. Sur un Mac vraiment
#    neuf, `python3` est le RACCOURCI des Command Line Tools : il ouvre une fenêtre
#    d'installation système, ou il échoue. `set -euo pipefail` tuait alors l'installeur sur
#    la ligne suivante, et le message ne nommait NULLE PART les Command Line Tools — la
#    personne reste bloquée sur une erreur qui ne dit pas quoi faire. On vérifie les deux
#    binaires (ffmpeg et brew le sont déjà) : un préalable non nommé est un préalable perdu.
command -v python3 >/dev/null 2>&1 \
  && python3 -c "import venv, ensurepip" >/dev/null 2>&1 || {
  echo "🔴 python3 n'est pas utilisable pour créer un environnement isolé."
  case "$(uname -s)" in
    Darwin) echo "   Sur un Mac neuf, c'est les outils de développement qui manquent :"
            echo "       xcode-select --install" ;;
    *)      echo "   Sur Debian/Ubuntu (WSL2 compris), c'est ce paquet :"
            echo "       sudo apt-get install -y python3-venv"
            echo "   Sur Fedora : sudo dnf install -y python3-libs" ;;
  esac
  echo "   (puis relancer cet installeur)"; exit 5; }
[ -x "$VENV/bin/python" ] || { echo "   création de $VENV…"; python3 -m venv "$VENV"; }
#    ⚠️ Le message des CLT ne vaut que pour macOS ; sur Linux c'est un paquet.
MODULE="mlx_whisper"; [ "$MOTEUR" = "faster-whisper" ] && MODULE="faster_whisper"
if "$VENV/bin/python" -c "import $MODULE" 2>/dev/null; then
  echo "   ✅ $MOTEUR déjà installé"
else
  echo "   installation de $MOTEUR (quelques minutes la première fois)…"
  "$VENV/bin/pip" install --quiet --upgrade pip
  "$VENV/bin/pip" install --quiet "$MOTEUR"
fi
# ⛔ LE CONTRÔLE POSITIF DE L'INSTALLEUR : il ne dit pas « installé » parce que pip n'a
#    pas crié — il IMPORTE le module. Un pip qui rend 0 sans avoir rien posé (roue
#    incompatible, cache pourri) laisserait l'installeur annoncer un succès sur une
#    machine incapable d'entendre quoi que ce soit — et c'est le défaut qu'on combat.
"$VENV/bin/python" -c "import $MODULE" 2>/dev/null || {
  echo "🔴 $MOTEUR s'est « installé » mais ne s'importe pas. Rien ne fonctionnera."
  echo "   Relancer, ou ouvrir une issue avec la sortie ci-dessus."; exit 6; }
echo "   ✅ vérifié : $MODULE s'importe pour de vrai"
# ⛔⛔ IL Y AVAIT ICI UN 2e CONTRÔLE, CODÉ EN DUR SUR `mlx_whisper` (retiré le 20 sept.
#    2026, trouvé par une revue aveugle qui a SIMULÉ une machine Linux). Vestige de la
#    version mono-plateforme. Effet mesuré : le bon moteur était choisi, installé,
#    vérifié ✅ à la ligne d'avant — puis cette ligne tuait l'installation en code 4 sur
#    Mac Intel, Linux ET WSL2, systématiquement. Le « multiplateforme » annoncé dans le
#    README n'existait donc PAS, et rien chez nous ne pouvait le voir : sur la machine
#    de développement (Apple Silicon), les deux contrôles passent.
#    ⭐ LA LEÇON : ajouter un garde NEUF sans retirer l'ANCIEN laisse deux gardes en
#    série, et c'est le plus vieux qui tranche. Le neuf dit ✅ juste avant. Un test de
#    la nouvelle logique ne peut pas attraper ça — seule une machine de l'AUTRE genre
#    le révèle, et on n'en a pas. Quand on généralise un outil, on CHERCHE les restes
#    de l'ancien cas particulier ; on ne les découvre pas, on les traque.
echo "   ✅ $VENV"

echo
echo "✅ INSTALLÉ. ⛔ Mais « installé » n'est pas « ça marche » : la seule preuve"
echo "   qui compte est de l'entendre dire une phrase qu'il ne peut pas deviner."
echo
echo "   Le contrôle positif, ~1 min (il fabrique lui-même une vidéo parlée et"
echo "   vérifie qu'il la réentend) :"
echo "     python3 \"$(cd "$(dirname "$0")" && pwd)/scripts/regarder.py\" --autotest"
