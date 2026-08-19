# Policies

```json
{
  "scenario_id": "ghana_power_backhaul_failure",
  "policies": [
    {
      "name": "terrestrial_only",
      "continuity": 0.4
    },
    {
      "name": "ntn_fallback",
      "continuity": 0.72
    },
    {
      "name": "priority_class",
      "continuity": 0.81
    }
  ],
  "evidence_status": "smoke_test_only"
}
```
