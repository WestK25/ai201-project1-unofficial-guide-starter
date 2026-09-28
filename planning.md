# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (ChatGPT, Claude, Copilot, etc.) to generate your implementation.
> Update the Retrieval Approach and Chunking Strategy sections if the approach changes during implementation.
> Update this file before starting any stretch features.

---

## Domain

My domain is **Howard University student life and campus survival**. The goal is to create an unofficial guide that helps current and incoming Howard students find useful information about housing, dining, transportation, campus life, and common student experiences.

This knowledge is valuable because official Howard University resources explain policies and services, but they do not always explain what students actually experience when using them. Student discussions on Reddit and other student-focused sources can provide perspectives about residence halls, dining, transportation, housing assignments, and navigating campus life that may be difficult to find through official channels.

The RAG system will combine these different sources so a student can ask a normal question and receive a grounded answer based only on the documents in the collection, with the sources identified in the response.

---

## Documents

The initial corpus will contain at least 10 sources covering both official Howard information and student perspectives.

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Howard University Housing Application | Official information about applying for housing, fees, eligibility, and housing requirements. | https://studentaffairs.howard.edu/housing/apply-housing |
| 2 | Howard University Transportation Services | Official information about campus shuttles, routes, tracking, frequency, and rider requirements. | https://auxiliary.howard.edu/services/parking-transportation/transportation-services |
| 3 | Howard Bison One Card & Meal Plans | Official information about meal plans, dining, laundry, Bison Bucks, and uses of the Bison One Card. | https://studentaffairs.howard.edu/housing/move-in/bison-one-card-meal-plans |
| 4 | Howard University Move-In Instructions | Official information about residence hall move-in, check-in, parking, guests, and move-in procedures. | https://studentaffairs.howard.edu/housing/move-in/instructions |
| 5 | Howard University 2026-27 Student Charges | Official information about housing and meal-plan costs and eligibility. | https://financialservices.howard.edu/official-notice/student-charges-2026-27 |
| 6 | r/HowardUniversity — "What should incoming Howard students know?" | Student discussion about community, food, internships, safety, and navigating Howard. | https://www.reddit.com/r/HowardUniversity/comments/1c6h31d/ |
| 7 | r/HowardUniversity — "Resident hall recommendations" | Student opinions about College Hall North/South, Annex, Quad, Drew, Cook, kitchens, and bathrooms. | https://www.reddit.com/r/HowardUniversity/comments/1snfwjv/resident_hall_recommendations/ |
| 8 | r/HowardUniversity — "What's the best dorm for Incoming Freshman Male?" | Student perspectives comparing Drew, Cook, College Hall South, and other freshman housing. | https://www.reddit.com/r/HowardUniversity/comments/1sa2az5/ |
| 9 | r/HowardUniversity — "Housing for Freshman" | Student discussion about freshman housing assignments, preferences, and roommates. | https://www.reddit.com/r/HowardUniversity/comments/1s9ygvz/housing_for_freshman/ |
| 10 | r/HowardUniversity — "How does off campus housing work?" | Student discussion about paying for off-campus housing, employment, loans, refunds, and housing options. | https://www.reddit.com/r/HowardUniversity/comments/1l41ecq/ |
| 11 | r/HowardUniversity — "Advice for New Applicants" | Student discussion describing residence hall visitation, mail, dining, and other day-to-day experiences. | https://www.reddit.com/r/HowardUniversity/comments/1jyjivj/ |
| 12 | r/HowardUniversity — "Upperclassman Housing" | Student discussion about housing availability for upperclassmen and off-campus alternatives. | https://www.reddit.com/r/HowardUniversity/comments/1txvuw9/ |

---

## Chunking Strategy

**Chunk size:** 800 characters

**Overlap:** 150 characters

**Reasoning:**

The corpus contains a mixture of relatively short Reddit posts/comments and longer official Howard University information pages. A chunk size of approximately 800 characters should be large enough to preserve a complete student experience, recommendation, policy explanation, or short group of related facts without creating chunks that contain too many unrelated topics.

A 150-character overlap will preserve context when an important sentence or explanation falls near a chunk boundary. This is especially useful for Reddit discussions, where a comment may contain several connected sentences, and official pages, where a policy may be explained across adjacent paragraphs.

This strategy will be evaluated during testing. If important information is consistently split between chunks or retrieval returns overly broad passages, the chunk size or overlap will be adjusted and the change documented here.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` using the `sentence-transformers` library.

**Top-k:** 4 chunks per query.

**Production tradeoff reflection:**

For this project, `all-MiniLM-L6-v2` provides a useful balance between semantic retrieval quality, speed, and the ability to run locally without paying for an embedding API.

For a production deployment, I would compare models based on retrieval accuracy, latency, cost, context limitations, multilingual support, and performance on informal student language. This corpus contains both formal university language and informal Reddit language, so a stronger model may better connect questions written in conversational language with relevant formal documents.

I would also consider whether embeddings should be generated locally or through an API. A local model can reduce API cost and improve privacy, while a hosted model may provide better retrieval performance at the cost of latency, dependence on an external service, and potentially higher operating costs.

---

## Evaluation Plan

The following five questions will be used to evaluate retrieval and grounded generation. The expected answers are defined before implementation so that the system can be judged against predetermined information rather than changing the expected result after seeing the model's response.

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Are first-year and second-year Howard students required to live in university housing? | Yes. Howard's housing information states that first-time-in-college and second-year students are required to live in University Housing or University-sponsored housing unless they receive an approved exemption. |
| 2 | How often do Howard shuttles usually arrive, and is the West Campus shuttle different? | Most Howard shuttle routes arrive approximately every 20–30 minutes, while the West Campus shuttle generally arrives approximately every 45 minutes. Actual arrival times can vary. |
| 3 | What do students say are some differences between College Hall South and Drew Hall for freshmen? | Student discussions generally describe College Hall South as a newer option with private/shared-suite bathroom advantages and convenient access to dining, while Drew is often recommended more for the social or traditional freshman experience than for its amenities. |
| 4 | What do Howard students say about the food options at Blackburn? | Student discussion describes Blackburn as having several options such as build-your-own stations, a vegan station, salad, waffles, and a changing hot-food line. Opinions about quality vary by student and station. |
| 5 | If an upperclassman does not receive Howard housing, what alternatives do students discuss? | Student discussions mention finding off-campus apartments, living with roommates, using income from part-time work or financial-aid refunds toward rent, and considering student-oriented or Howard-affiliated housing options. These are student experiences rather than guarantees from the University. |

---

## Anticipated Challenges

1. **Official information and student experiences may conflict.** Official Howard pages describe policies and services, while Reddit comments describe individual experiences that may vary by person or year. The system must preserve source attribution and avoid presenting a student's opinion as an official university policy.

2. **Informal student language may reduce retrieval quality.** Reddit posts may use abbreviations such as "CHS," "CHN," or "the Quad," while official documents may use full residence hall names. Semantic embeddings should help connect these terms, but retrieval tests will be used to identify cases where terminology causes relevant chunks to be missed.

3. **Chunk boundaries may separate important context.** A student's recommendation or an official policy explanation could be divided between two chunks. The planned overlap should reduce this risk, but sample chunks and evaluation results will be reviewed to determine whether the strategy needs adjustment.

4. **Some information can change over time.** Housing procedures, transportation schedules, meal plans, and student experiences may change between academic years. Source names and metadata will therefore be preserved so users can see where the retrieved information came from.

---

## Architecture

```text
Official Howard Pages + Student Discussions
                    |
                    v
        +-----------------------+
        |  Document Ingestion   |
        | Python text loading   |
        | + basic cleaning      |
        +-----------------------+
                    |
                    v
        +-----------------------+
        |       Chunking        |
        | 800 characters        |
        | 150-char overlap      |
        +-----------------------+
                    |
                    v
        +-----------------------+
        |      Embedding        |
        | all-MiniLM-L6-v2      |
        | sentence-transformers |
        +-----------------------+
                    |
                    v
        +-----------------------+
        |     Vector Store      |
        |       ChromaDB        |
        +-----------------------+
                    |
              User Question
                    |
                    v
        +-----------------------+
        |       Retrieval       |
        | Embed query + search  |
        | Top 4 chunks          |
        +-----------------------+
                    |
                    v
        +-----------------------+
        |      Generation       |
        |      Groq LLM         |
        | Retrieved context     |
        | + grounding prompt    |
        +-----------------------+
                    |
                    v
        Grounded Answer + Sources