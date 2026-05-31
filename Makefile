.PHONY: test demo e2e

PY := PYTHONPATH=src

test:
	$(PY) pytest -q

demo:
	$(PY) python3 -m ntn_resilience.cli run gary_emergency --toy

e2e:
	@mkdir -p results/e2e
	$(PY) pytest -q 2>&1 | tee results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m ntn_resilience.cli list-scenarios >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m ntn_resilience.cli summarize gary_emergency >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m ntn_resilience.cli run gary_emergency --toy >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m ntn_resilience.cli make-report gary_emergency >> results/e2e/e2e_terminal_output.txt
	python3 scripts/e2e_check_required_artifacts.py
