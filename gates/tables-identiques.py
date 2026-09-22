#!/usr/bin/env python3
"""
TABLES-IDENTIQUES — la table d'aiguillage est copiée 3 fois, elle doit rester UNE.

⛔ LE TROU QU'IL BOUCHE, VU EN ÉCRIVANT LA CONSIGNE DE REVUE (20 sept. 2026). La table
   « quel outil pour quelle vidéo » vit dans SKILL.md, codex/SKILL.md et README.md — il
   le faut, chacun est lu par quelqu'un de différent (Claude, Codex, un humain). Mais
   trois copies à la main divergent : on corrige une ligne là où on l'a vue, les deux
   autres restent, et **les trois continuent de se lire comme la vérité**. Une divergence
   de doc ne plante jamais — elle se découvre le jour où Codex et Claude aiguillent la
   même vidéo vers deux outils différents.

⭐ Il compare les LIGNES DE TABLEAU, pas le texte autour : le paragraphe d'intro peut
   légitimement être formulé autrement pour Codex. C'est la RÈGLE qui doit être identique.

Code 0 = les trois disent la même chose · 2 = elles divergent (nomme où).
"""
import hashlib, io, sys

FICHIERS = ["SKILL.md", "codex/SKILL.md", "README.md"]
MARQUEUR = "QUEL OUTIL POUR QUELLE VIDÉO"

def lignes_de_table(chemin):
    """Le PREMIER bloc de tableau contigu après le marqueur, et rien d'autre.

    ⛔ PREMIÈRE VERSION FAUSSE, ATTRAPÉE PAR SON PROPRE CONTRÔLE POSITIF (20 sept. 2026).
       Elle prenait « toutes les lignes commençant par | dans les 4000 caractères qui
       suivent » — une FENÊTRE ARBITRAIRE. Elle avalait donc les tableaux SUIVANTS
       (les pièges dans SKILL.md, l'autotest dans README.md), qui n'ont ni la même
       longueur ni le même contenu d'un document à l'autre : 10, 6 et 14 lignes pour
       des tables d'aiguillage pourtant IDENTIQUES. Elle criait 🔴 sur un paquet sain.
       👉 Un faux rouge coûte autant qu'un faux vert : on cesse de lire le garde.
       Le bloc se BORNE — dès qu'une ligne non-`|` suit des lignes `|`, le tableau
       est fini."""
    s = io.open(chemin, encoding="utf-8").read()
    i = s.find(MARQUEUR)
    if i < 0:
        return None
    table, commence = [], False
    for ligne in s[i:].split("\n"):
        l = ligne.strip()
        if l.startswith("|"):
            commence, _ = True, table.append(l)
        elif commence:
            break
    return table

racine = sys.argv[1] if len(sys.argv) > 1 else "."
vues, absents = {}, []
for f in FICHIERS:
    t = lignes_de_table(f"{racine}/{f}")
    if t is None or not t:
        absents.append(f)
        continue
    vues[f] = (hashlib.sha256("\n".join(t).encode()).hexdigest()[:12], len(t))

if absents:
    print(f"🔴 table d'aiguillage ABSENTE de : {', '.join(absents)}")
    print("   ⛔ Un document sans la table envoie son lecteur deviner.")
    sys.exit(2)

empreintes = {e for e, _ in vues.values()}
if len(empreintes) != 1:
    print("🔴 LES TABLES D'AIGUILLAGE DIVERGENT :")
    for f, (e, n) in vues.items():
        print(f"     {f:<16} {n} lignes · {e}")
    print("   ⛔ Corriger la bonne, recopier dans les deux autres, relancer.")
    sys.exit(2)

e, n = next(iter(vues.values()))
print(f"  ✅ table d'aiguillage identique dans les 3 documents ({n} lignes · {e})")
