# Project 1 validation and rubric audit

The current evidence supports all **25 required points and 5 stretch points targeted by the supplied rubric**, subject to the instructor's grading. This is an evidence audit, not an awarded grade. I have recorded and uploaded the project demo, which is linked in the [README Demo section](../README.md#demo).

I completed the manual tests described in the README’s AI Usage Transparency section, reviewed all five evaluation questions, expected answers, actual answers, judgments and reasoning, and accepted those judgments and the documented limitations. The accepted sequence remains **Accurate, Accurate, Partially Accurate, Accurate, Partially Accurate**. Every accepted evaluation row was compared with its pre-audit copy and preserved exactly. Only the review metadata in generation.json was updated to record my acceptance.

## Cleanup verification — October 13, 2026

The submission cleanup removed the private recording script and a redundant file-change inventory, revised narrative documentation, and updated the README generator so regeneration preserves the cleaned wording. The application code, tests, requirements, twelve corpus documents, and retained JSON evidence are byte-identical to their pre-cleanup copies. The five accepted judgments and original expected answers are unchanged.

The assistant ran `python -m unittest discover -s tests -v` in an isolated Python 3.12.1 environment using the dependency versions recorded in `environment.txt`: **9 tests passed in 0.691 seconds**, with no failures or errors. This is separate from my earlier seven-test run. All project/test files passed syntax checks; all project modules and the ChromaDB, Sentence Transformers, Groq, Gradio, and BM25 dependencies imported successfully. `python -m pip check` found no broken requirements. A repeated `python report.py` run was byte-identical and retained my review and the demo placeholder.

All 15 local Markdown links resolved. Whitespace/conflict checks passed, and secret scans found no matches in the 57 submission files, the Git index, or the eight historical Git blobs. The local environment, secrets, bytecode, model cache, and Chroma indexes remain ignored. No files were staged, and the commit and remote configuration were unchanged. Projects 2–4 were untouched.

The existing Python 3.14 environment again stalled during a dependency import; the cleanup checks used the working Python 3.12 environment instead. The README’s Python 3.12 setup remains the reproducible runtime path. No live model calls or experiments were rerun for this documentation cleanup; the earlier live evidence and its dates remain intact. At that cleanup checkpoint, the demo had not yet been recorded; its completed recording is now linked in the README.

## Final verification after demo upload

I supplied the completed demo link, and the assistant verified that its Google Drive viewer returned HTTP 200 without authentication, identified the file as `AI Project 1 Demo Video.mov`, and exposed video metadata without an access-denied message. The README and its generator now include the actual link. The earlier unrecorded-demo notes are historical checkpoints, not unfinished submission work.

The assistant reran `python -m unittest discover -s tests -v`: **9 tests passed in 0.201 seconds**, with no failures or errors. Syntax, project/dependency imports, dependency consistency, report regeneration, and all 17 local Markdown links passed. The secret scan found no matches in submission files, the Git index, or Git history. `.env`, `.venv`, `.venv312`, bytecode, model caches, and Chroma indexes are ignored.

These checks used the isolated Python 3.12 environment with the recorded dependency versions after cloud-offloaded files stalled imports in the local environment. No new live Groq calls or experiment outputs were needed. The assistant added explicit retrieval-quality summaries from the saved passages to match the starter checklist; the five answers, accepted accuracy judgments, expected answers, and source corpus remain unchanged.

## Required rubric

| Category | Target | Status and exact evidence |
|---|---:|---|
| Document Pipeline | 3/3 | PASS — README: Domain and Sources / Document Pipeline; documents/*.txt; evidence/chunks.json; pipeline.py load_documents and chunk_documents. Twelve meaningful documents (five official, seven student), 800 characters/150 overlap, rationale, and five actual labeled sample chunks. |
| Retrieval | 4/4 | PASS — README: Retrieval and relevance analyses; evidence/retrieval.json comparisons; pipeline.py Retriever.search. Three real queries with all top-four passages, relevance explanations, MiniLM name, Chroma/top-k and production accuracy/cost/latency/privacy/language/domain/context tradeoffs. |
| Grounded Generation | 3/3 | PASS — README: Grounded Generation, real answer transcripts and out-of-scope responses; generation.py; evidence/generation.json; evidence/final_verification/app_http.json. Two cited examples, prompt/citation-check explanation, FIFA refusal, and both my manual Super Bowl refusal test and the assistant’s separate retest. |
| Evaluation | 4/4 | PASS — README: Evaluation Report / Known Limitations; evidence/generation.json; evidence/failure_analysis.md. All five original questions and expectations, full actual answers, accepted accuracy judgments and reasoning; specific generation attribution/temporal-grounding failures and missing roommate corpus coverage. |
| Query Interface | 2/2 | PASS — README: Query Interface / Actual Gradio HTTP interaction; app.py and cli.py; evidence/interface.json; evidence/final_verification/app_http.json and smoke.json. Documented inputs, answers, source output and full transcripts; real CLI and Gradio entry point work. |
| planning.md | 4/4 | PASS — planning.md contains domain/value, source plan, chunk size/overlap/reasoning, retrieval/model/top-k/tradeoffs, five questions/expectations, four challenges, architecture and AI Tool Plan. Later discoveries are dated appendices, not rewritten planning history. |
| README Completeness | 3/3 | PASS — README includes domain/sources/chunking/model/tradeoffs/grounding/evaluation/failure/spec reflection, setup and architecture. Local links and evidence consistency verified. The completed demo video is linked in the README. |
| AI Usage Transparency | 2/2 | PASS — README: AI Usage Transparency. Two specific AI implementation uses with supplied context, outputs, checks and revisions; my seven-test run, initial browser failure, investigation/rebuild, CLI/UI review, source-type distinction, contextual follow-up, refusal, and acceptance of all five judgments. No claim of manual source-code authorship or inspection of every raw chunk/source. |

## Stretch rubric

| Feature | Target | Status and exact evidence |
|---|---:|---|
| Hybrid retrieval | +2 | PASS — pipeline.py combines semantic vectors and BM25 through reciprocal rank fusion, sum 1/(60+rank), up to twelve candidates per method. Three same-query comparisons, full results and analysis in README/evidence/retrieval.json. UI and CLI expose all three modes. Nine mode/query rankings reproduced during final verification. |
| Chunking comparison | +1 | PASS — experiments.py and README/evidence/retrieval.json compare 800/150 (26 chunks) with 400/75 (46), using identical queries/model/hybrid/top-k. Six strategy/query rankings reproduced. Source hit@4 tied, while smaller chunks focused on policy/frequency and larger chunks retained dorm-comparison context. |
| Metadata filtering | +1 | PASS — source-type filtering occurs before both ranking paths. Different official/student result sets appear in README and retrieval.json. Final CLI and HTTP tests confirm controls and labels. |
| Conversational memory | +1 | PASS — generation.py contextual_query and app.py session state retain bounded user-question history; prior generated answers are not supplied as evidence. I manually verified and accepted CHS→Drew; evidence/interface.json and final_verification/app_http.json show actual two-turn behavior. |

## Runtime validation commands — October 1, 2026

These October 1 commands ran in an isolated Python 3.12.1 environment with a separate model cache and HF_HUB_OFFLINE=1 for cached embeddings. The README provides portable setup commands.

| Command/check | Actual outcome |
|---|---|
| python -m pip check | PASS — no broken requirements. |
| python -m unittest discover -s tests -v | PASS — original seven tests; after adding report-preservation regressions, all nine tests pass. My earlier seven-test result remains recorded separately. |
| python -m py_compile pipeline.py generation.py cli.py app.py experiments.py report.py smoke.py | PASS — syntax. Runtime calls also imported Chroma, Sentence Transformers, Groq and Gradio successfully. |
| python cli.py build | First sandbox attempt FAIL with SQLite code 266 disk I/O error. Permitted retry PASS: Indexed 26 chunks. This is separate from my earlier AttributeError and is not claimed to establish its cause. |
| python cli.py retrieve "How often do Howard shuttles arrive?" --mode semantic (also bm25 and hybrid) | PASS — four results for each, Transportation Services ranked first; complete outputs in final_verification/cli.json. |
| python cli.py retrieve "Howard housing assignments" --source-type official (also student) | PASS — each result obeyed the chosen source type; complete outputs in final_verification/cli.json. |
| python experiments.py --generate --output-dir evidence/final_verification | PASS — all ten real Groq calls, nine search-mode/query comparisons, six chunking/query comparisons and filtering. Separate run preserved the accepted submission evidence. Assistant review retained three Accurate and two Partially Accurate; I did not separately review or accept this new run. |
| python app.py, followed by gradio_client calls to /ask | Initial official-only shuttle request FAIL: Groq InternalServerError; retrieval returned sources. Failure retained in final_verification/app_http_initial_error.json. Retry PASS: four real interactions (shuttle, CHS, Drew follow-up, Super Bowl), citations/source labels, contextual memory and exact refusal. HTTP 200; app_http.json contains full outputs. Server stopped normally. |
| python smoke.py --output-dir evidence/final_verification | PASS — seven checks: idempotent 26-chunk rebuild, metadata filters, empty query, UI empty query, localhost HTTP 200, client configuration and HTTP callback. Server closed. |
| python cli.py ask "How often do Howard shuttles arrive?" | PASS — real answer correctly gave 20–30 minutes, West Campus about 45, possible delays/live tracking and Transportation Services citations; exit 0. |
| python report.py | PASS — current review status and evidence rendered; a repeat render was byte-identical and retained completed human review and Demo section. |
| python experiments.py --generate (protection check) | PASS with expected exit 2 — refused to replace the accepted generation run before retrieval/API calls. Use --output-dir for new runs. |
| Evidence integrity / final_audit.json | PASS — twelve documents, 26/46 chunks, five sample chunks, saved chunks equal pipeline output, matching corpus signatures, unchanged original expectations and accepted rows, complete real outputs, required README sections and valid local links. |
| git diff --check and conflict-marker scan | PASS — no whitespace errors or merge markers. No Git mutation performed. |
| Security scan / security.json | PASS — .env ignored/untracked, .env.example key is a placeholder, no matching real key or credential pattern found in submission candidates or tracked/index content. Secret values were not printed or modified. |

## Retained limitations

The two Partially Accurate answers remain visible. Citations validate identifiers, not entailment: vague bathroom wording, temporal overstatement of historical property affiliations, and missing roommate evidence remain legitimate limitations. The initial live UI server error resolved on retry but demonstrates dependence on Groq availability; no unconditional live-service guarantee is made. My initial browser AttributeError was recovered by rebuilding/restarting, but its original traceback was not captured and the cause is unproven.

Source verification is complete at the document-paraphrase level: the full-title [Housing Waitlist URL](https://www.reddit.com/r/HowardUniversity/comments/1e6qzk5/housing_waitlist/) loaded during the final audit and confirmed the indexed text. No source needs further collection. Individual Reddit identities and anecdotes remain unauthenticated and explicitly labeled as perspectives. This source recheck was performed by the assistant.

I retained both Partially Accurate judgments after reviewing the answers and their limitations. The completed demo accompanies these unchanged evaluation results.

## Evidence and history

The accepted submission run remains at evidence/generation.json and retrieval.json. New runtime checks are under evidence/final_verification/. Earlier incomplete-review wording and unsuccessful attempts inside evidence/recovery_2026-09-29/ are historical snapshots, not current outstanding tasks. Original generation_initial.json and generation_unavailable.json remain intact because they substantiate real failures. No generated environment, model cache, or Chroma index is intended for Git submission.

The earlier audits did not commit, push, change remotes, delete source documents, or modify `.env`. The empty `documents/.gitkeep` is superseded by the twelve corpus files.
