import json
import pathlib
p = pathlib.Path(__file__).parent / "lebron_response.json"
d = json.loads(p.read_text(encoding="utf-8"))
print("=== ANSWER ===")
print(d["answer"][:700])
print()
print("Sources:", len(d["sources"]))
print("SQL:", d.get("generated_sql", "None"))
print("Processing:", round(d["processing_time_ms"]), "ms")
if d.get("visualization"):
    v = d["visualization"]
    print("Viz Pattern:", v["pattern"])
    print("Viz Type:", v["viz_type"])
    vj = json.loads(v["plot_json"])
    layout = vj.get("layout", {})
    title = layout.get("title", {})
    print("Viz Title:", title.get("text", title) if isinstance(title, dict) else title)
    annots = layout.get("annotations", [])
    print("Viz Stats:", annots[0]["text"][:500] if annots else "(none)")
else:
    print("No visualization")
