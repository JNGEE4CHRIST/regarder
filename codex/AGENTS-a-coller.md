# La ligne à coller dans `~/.codex/AGENTS.md`

Le skill seul ne suffit pas : Codex ne le lit que s'il sait **quand** aller le chercher.

## ⭐ La commande qui écrit le bloc pour toi, avec TON chemin dedans

⛔ **Avant le 20 sept. 2026, ce fichier disait « en remplaçant `<RACINE>` par le chemin
absolu du dépôt ».** Une revue Codex l'a fait tomber en une ligne : ce n'était donc pas
copiable-collable, et une consigne « à adapter » se colle quand même telle quelle — avec
le `<RACINE>` dedans. Un agent lit alors un chemin qui n'existe pas. **Maintenant la
machine remplit le chemin elle-même :**

```bash
# depuis le dépôt cloné :
./codex/bloc-agents.sh >> ~/.codex/AGENTS.md
```

Il écrit le bloc ci-dessous avec le chemin RÉEL de ton clone, et refuse si `AGENTS.md`
le contient déjà (pas de doublon silencieux).

## Ce que ça ajoute

```markdown
### 🎥 Une vidéo locale (screen record, .mov, .mp4) — ou un lien vers une vidéo
Skill `regarder`. HORS bac à sable (le GPU n'y est pas visible) :
`python3 <RACINE>/scripts/regarder.py "<video>" --sortie /tmp/regard/<nom>-<HHMMSS>`,
puis ouvrir `INDEX.md` ET l'image de chaque réplique. Jamais de transcription par un
autre moyen, jamais les images seules.
⛔ Une URL : l'outil REFUSE (code 2) et dit quoi faire — télécharger d'abord avec
`yt-dlp`, puis relancer. Il ne télécharge rien lui-même, c'est voulu.
```

⛔ **« Branché » ne veut pas dire « le skill est écrit ».** Ça se prouve par un vrai
`codex exec` (entrée standard fermée, `</dev/null`), en lui parlant comme d'habitude,
**sans lui nommer l'outil**, et en regardant s'il y va tout seul. ⚠️ `codex exec` rend
`EXIT=0` même sur une erreur : on juge sa **sortie**, jamais son code de retour.
