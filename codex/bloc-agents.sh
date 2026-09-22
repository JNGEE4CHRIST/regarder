#!/usr/bin/env bash
# Écrit le bloc AGENTS.md avec le chemin RÉEL de ce clone.
#
# ⛔ NÉ D'UNE REVUE CODEX (20 sept. 2026). `AGENTS-a-coller.md` demandait de remplacer
#    `<RACINE>` à la main — donc il n'était PAS copiable-collable, et un bloc collé tel
#    quel envoie l'agent vers un chemin qui n'existe pas. ⭐ Une consigne « à adapter »
#    se colle quand même sans être adaptée : c'est la machine qui doit remplir le trou.
set -euo pipefail
RACINE="$(cd "$(dirname "$0")/.." && pwd)"
CIBLE="$HOME/.codex/AGENTS.md"

[ -f "$RACINE/scripts/regarder.py" ] || {
  echo "🔴 $RACINE ne ressemble pas au dépôt regarder (scripts/regarder.py absent)." >&2
  exit 2; }

# ⛔ Un doublon ne plante jamais : les deux blocs se lisent comme la vérité, et le jour
#    où l'un des deux est corrigé, l'agent peut lire l'autre. On refuse au lieu d'ajouter.
if [ -f "$CIBLE" ] && grep -q "scripts/regarder.py" "$CIBLE"; then
  echo "⚠️ $CIBLE contient déjà un bloc qui pointe vers regarder.py — rien ajouté." >&2
  echo "   Le corriger à la main si le chemin a changé." >&2
  exit 3
fi

cat <<BLOC

### 🎥 Une vidéo locale (screen record, .mov, .mp4) — ou un lien vers une vidéo
Skill \`regarder\`. HORS bac à sable (le GPU n'y est pas visible) :
\`python3 $RACINE/scripts/regarder.py "<video>" --sortie /tmp/regard/<nom>-<HHMMSS>\`,
puis ouvrir \`INDEX.md\` ET l'image de chaque réplique. Jamais de transcription par un
autre moyen, jamais les images seules.
⛔ Une URL : l'outil REFUSE (code 2) et dit quoi faire — télécharger d'abord avec
\`yt-dlp\`, puis relancer. Il ne télécharge rien lui-même, c'est voulu.
⛔ Si ça sort en code 7 : \`bash $RACINE/installer.sh\`
BLOC
