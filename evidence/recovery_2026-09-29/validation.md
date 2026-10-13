# Validation and rubric audit

> Historical September 29 validation snapshot. Later recovery and my completed review are recorded in [the current validation document](../validation.md).

Validation date: 2026-09-29. These are assistant-run checks; student verification and acceptance remain pending. See `environment.txt` for the actual Python 3.12 environment's package versions. No commits, pushes, Git-history changes, or .env edits were made. The pre-existing deletion of `documents/.gitkeep` was left alone.

## Tests actually run

| Check / command | Outcome |
|---|---|
| `python -m py_compile pipeline.py generation.py cli.py app.py experiments.py report.py smoke.py` | Passed syntax compilation. |
| `python -m unittest discover -s tests -v` | Seven tests passed, including chunk coverage/overlap/stability, metadata ingestion, exclusions, corpus count, reference handling, missing key/query/context, and citation rejection. Groq responses in the citation unit test are mocks, not evaluation evidence. |
| `python -m pip check` | Passed in temporary Python 3.12 environment and existing Python 3.14 environment. |
| Imports: chromadb, sentence_transformers, gradio | Passed in temporary Python 3.12 environment. Original environment full imports were stopped after prolonged cloud-file stalls. |
| `python cli.py chunks` | Passed; 12 documents and 26 baseline chunks, saved in `chunks.json`. |
| `python cli.py build` | Passed with network permission; 26 embedded chunks stored in ChromaDB. |
| `python experiments.py --generate` | Ran three semantic/BM25/hybrid comparisons; 800/150 versus 400/75 on identical queries; metadata filtering; five planned generation questions; out-of-scope/adversarial/live-arrival tests; and two conversational turns. Full outputs and statuses are in `retrieval.json` and `generation.json`. API status `ok` means the request/citation checks succeeded, not that the answer is accurate. |
| `python smoke.py` | Passed idempotent rebuilding at 26 chunks, source-type filtering, empty query handling, Gradio HTTP 200, client configuration, and empty-question HTTP callback. Local server was stopped after testing. |
| `git diff --check` / `git check-ignore .env .cache/huggingface chroma_db .venv` | Passed at review; secret, caches, database, and environments are ignored. |

The first unit-test coverage input was accidentally periodic, triggering intentional duplicate suppression; the test was changed to unique text and passed. Initial sandbox installs/model downloads failed DNS resolution and were rerun with permission. The newest Gradio installed an incompatible Hub version; pinning Gradio 6.9.0 and Hub <1 resolved the dependency check. The initial Llama generation requests all returned NotFoundError; the model list confirmed that account could not access it. Qwen was selected from that list and evaluated. The first successful Qwen run included an entity-attribution error and one RateLimitError; those outputs are retained in `generation_initial.json`. No API failure is counted as a correct answer or refusal. The final run uses the refined prompt and spaces calls by 15 seconds.

## Required rubric — evidence audit (25 possible points)

| Category | Item | Evidence / status |
|---|---|---|
| Document Pipeline (3) | Domain and at least 10 specific documents | Present: 12 documents, linked source table in README; collection provenance in `source_review.md`. |
| | Chunk size, overlap, reasoning | Present: 800 characters / 150 overlap, explained in planning and README. |
| | Five labeled real sample chunks | Present in README, generated from pipeline; all chunks in `chunks.json`. |
| Retrieval (4) | Three real retrieval tests | Present: complete semantic passages and scores in README and JSON. |
| | Relevance explanations for at least two | Present: policy, shuttle, and dorm analyses grounded in actual rankings. |
| | Embedding model named | Present: all-MiniLM-L6-v2. |
| | Production tradeoffs | Present: accuracy, cost, token context, languages, domain language, latency, privacy, local versus API. |
| Grounded Generation (3) | Two real cited answers | Present: housing and shuttle transcripts from successful Qwen requests. |
| | Out-of-scope query and refusal | Present: FIFA question and exact insufficient-information response. |
| | Grounding explanation | Present: prompt, fresh JSON context, empty-result refusal, citation checks, and their limits. |
| Evaluation (4) | Five planned questions and expectations | Preserved and reported in README. |
| | Actual responses and judgments | Saved full responses; AI-assisted judgments awaited my acceptance at this checkpoint. |
| | Specific honest failure | Cook-to-Drew entity misattribution in initial run, source coverage gap, and final-run caveats; see failure analysis. |
| Query Interface (2) | Input/output description | Present; actual Gradio server and callback tested. |
| | Complete interaction transcript | Present: question, full actual backend response, source list; same backend used by UI. Browser visual review remains manual. |
| planning.md (4) | Domain/value and document list | Present, preserving original planning purpose and recording source substitution. |
| | Chunking/retrieval/model/top-k/tradeoffs | Present. |
| | Five questions with specific expectations | Original expectations preserved. |
| | Challenges, architecture, AI Tool Plan | Present; unfinished architecture fence repaired and missing AI Tool Plan added. |
| README Completeness (3) | Technical setup and architecture | Present, with reproducible commands and model/dependency refinements. |
| | Evaluation/failure/spec reflection | Present, with actual evidence and stated limits. |
| AI Usage Transparency (2) | Two specific assistance instances | Documented requests, supplied context, produced files, assistant-run checks and revisions. |
| | My review/revision/acceptance | **Pending at this historical checkpoint.** I had not yet completed or recorded my manual testing and evaluation acceptance. The current README records my later work. |

## Stretch — evidence audit (+5 possible points)

| Feature | Evidence / status |
|---|---|
| Hybrid (+2) | Implemented and default in UI; semantic/BM25/hybrid actual top-four results for three queries, rank-fusion formula, scores, and honest comparison. No unsupported claim of hybrid superiority. |
| Chunking (+1) | 800/150 (26 chunks) versus 400/75 (46 chunks), same three queries, actual top-four results, tied hit@4, and passage-level coverage analysis. |
| Metadata filtering (+1) | Implemented before both rankers; official/student UI control; actual changed result lists and assertions. |
| Conversational memory (+1) | Per-session bounded history; contextual retrieval query and real CHS→Drew two-turn transcript. Coreference works in the demonstrated case, not guaranteed for arbitrary conversations. |

These are evidence statuses, not awarded grades. The instructor determines points. At this checkpoint, my manual testing, evaluation acceptance, and demo were still pending. The direct waitlist page was unavailable, although its indexed text had been collected. The later [validation record](../validation.md) documents the completed manual review and resolved source access; the completed demo is now linked in the [README](../../README.md#demo).

## Historical runtime context

This run used an isolated Python 3.12 environment and a separate embedding-model cache. It ran `python -m unittest discover -s tests -v` and launched `python app.py`. Current portable setup and evidence-preserving rerun commands are in the [README](../../README.md#setup); this archived record does not replace the accepted evaluations.
