#!/usr/bin/env python3
"""Regenera catalogo.json y miniaturas.json desde roms/ y covers/."""
import json, os, hashlib, datetime, subprocess, base64, tempfile

BASE = "https://zerogapcode.github.io/nes-arcade/"

# id, nombre, archivo .nes, carátula. El orden es el del catálogo.
JUEGOS = [
    ("battletoadsdd", "Battletoads & Double Dragon",        "BattletoadsDD.nes", "battletoadsdd.jpg"),
    ("contra",        "Contra",                             "Contra.nes",        "contra.jpg"),
    ("doubledragon",  "Double Dragon",                      "DoubleDragon.nes",  "doubledragon.jpg"),
    ("doubledragon2", "Double Dragon II: The Revenge",      "DoubleDragon2.nes", "doubledragon2.jpg"),
    ("doubledragon3", "Double Dragon III: The Sacred Stones","DoubleDragon3.nes","doubledragon3.jpg"),
    ("lowgman",       "Low G Man",                          "LowGMan.nes",       "lowgman.jpg"),
    ("mariobros",     "Mario Bros.",                        "MarioBros.nes",     "mariobros.jpg"),
    ("megaman2",      "Mega Man 2",                         "MegaMan2.nes",      "megaman2.jpg"),
    ("metalgear",     "Metal Gear",                         "MetalGear.nes",     "metalgear.jpg"),
    ("punchout",      "Mike Tyson's Punch-Out!!",           "PunchOut.nes",      "punchout.jpg"),
    ("pacman",        "Pac-Man",                            "PacMan.nes",        "pacman.jpg"),
    ("platoon",       "Platoon",                            "Platoon.nes",       "platoon.jpg"),
    ("robocop",       "RoboCop",                            "RoboCop.nes",       "robocop.jpg"),
    ("smb",           "Super Mario Bros.",                  "SMB.nes",           "smb.jpg"),
    ("smb2",          "Super Mario Bros. 2",                "SMB2.nes",          "smb2.jpg"),
    ("smb3",          "Super Mario Bros. 3",                "SMB3.nes",          "smb3.jpg"),
    ("tmnt",          "Teenage Mutant Ninja Turtles",       "TMNT.nes",          "tmnt.jpg"),
    ("terminator2",   "Terminator 2: Judgment Day",         "Terminator2.nes",   "terminator2.jpg"),
    ("tetris",        "Tetris",                             "Tetris.nes",        "tetris.jpg"),
    ("zelda",         "The Legend of Zelda",                "Zelda.nes",         "zelda.jpg"),
]

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

juegos, thumbs = [], {}
with tempfile.TemporaryDirectory() as tmp:
    for gid, nombre, rom, cover in JUEGOS:
        rp, cp = f"roms/{rom}", f"covers/{cover}"
        for p in (rp, cp):
            if not os.path.exists(p):
                raise SystemExit(f"falta {p}")

        juegos.append({
            "id": gid, "nombre": nombre, "rom": rp,
            "bytes": os.path.getsize(rp), "md5": md5(rp),
            "caratula": cp, "caratula_bytes": os.path.getsize(cp),
        })

        # Miniatura 76x108 para la lista del catálogo del portal.
        thumb = os.path.join(tmp, gid + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "45",
                        "-Z", "108", cp, "--out", thumb],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        thumbs[gid] = base64.b64encode(open(thumb, "rb").read()).decode("ascii")

with open("catalogo.json", "w") as f:
    json.dump({"version": 1,
               "actualizado": datetime.date.today().isoformat(),
               "base": BASE,
               "juegos": juegos},
              f, ensure_ascii=False, indent=2)
    f.write("\n")

with open("miniaturas.json", "w") as f:
    json.dump(thumbs, f, separators=(",", ":"))
    f.write("\n")

cat_size = os.path.getsize("catalogo.json")
thumb_size = os.path.getsize("miniaturas.json")
print(f"{len(juegos)} juegos")
print(f"catalogo.json    {cat_size:>8,} B   ({cat_size // len(juegos)} B/juego)")
print(f"miniaturas.json  {thumb_size:>8,} B   ({thumb_size // len(juegos)} B/juego)")
print(f"ROMs             {sum(g['bytes'] for g in juegos):>8,} B")
print(f"carátulas        {sum(g['caratula_bytes'] for g in juegos):>8,} B")
