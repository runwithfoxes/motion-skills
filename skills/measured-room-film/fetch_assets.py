"""Download the free Poly Haven textures and models the realistic games room uses. No key, no cost.
Run: python3 fetch_assets.py   (files land in assets/, which git ignores)"""
import json, os, urllib.request
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
TEX = ["laminate_floor_02", "plastered_wall_02", "velour_velvet", "black_oak_veneer", "fabric_pattern_07"]
MODELS = ["bar_chair_round_01", "gamepad"]
def get(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "dray-games-room"})
        open(path, "wb").write(urllib.request.urlopen(req).read())
def files(asset):
    req = urllib.request.Request(f"https://api.polyhaven.com/files/{asset}", headers={"User-Agent": "dray-games-room"})
    return json.load(urllib.request.urlopen(req))
for t in TEX:
    f = files(t)
    for key, name in (("Diffuse", "diff"), ("nor_gl", "nor"), ("Rough", "rough")):
        if key in f:
            u = f[key]["2k"]["jpg"]["url"]; get(u, os.path.join(HERE, t, name + ".jpg"))
    print("texture", t)
for m in MODELS:
    g = files(m)["gltf"]["1k"]["gltf"]
    get(g["url"], os.path.join(HERE, m, os.path.basename(g["url"])))
    for rel, inc in g.get("include", {}).items():
        get(inc["url"], os.path.join(HERE, m, rel))
    print("model", m)
