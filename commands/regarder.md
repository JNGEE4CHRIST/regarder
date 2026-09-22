---
description: Écouter ET voir une vidéo locale (screen record, mémo, démo). Transcrit la voix en local, sans clé API, et attache à chaque phrase l'écran de ce moment-là.
argument-hint: <chemin-de-la-video> [ce que tu veux en savoir]
allowed-tools: [Bash, Read]
---

Invoque le skill `regarder` (défini dans SKILL.md) avec les arguments : $ARGUMENTS

Suis le pipeline au complet : lancer `scripts/regarder.py` sur la vidéo avec un dossier
`--sortie` neuf → ouvrir `INDEX.md` → **ouvrir avec `Read` l'image attachée à CHAQUE
réplique** (pas seulement lire son chemin) → rendre la liste des demandes, une case à
cocher par ligne, avec horodatage, citation, et ce que l'écran montre à cet instant.

⛔ Un code 3, 4 ou 5 ne veut jamais dire « il n'a rien dit » — lire le tableau des codes
dans SKILL.md et redemander ce qui manque au lieu de répondre sur les images seules.

Si aucun argument n'est donné, demander le chemin de la vidéo avant de continuer.
