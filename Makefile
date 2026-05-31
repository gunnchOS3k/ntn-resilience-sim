.PHONY: test demo demo-research benchmark-toy map

test:
	pytest -q

demo:
	PYTHONPATH=src python3 -m ntn_resilience.cli run gary_emergency --toy
