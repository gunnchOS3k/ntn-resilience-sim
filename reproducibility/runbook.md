# Runbook

```bash
pip install -r requirements.txt
pytest -q
PYTHONPATH=src python3 -m ntn_resilience.cli run gary_emergency --toy
```

Expected: exit 0, artifact under results/ or docs/generated/.
