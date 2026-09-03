# Evaluation report

Ran on 15 hand-written questions covering four categories:
`kb_only`, `web_only`, `both`, and `out_of_scope`.

## Aggregate metrics

- **Tool-selection accuracy:** 15/15 (100%)
- **Citation accuracy:** 14/15 (93%)
- **Average tool calls per question:** 2.07
- **Average time per question:** 18.2s

## Accuracy by category

| Category | N | Tool selection | Citations |
|---|---|---|---|
| `kb_only` | 6 | 6/6 | 6/6 |
| `web_only` | 4 | 4/4 | 4/4 |
| `both` | 4 | 4/4 | 3/4 |
| `out_of_scope` | 1 | 1/1 | 1/1 |

## Per-question results

| ID | Category | Tool ✓ | Cite ✓ | Calls | Time |
|---|---|---|---|---|---|
| `kb_01_mesa_optimization` | kb_only | ✅ | ✅ | 3 | 25.35s |
| `kb_02_constitutional_ai_method` | kb_only | ✅ | ✅ | 1 | 13.12s |
| `kb_03_sleeper_agents` | kb_only | ✅ | ✅ | 2 | 17.08s |
| `kb_04_rlhf` | kb_only | ✅ | ✅ | 2 | 13.82s |
| `kb_05_reward_hacking` | kb_only | ✅ | ✅ | 3 | 23.34s |
| `kb_06_scalable_oversight` | kb_only | ✅ | ✅ | 2 | 16.56s |
| `web_01_uk_pm` | web_only | ✅ | ✅ | 1 | 7.39s |
| `web_02_us_election_2024` | web_only | ✅ | ✅ | 1 | 10.26s |
| `web_03_ai_act` | web_only | ✅ | ✅ | 1 | 11.84s |
| `web_04_anthropic_models` | web_only | ✅ | ✅ | 1 | 13.68s |
| `both_01_cai_recent` | both | ✅ | ✅ | 2 | 21.15s |
| `both_02_interpretability_progress` | both | ✅ | ✅ | 2 | 18.02s |
| `both_03_rlhf_alternatives` | both | ✅ | ❌ | 4 | 27.39s |
| `both_04_deceptive_alignment_updates` | both | ✅ | ✅ | 5 | 41.72s |
| `edge_01_out_of_scope` | out_of_scope | ✅ | ✅ | 1 | 12.08s |

## Failures worth investigating

- **`both_03_rlhf_alternatives`**
  - Missing citations: ['2204.05862']
