from pathlib import Path
def export() -> Path:
    out = Path("results/tool_exports/ntn_standards_watchlist.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# NTN standards watch\n\n3GPP NTN, ITU references — literature alignment only.\n", encoding="utf-8")
    return out
