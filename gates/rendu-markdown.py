#!/usr/bin/env python3
"""UNE TABLE COUPÉE PAR UN PARAGRAPHE NE SE REND PLUS COMME UNE TABLE.

⛔ LE DÉFAUT PAYÉ, TROUVÉ PAR KIMI LE 20 SEPTEMBRE 2026. Deux tableaux du paquet
   étaient coupés en deux par un paragraphe glissé au milieu : GitHub rendait alors les
   lignes suivantes en TEXTE BRUT, pipes compris, hors du tableau.
   · la ligne « Windows natif » du README et de SKILL.md — donc le lecteur du README
     ne voyait PAS que Windows natif est refusé, celui de la version Codex oui ;
   · les codes 7/3/4/5/6/8 de codex/SKILL.md — six codes de sortie sur huit, sans
     en-tête de colonne.

⭐ POURQUOI ÇA MÉRITE UN GATE ET PAS UNE RELECTURE. Le fichier SOURCE se lit
   parfaitement : les lignes sont là, alignées, dans l'ordre. Le défaut n'existe qu'au
   RENDU, c'est-à-dire chez le lecteur — et personne n'ouvre GitHub pour vérifier une
   ligne qu'il vient d'écrire. ⚠️ Je l'ai moi-même introduit en déplaçant un bloc, puis
   « réparé » en le déplaçant au mauvais endroit : deux fois le même geste, deux fois
   invisible à la relecture du source.

Se lance seul (--autotest) : il fabrique les deux formes et vérifie qu'il dit non à
l'une et oui à l'autre. Un gate jamais vu bloquer ne garde rien.
"""
import os, sys

DOCS = ("README.md", "SKILL.md", os.path.join("codex", "SKILL.md"))


def orphelines(texte):
    """Lignes de tableau qui suivent une ligne NON VIDE qui n'est pas du tableau."""
    lignes, trouve, dans_code = texte.split("\n"), [], False
    for i, l in enumerate(lignes):
        if l.lstrip().startswith("```"):
            dans_code = not dans_code
        if dans_code or not l.startswith("|"):
            continue
        avant = lignes[i - 1] if i else ""
        if avant.strip() and not avant.startswith("|"):
            trouve.append((i + 1, l[:70]))
    return trouve


def juger(racine):
    casse = 0
    for nom in DOCS:
        chemin = os.path.join(racine, nom)
        if not os.path.isfile(chemin):
            continue
        mauvaises = orphelines(open(chemin, encoding="utf-8").read())
        if mauvaises:
            casse += len(mauvaises)
            print(f"  🔴 {nom} — {len(mauvaises)} ligne(s) de tableau ORPHELINE(S) :")
            for n, l in mauvaises:
                print(f"       ligne {n} : {l}")
    if casse:
        print("\n  ⛔ Sur GitHub, ces lignes se rendent en TEXTE BRUT, pipes compris, hors du")
        print("     tableau. Le fichier source, lui, se lit parfaitement — c'est tout le piège.")
        print("     👉 Remettre la ligne DANS le tableau, et le paragraphe APRÈS.")
        return 1
    print(f"  ✅ aucune ligne de tableau orpheline ({len(DOCS)} documents)")
    return 0


def autotest():
    bon = "| a | b |\n|---|---|\n| 1 | 2 |\n\nUn paragraphe APRÈS.\n"
    mauvais = "| a | b |\n|---|---|\n\nUn paragraphe AU MILIEU.\n| 1 | 2 |\n"
    ok = True
    for nom, texte, attendu in (("table saine", bon, 0), ("table COUPÉE", mauvais, 1)):
        rendu = len(orphelines(texte))
        vu = 1 if rendu else 0
        print(f"   {'✅' if vu == attendu else '🔴'} {nom:<16} {rendu} orpheline(s) (attendu "
              f"{'≥1' if attendu else '0'})")
        ok = ok and vu == attendu
    # ⭐ Un tableau DANS un bloc de code n'est pas un tableau : sans ça, tout exemple
    #    de sortie collé dans la doc compterait comme un défaut, et le gate serait
    #    désarmé le jour où il crie au loup une fois de trop.
    dans_code = "Exemple :\n```\ntexte\n| a | b |\n```\n"
    vu = len(orphelines(dans_code))
    print(f"   {'✅' if vu == 0 else '🔴'} bloc de code     {vu} orpheline(s) (attendu 0)")
    ok = ok and vu == 0
    print("\n✅ le gate dit non à la coupée et oui à la saine" if ok else "\n🔴 GATE CASSÉ")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--autotest" in sys.argv:
        sys.exit(autotest())
    sys.exit(juger(sys.argv[1] if len(sys.argv) > 1 else "."))
