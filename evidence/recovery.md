# Technical recovery — October 1, 2026

Cloud-offloaded dependency files stalled the original Python 3.14 environment, and the earlier temporary environment and model cache were no longer available. Recovery recreated an isolated Python 3.12 environment, installed the recorded dependencies, restored the embedding model, and rebuilt the ignored Chroma index. Evidence saves use atomic replacement to avoid stalled overwrites.

Generation validation also required corrections: grouped citations are now parsed, instructions check speaker/entity attribution and venue categories, stale corpus signatures prevent report generation, and retrying changed evaluation answers resets their proposed judgments. Reference-bearing follow-ups receive prior user questions; unrelated questions do not. These changes preserved the original five expected answers.

The twelve source documents and earlier failures remain intact. The [archived September 29 evidence](recovery_2026-09-29/validation.md) records the earlier run, and the [failure analysis](failure_analysis.md) explains the remaining limitations. The [validation record](validation.md) documents the successful recovery checks and my later acceptance of the five evaluation judgments.

My separately observed Gradio retrieval error resolved after rebuilding and restarting. Its original traceback was not captured, so the cause remains unproven; it is not attributed to the later SQLite or cloud-storage failures.
