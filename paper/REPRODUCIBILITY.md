# Reproducibility (Paper III)

Canonical: [../REPRODUCIBILITY.md](../REPRODUCIBILITY.md)

Frozen protocol: [artifacts/experiment_protocol.yaml](artifacts/experiment_protocol.yaml)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt pytest matplotlib
make paper-reproduce
```

Tables and decision-region figures come from `rq3_gary_failover_sweeps.json`. SYNTHETIC_SIM. NTN is not always better. Independent human reproduction PENDING.
