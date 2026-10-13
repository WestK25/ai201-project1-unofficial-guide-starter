# Separate final verification run

These are new assistant-run checks from the final audit. The submission evaluations I accepted remain in [generation.json](../generation.json) and are unchanged; these new outputs do not replace them. All ten experiment calls succeeded. Four of the five new answers matched accepted answer text exactly; question 1 omitted only a redundant citation. The assistant inspected and reviewed these outputs separately.

retrieval.json/chunks.json: three search modes, identical-query chunking comparison, metadata filters.
generation.json: five planned questions, three additional questions and two conversational turns.
cli.json: actual semantic/BM25/hybrid and official/student CLI outputs.
app_http_initial_error.json: retained real Groq server error during the first standalone-app check.
app_http.json: successful retry of the four demonstration interactions through the actual app.py server.
smoke.json: successful index/filter/empty-input/HTTP checks.
evidence_protection.json: expected refusal to overwrite accepted evaluations.

The completed demo video is linked in the [README Demo section](../../README.md#demo).
