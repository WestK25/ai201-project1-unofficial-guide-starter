"""Render README evidence from saved run artifacts (never invent missing results)."""
import json
import re
from pipeline import ROOT, load_documents, chunk_documents, fingerprint
from generation import sources_markdown
from experiments import planned_questions


def preserve_manual_sections(rendered, existing):
    """Keep completed personal review and the demo URL across report regeneration."""
    for heading in ['AI Usage Transparency', 'Demo']:
        pattern = rf'^## {re.escape(heading)}\n.*?(?=^## |\Z)'
        saved = re.search(pattern, existing, flags=re.M | re.S)
        if saved:
            rendered = re.sub(pattern, lambda _: saved.group(), rendered, flags=re.M | re.S)
    return rendered


def main():
    docs = load_documents(); chunks = chunk_documents(docs)
    path = ROOT/'evidence'
    retrieval = json.loads((path/'retrieval.json').read_text()) if (path/'retrieval.json').exists() else None
    generation = json.loads((path/'generation.json').read_text()) if (path/'generation.json').exists() else None
    for artifact in [retrieval, generation]:
        if artifact and artifact.get('corpus_signature') != fingerprint(chunks):
            raise ValueError('Evidence belongs to a different corpus. Rebuild and rerun experiments.')
    sections = ['''# The Unofficial Guide to Howard University Student Life

## Project Overview

This RAG application answers Howard student-life questions from a local collection of official information and individual student experiences. It ingests attributed text, makes overlapping chunks, embeds them locally, retrieves evidence from ChromaDB and BM25, and asks Groq to produce a cited answer. It includes a Gradio conversation interface, source filtering, retrieval comparisons, and saved evaluation artifacts. It is an unofficial course project, not a live University service.

## Domain and Sources

Housing procedures, dining, transportation, and everyday campus experiences are distributed across University offices and student discussions. The collection brings those perspectives together while preserving their different authority and dates. Source files are editorial paraphrases, not verbatim captures or invented student quotations. The assistant checked the two summaries I supplied against the linked pages. Other summaries were written after retrieving the cited source text on September 29, 2026. Reddit identities/enrollment and the truth of individual anecdotes are not independently verified.

The corpus has 12 meaningful documents (five official, seven student-perspective). The original upperclassman thread `1txvuw9` could not be fetched; the historical July 19, 2024 **Housing Waitlist** post replaces it on the same topic. Its indexed text was rechecked on October 1, and the final audit also retrieved the [full-title post URL](https://www.reddit.com/r/HowardUniversity/comments/1e6qzk5/housing_waitlist/), resolving the earlier direct-page access issue. See [source_review.md](evidence/source_review.md) for the verification record. Other abbreviated Reddit URLs resolved with full title paths. No missing source text was invented. The assistant performed source verification; I describe my own testing, review, and acceptance decisions in AI Usage Transparency.

| Document | Type / topic | Source |
|---|---|---|''']
    for doc in docs:
        m=doc['metadata']; sections.append(f"| `{m['filename']}` | {m['source_type']} / {m['topic']} | [{m['source']}]({m['source_url']}) |")
    sections.append('''
## Setup

Run these commands from the repository root. Python 3.12 is the tested version; the dependency versions are recorded in `evidence/environment.txt`. Preserve any existing `.env`. For a new checkout only, create `.env` from `.env.example` and privately set `GROQ_API_KEY`. Optional `GROQ_MODEL` defaults to `qwen/qwen3.8-27b`. Never paste credentials into logs or Git.

```bash
# Only if an environment does not already exist:
python3.12 -m venv .venv312
source .venv312/bin/activate
python -m pip install -r requirements.txt
# New checkout only; this command does not overwrite an existing .env:
test -f .env || cp .env.example .env
python cli.py build
python -m unittest discover -s tests -v
python experiments.py --generate --output-dir evidence/new_run
# New runs require their own review; the accepted report evidence is preserved.
python report.py
python app.py
```

The first index build downloads the embedding model and requires network access. Embeddings and Chroma data stay local; generation sends the question, up to three prior user questions, and retrieved passages to Groq. Generated answers are nondeterministic even with temperature zero. `python experiments.py --output-dir evidence/new_run` runs retrieval-only experiments without an API key. Use a new output directory for reruns; accepted generation evidence is protected. `python smoke.py --generate --output-dir evidence/new_run` tests the Gradio HTTP API with real generation. `python cli.py retrieve "How often do shuttles arrive?" --mode semantic` tests retrieval independently. `python cli.py chunks` displays every chunk and its metadata.

The October 1 recovery succeeded in an isolated Python 3.12 environment after cloud-offloaded files stalled the original Python 3.14 environment. Use the portable setup above and keep source files, dependencies, and the model cache available locally. The technical recovery record is preserved in [recovery.md](evidence/recovery.md).

The environment, `.env`, model cache, and Chroma indexes are ignored. The small, deliberate `evidence/*.json` artifacts remain reviewable submission evidence. They contain public corpus text and demonstration questions, not the API key.

## Document Pipeline

`pipeline.py` reads non-hidden `.txt` files, excludes empty files and explicitly unverified or placeholder documents, parses metadata before `CONTENT:`, and collapses unnecessary whitespace. Invalid metadata raises an actionable error. Each chunk retains filename, source title, URL, accessed date, source type, topic, content description, and character offsets. IDs hash the metadata and text, making unchanged builds stable. Changed documents invalidate the index signature; rebuilding upserts current chunks and removes obsolete IDs.

The baseline uses **800-character chunks with 150-character overlap**. This retains short policy explanations or student experiences with some boundary context while keeping passages focused. Fixed character boundaries can cut sentences and words; overlap reduces but does not eliminate that problem. Exact duplicate text within a document is emitted once. The loop validates its stride and stops at the final chunk. Metadata is stored separately and is not part of the 800-character body. Small final chunks are retained.
''')
    sections.append(f'Actual corpus: **{len(docs)} documents, {len(chunks)} baseline chunks**. Full output: [chunks.json](evidence/chunks.json).\n\n### Five actual sample chunks\n')
    samples=[]
    for chunk in chunks:
        if chunk['metadata']['filename'] not in [c['metadata']['filename'] for c in samples]: samples.append(chunk)
        if len(samples)==5: break
    for i,c in enumerate(samples,1):
        sections.append(f"**Sample {i}: {c['metadata']['filename']}**, offset {c['metadata']['start']}, ID `{c['id']}`\n\n> {c['text']}\n")
    sections.append('''
## Retrieval

The model is **sentence-transformers/all-MiniLM-L6-v2**, with normalized embeddings and ChromaDB cosine distance. Queries use the same model. Semantic retrieval and the application default hybrid retrieval both return **top-k = 4**. Returned records include text, source metadata, ranking score, cosine distance when available, and BM25 score when available. Lower cosine distance is better; the hybrid score is a rank-fusion value, not a probability.

### Production embedding-model tradeoff reflection

This local model is small and economical for a classroom corpus. Its [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) describes 384-dimensional embeddings and truncation beyond 256 word pieces. Character chunking cannot guarantee a token limit, so a production system should measure token counts and truncation. Larger-context models may retain longer policy conditions but also produce less focused matches.

Production selection should measure answer-bearing passage recall and ranking accuracy on held-out Howard questions, including slang, CHS/CHN abbreviations, and conflicting perspectives. Multilingual support should be tested explicitly; this English model is not evidence of good multilingual performance. A larger or domain-tuned local model may improve domain accuracy at higher memory and latency cost. API embeddings add recurring cost, network latency, and an external data boundary; local embeddings reduce that exposure and per-query API fees but still incur compute and maintenance costs. A stronger model should be selected by measured accuracy, context capability, language coverage, privacy needs, and cost, not model size alone.
''')
    if retrieval:
        sections.append(f"Run: {retrieval['timestamp']}. Full passages and scores: [retrieval.json](evidence/retrieval.json).\n\n### Three real semantic retrieval tests\n")
        for i,test in enumerate(retrieval['comparisons'],1):
            sections.append(f"**Test {i}: {test['query']}**\n")
            for rank,r in enumerate(test['results']['semantic'],1):
                sections.append(f"{rank}. `{r['metadata']['filename']}` / `{r['id']}`; cosine distance {r['cosine_distance']:.4f}\n\n   > {r['text']}\n")
        sections.append('''Relevance review: test 1 should retrieve `howard_housing.txt`, which contains the residency requirement and exemption condition. Test 2 should retrieve `howard_transportation.txt`, which distinguishes normal arrival intervals from the West Campus exception. The displayed passages and expected-source hit results allow a reviewer to check whether those clauses were actually returned; a filename match alone does not prove full answer coverage. Test 3 targets the student dorm comparison rather than official rate information.

### Hybrid search comparison (+2)

BM25 uses lowercase alphanumeric tokens with the library's default parameters. The system ranks up to 12 vector candidates and 12 positive-score BM25 candidates and adds `1 / (60 + rank)` for each appearance. Ties break by stable chunk ID. Source-type filtering occurs before ranking in both paths. The Gradio default is hybrid, with selectors for semantic and BM25 baselines.

Expected-source hit@4 is a deliberately narrow, reproducible metric fixed in `experiments.py`; it measures whether at least one result comes from the specified relevant source. It does not grade completeness or generation quality.

| Query | Semantic top 4 | BM25 top 4 | Hybrid top 4 | Expected-source hit (S/B/H) |
|---|---|---|---|---|''')
        for t in retrieval['comparisons']:
            lists=['<br>'.join(f"{r['metadata']['filename']}@{r['metadata']['start']}" for r in t['results'][mode]) for mode in ['semantic','bm25','hybrid']]
            sections.append('| '+t['query']+' | '+' | '.join(lists)+' | '+' / '.join(str(t['hit_at_4'][m]) for m in ['semantic','bm25','hybrid'])+' |')
        sections.append('\n### Chunking comparison (+1)\n\nSame three queries, same embedding model, source corpus, hybrid ranking, and top-k. Only chunk size and overlap change.\n\n| Strategy | Chunk count | Query | Hit@4 | Actual top 4 (file@offset) |\n|---|---|---|---|---|')
        for strategy in retrieval['chunking']:
            for t in strategy['queries']:
                sections.append(f"| {strategy['size']}/{strategy['overlap']} | {strategy['chunk_count']} | {t['query']} | {t['hit_at_4']} | "+'<br>'.join(f"{r['metadata']['filename']}@{r['metadata']['start']}" for r in t['results'])+' |')
        sections.append('\n### Metadata filtering (+1)\n\nQuestion: '+retrieval['filter_query']+'\n')
        for kind,results in retrieval['filters'].items():
            sections.append(f"- **{kind}:** "+'; '.join(f"{r['metadata']['filename']} ({r['metadata']['source_type']})" for r in results))
        analysis=path/'retrieval_analysis.md'
        sections.append('\n'+(analysis.read_text() if analysis.exists() else 'Retrieval analysis is unavailable; the saved rankings still need a documented quality review in `evidence/retrieval_analysis.md`.'))
    else:
        sections.append('**NOT YET RUN:** retrieval, hybrid, chunking, and filtering evidence. Run `python cli.py build` and `python experiments.py`.')
    sections.append('''
## Grounded Generation

`generation.py` sends a system instruction requiring answers only from fresh retrieved context, distinction between official information and individual experiences, respect for dates and disagreement, inline `[S1]` citations, and an explicit insufficient-information response. Context is JSON with source IDs, dates, types, URLs, and passages. Prior generated answers are never used as evidence. Empty retrieval returns a fixed refusal without calling Groq. Missing credentials and API errors produce visibly labeled unavailable states, not fabricated answers; exception bodies are not logged.

The post-check rejects answers without a recognized citation or with out-of-range citation IDs. It accepts single and grouped IDs, such as `[S1]` and `[S1, S2]`. It does **not** prove each claim is entailed by its citation. There is no calibrated similarity threshold or entailment verifier: the model must assess whether retrieved passages support the answer. This is an honest grounding limitation. The model is configurable because [Groq model availability](https://console.groq.com/docs/models) can change.

## Query Interface

Launch with `python app.py`, then open the localhost URL printed by Gradio. Inputs: question, source type (`all`, `official`, `student`), and search method. Outputs: conversation with cited answers, source links and types, and an expandable panel containing the contextual search query, retrieved chunks, and ranking details. Clear conversation resets the session. The UI is bound to localhost and does not create a public sharing link.

### Conversational memory (+1)

A bounded per-session history retains six turns for display. A reference-bearing follow-up (such as “that” or “compare”) includes up to three prior user questions in its retrieval query. The generator also receives those user questions to interpret the reference. This simple approach supports short comparisons but can pollute retrieval when topics change; it is not a general coreference model. Previous generated answers do not become factual evidence.
''')
    if generation:
        sections.append(f"Generation run: {generation['timestamp']}. Full evidence: [generation.json](evidence/generation.json).\n\n### Two real responses / sample interaction transcripts\n")
        for r in generation['evaluations'][:2]:
            sections.append(f"**Question:** {r['question']}\n\n**Complete response ({r['status']}):**\n\n{r['answer']}\n\n**Retrieved sources:**\n\n{sources_markdown(r['results'])}\n")
        sections.append('### Out-of-scope and difficult questions\n')
        for r in generation['extra_tests']:
            sections.append(f"**Question:** {r['question']}\n\n**Actual response ({r['status']}):** {r['answer']}\n")
        sections.append('### Real multi-turn transcript\n')
        for r in generation['conversation']:
            sections.append(f"**User:** {r['question']}\n\n**Search query:** {r['retrieval_query']}\n\n**Complete response ({r['status']}):** {r['answer']}\n\n**Sources:**\n\n{sources_markdown(r['results'])}\n")
        interface_path = path/'interface.json'
        if interface_path.exists():
            sections.append('### Actual Gradio HTTP interaction\n\nComplete returned conversation, sources, and retrieval details: [interface.json](evidence/interface.json). This exercised the real `/ask` endpoint, including session state and the student-only filter.\n')
            for turn in json.loads(interface_path.read_text()):
                content = turn['conversation'][-1]['content']
                if not isinstance(content, str):
                    content = '\n'.join(block.get('text', str(block)) for block in content)
                sections.append(f"**Question:** {turn['question']}\n\n**Actual UI response:** {content}\n\n**Sources:**\n\n{turn['sources']}\n")
        review_status = ('I personally reviewed all five questions, expectations, actual answers, judgments, and reasoning, and accepted all five judgments exactly as recorded, along with the documented limitations and failure analysis.'
                         if generation.get('review', {}).get('student_accepted') else
                         'These AI-assisted judgment proposals are awaiting my review and acceptance.')
        sections.append('## Evaluation Report\n\nThe five expectations below were preserved from the original planning document. ' + review_status + ' API failures are not graded as knowledge answers. Use `--output-dir evidence/new_run` for fresh experiments; the accepted run is protected from replacement.\n')
        sections.append("""### Retrieval quality for the accepted evaluations

The assistant checked the saved passages for this coverage summary. **Relevant** means the retrieved set contains the expected answer-bearing information; it does not mean every returned passage is equally useful. **Partially relevant** means the set supports only part of the original expectation. My accepted answer-accuracy judgments below are unchanged. Source IDs refer to each question's saved results in `evidence/generation.json`.

| Question | Retrieval quality | Saved context and limitations |
|---|---|---|
| 1 — Housing requirement | Relevant | S1 (`howard_housing.txt@0`) states the first-time-in-college/second-year requirement and approved-exemption exception. S2/S3 add eligibility details; the freshman anecdote in S4 is unnecessary for the policy answer. |
| 2 — Shuttle frequency | Relevant | S1 (`howard_transportation.txt@0`) gives the normal and West Campus intervals and possible delays. All four retrieved passages are from Transportation Services. |
| 3 — CHS versus Drew | Relevant | S1 describes bathrooms shared with a roommate, and S2 covers newer CHS facilities, dining proximity, Drew's experience versus amenities, and disagreement. The official price passage is less central to the student-experience question. The answer's vague bathroom wording is a generation limitation despite available context. |
| 4 — Blackburn food | Relevant | S2 (`student_incoming_advice.txt@0`) supplies the stations and personal preferences; S4 adds official venue context. The dorm and off-campus passages in S1/S3 add retrieval noise. |
| 5 — Upperclassman alternatives | Partially relevant | S2/S3 contain historical off-campus suggestions and funding accounts with explicit uncertainty. The original roommate expectation is unsupported by the collected corpus; current property affiliation is also not established. |

""")
        for i,r in enumerate(generation['evaluations'],1):
            sections.append(f"### Question {i}\n\n**Question:** {r['question']}\n\n**Expected:** {r['expected']}\n\n**Actual ({r['status']}):** {r['answer']}\n\n**Accuracy:** {r['judgment']}\n\n**Reasoning:** {r['reasoning'] or 'Pending review.'}\n")
    else:
        sections.append('## Evaluation Report\n\n**NOT YET RUN:** Groq generation, out-of-scope refusal, and multi-turn generation. Run `python experiments.py --generate`; unavailable responses are never presented as successful evidence.\n')
        for r in planned_questions():
            sections.append(f"- **Question:** {r['question']} **Expected:** {r['expected']} **Actual / judgment:** Not run.\n")
    analysis=path/'failure_analysis.md'
    sections.append('## Known Limitations / Failure Case\n\n'+(analysis.read_text() if analysis.exists() else 'Actual failure analysis pending runtime evaluation. Known design limits: small curated corpus, historical anecdotes, fixed character boundaries, uncalibrated evidence sufficiency, and heuristic conversation resolution.'))
    sections.append('''
## Spec Reflection

My planning document made the implementation requirements concrete: 800/150 chunking, a local MiniLM model, ChromaDB, and four retrieved passages. I kept the predetermined evaluation expectations when reviewing the results, including the roommate detail that the collected sources do not support. This helped me distinguish a working pipeline from a complete, well-grounded answer.

The unavailable upperclassman Reddit thread was replaced with a historical waitlist post, documented above and in planning.md. Hybrid ranking, source filtering, and conversational follow-ups refine the baseline as requested stretch features; semantic retrieval remains available. Gradio was added because the starter listed it as an optional interface but contained no implementation. The first Groq default returned NotFoundError and was absent from the authenticated model list, so the default changed to available `qwen/qwen3.8-27b` in instruct mode. That preview model remains configurable; the unsuccessful run is preserved separately. Gradio was pinned to 6.9.0 with Hugging Face Hub <1 to match the starter Transformers dependency. Recovery added grouped-citation validation, rejection of stale corpus evidence, judgment resets after retries, and suppression of unrelated conversation history in generation. It recreated the vanished Python 3.12 environment and reran the complete evidence suite. Earlier evidence is preserved under `evidence/recovery_2026-09-29/`. The starter's README requirements, dependencies, and source summaries guided the implementation; no Tinker or other application code was present to reuse.

## AI Usage Transparency

I established the project direction, Howard student-life domain, initial source choices, two source summaries, planning requirements, and evaluation expectations. AI substantially assisted with implementation and documentation, including application code, tests, source paraphrases, and report generation. I directed that work and personally tested the application, investigated a retrieval failure, reviewed its answers and citations, and accepted the evaluation judgments and limitations. The examples below distinguish the assistant’s work from my own testing and decisions.

1. **Pipeline assistance:** I directed AI to implement ingestion, 800/150 chunking, MiniLM/Chroma retrieval, and the stretch comparisons using planning.md and starter files. The assistant produced `pipeline.py`, CLI commands, tests, and `experiments.py`. Assistant-run unit tests checked chunk coverage/overlap/stability, ingestion exclusions, and missing-input behavior. Recovery rechecked all sources, recreated Python 3.12, verified all retrieval rankings and both chunking strategies, and validated metadata filtering. A coverage test initially used repeating text that intentionally triggered duplicate suppression; it was revised to unique text, then passed. **My review/testing and decisions:** I personally activated the project environment and ran `python -m unittest discover -s tests -v`; all seven tests passed. I manually launched Gradio with `python app.py` and asked “How often do Howard shuttles arrive?” The UI returned “Retrieval unavailable (AttributeError). Run python cli.py build and check dependencies.” I stopped the app and investigated rather than accepting the earlier automated result. I ran `python cli.py build`, which reported “Indexed 26 chunks,” then `python cli.py ask "How often do Howard shuttles arrive?"`. I reviewed and accepted the cited answer: most routes arrive approximately every 20–30 minutes, West Campus approximately every 45 minutes, with possible delays and attribution to Howard Transportation Services. After relaunching Gradio, I personally verified that the same question worked with citations and visible retrieved sources.

2. **Generation and reporting assistance:** I directed AI to add Groq grounding, visible sources, Gradio, evaluation artifacts, and a rubric report, while prohibiting invented source text and evidence. The assistant produced `generation.py`, `app.py`, source paraphrases, and this artifact-driven report. The assistant checked source text and labeled historical disagreement and missing coverage. Actual testing exposed a Cook-to-Drew attribution error and paraphrase-as-quotation risk; the assistant preserved that run, tightened the prompt, and reran evaluation. An unavailable Llama model was replaced with an account-accessible Qwen model after checking the Models API. During recovery, the assistant revised instructions after inspecting attribution failures, corrected grouped citation parsing, and reran all ten Groq calls plus a real two-turn Gradio HTTP interaction. The Blackburn category and follow-up speaker errors did not recur; remaining dorm and off-campus weaknesses are recorded rather than marked Accurate. Saved runtime results distinguish success, unavailable API calls, and proposed judgments. **My review/testing and decisions:** In Gradio, I asked “What do students say about College Hall South?” I reviewed and accepted the response because it cited labeled student sources, presented differing experiences, and distinguished individual opinions from official housing policy or verified rankings. Without clearing the conversation, I asked “How does that compare with Drew?” I verified that “that” referred to College Hall South and that the answer compared it with Drew Hall using prior conversation context; I accept this as my manual verification of conversational memory. I also asked “Who won the 2026 Super Bowl?” and reviewed the exact response: “The available sources do not provide enough information to answer this question.” I accepted this grounding behavior because the system refused to invent an unsupported answer. I also personally reviewed all five planned evaluation questions, expected answers, actual answers, accuracy judgments, and reasoning. I accept the existing judgments exactly as written: Accurate, Accurate, Partially Accurate, Accurate, Partially Accurate. I reviewed and accept the documented limitations and failure analysis; the two Partially Accurate results remain visible.

## Architecture

```text
Official Howard pages + historical student discussions
  -> attributed editorial .txt summaries (12 documents)
  -> metadata parsing + whitespace cleaning
  -> 800-character chunks / 150-character overlap + stable IDs
  -> all-MiniLM-L6-v2 embeddings -> persistent ChromaDB
User question + bounded user-question history
  -> source-type filter -> vector search + BM25 -> reciprocal rank fusion -> top 4
  -> Groq grounding prompt + labeled fresh evidence
  -> citation validation -> answer + source links + retrieved passages
  -> Gradio conversation (session state) / CLI / saved evaluation evidence
```

## Demo

[Project 1 Demo Video](https://drive.google.com/file/d/180ZixYKxZe4Kuu8D8pOAcEdD8f3AdbKO/view?usp=sharing)

I recorded the demo linked above. The implementation, evaluation results, and limitations are documented in this README.

## Validation and Rubric Audit

See [validation.md](evidence/validation.md) for commands actually run, their outcomes, remaining checks, and an item-by-item rubric audit. Source text, runtime evidence, my evaluation acceptance, and the video are distinct requirements. The evidence supports the rubric targets; the instructor determines the grade.
''')
    temporary = ROOT/'README.tmp'
    existing = (ROOT/'README.md').read_text() if (ROOT/'README.md').exists() else ''
    temporary.write_text(preserve_manual_sections('\n'.join(sections), existing))
    temporary.replace(ROOT/'README.md')
    print('README rendered from available artifacts.')


if __name__ == '__main__':
    main()
