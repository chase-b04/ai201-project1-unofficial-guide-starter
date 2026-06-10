# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

The domain I choose was off campus housing. This knowledge is valuable because when I was once looking for an off-campus house, there was a lot of options, all of them would try to pressure buyers to sign with them asap, making them think the prices would skyrocket after a certain date or that they would run out of spots in October. This is far from true, as these off campus housing locations have deals and openings even in the Spring semester. Because of this, I wish I had more condensed information, more knowledge of the deals these complexes run, and knew about some apartments that I had only learned about after I signed a lease.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| #   | Source                 | Description                                                             | URL or location                                                                                          |
| --- | ---------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 1   | asu.edu                | Official ASU off-campus housing search and listing portal.              | https://offcampushousing.asu.edu/                                                                        |
| 2   | Reddit                 | Student discussion about off-campus apartment recommendations near ASU. | https://www.reddit.com/r/ASU/comments/y6pbzt/offcampus_apartments/                                       |
| 3   | forrentuniversity.com  | Rental listings near ASU Downtown Phoenix campus.                       | https://www.forrentuniversity.com/Arizona-State-University-Downtown-Phoenix-Campus                       |
| 4   | offcampus-universe.com | Affordable off-campus housing options for Arizona State students.       | https://www.offcampus-universe.com/post/asu-affordable-housing-options-for-students                      |
| 5   | Reddit                 | Advice and experiences on ASU off-campus accommodation.                 | https://www.reddit.com/r/ASU/comments/1lea94p/offcampus_accommodation_help/                              |
| 6   | Facebook               | Community group post for ASU housing rentals.                           | https://www.facebook.com/groups/asu.off.campus.housing.arizona.state.rentals/posts/2081825209009541/     |
| 7   | gyandhan.com           | Tips for choosing off-campus housing near ASU Tempe.                    | https://discussions.gyandhan.com/t/things-to-know-before-picking-off-campus-housing-near-asu-tempe/16496 |
| 8   | ramblertempe.com       | Guide to popular housing options for ASU students.                      | https://ramblertempe.com/resources/where-do-asu-students-live-housing-options-beyond-greek-housing/      |
| 9   | Reddit                 | Student recommendations for best off-campus apartments near ASU.        | https://www.reddit.com/r/ASU/comments/1jqarh9/best_offcampus_apartments/                                 |
| 10  | nau.edu                | NAU's off-campus housing and roommate listing service.                  | https://louieslist.nau.edu/                                                                              |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500

**Overlap:** 100

**Why these choices fit your documents:** These choices fit my document because my documents where quite long and contained a lot of different characters, thus bigger chunks to break down my documents would retrieve better information. 100 overlap is good for reducing the risk of information being split while the chunks where being made.

**Final chunk count:** A chunk size of 500 characters balances semantic completeness with retrieval precision by keeping related information together while avoiding overly large chunks that may contain multiple topics. A 100-character overlap preserves context across chunk boundaries and reduces the risk of important information being split between adjacent chunks. This configuration works well for general text documents, FAQs, and web content where relevant information is often contained within a few paragraphs.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2

**Production tradeoff reflection:** The all-MiniLM-L6-v2 model provides a good balance between retrieval quality, speed, and computational cost, making it well suited for educational and prototype RAG systems. Retrieving the top 5 chunks generally provides enough context for answer generation while limiting irrelevant information. The tradeoff is that larger models typically require more memory, increase embedding latency, and raise infrastructure costs, so the choice would depend on application requirements and expected query volume.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** In my query.py build_prompt() function, I prompt the model to not invent facts of use outside knowledge with "Do NOT invent facts or use outside knowledge beyond what is written below." and to only say it doesn't have enough info if it doesn't and no other relevant information with "if the documents contain NO relevant information whatsoever.", which the model did struggle with in hindsight.

**How source attribution is surfaced in the response:** In \_build_prompt(), each chunk is labeled before being sent to the model with "f"[Document {i} — source: {hit['source']}]\n{hit['text']}"," as the prompt instructs the model to cite its sources. As for the UI, in app.py, the ask() function is called a few times like "result = ask(question)" to return metadata from the retrieved chunks and seperate them as sources.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| #   | Question                                                                                                      | Expected answer                                                                                                    | System response (summarized)                                                                                                                                                                                                                                                               | Retrieval quality   | Response accuracy   |
| --- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- | ------------------- |
| 1   | What should students know before signing a lease for off-campus housing near ASU?                             | Lease, times to sign the lease, and potential costs                                                                | The system cited 6 documents/websites, discusses leases, roomate relationships, rental responses, move-in planning, furniture and common off-campus housing questions in a good grounded response.                                                                                         | Relevant            | Accurate            |
| 2   | What concerns do students raise about choosing off-campus housing near ASU Tempe?                             | Cost, commute distance, roommates, safety, and lease terms.                                                        | Uses 3 documents to reference overwhelming processes, safety, funishment, commutes, and a concern if they made the right choice. Ends with a summary line after the three cites responses.                                                                                                 | Relevant            | Accurate            |
| 3   | What are the pros and cons of living in off-campus student apartments versus traditional apartments near ASU? | On-Campus might be cheaper, Off-Campus is full year round, has ammenities, and provides a better living experience | References 4 documents talking about the broader community, amenities, space of the living areas, and the price ranges for on campus versus off campus.                                                                                                                                    | Relevant            | Accurate            |
| 4   | What neighborhoods near ASU Tempe are most popular for student housing?                                       | Real places around Tempe and reviews around them                                                                   | Did not return housing but instead returned 3 chunked responses with a summary response that references 3 documents about the areas of Tempe, but does mention the name of any actual neighborhoods in the area.                                                                           | Partially relevant  | Inaccurate          |
| 5   | What alternatives to Greek housing are discussed in the Rambler Tempe article?                                | Off-campus apartments, student communities, and shared housing options.                                            | Only one response is returned referencing 1 doc twice as two documents for some reason but does provide real context, afterwards it mentions the rest of the documents information, but states it's irrelevance to one specific document, showing that it is over relying on that article. | Partially relevant. | Partially accurate. |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** What advice do students give international students seeking off-campus accommodation in the Reddit help thread?

**What the system returned:** I don't have enough information on that.

According to the provided documents, there is no information from a Reddit help thread. The documents provided are from various sources (rambler.txt, asu.txt, and universe.txt), but none of them are specified as a Reddit thread (the closest being Document 1, which does not contain the file name "reddit-grad.txt" as mentioned in the prompt, but rather "rambler.txt").

**Root cause (tied to a specific pipeline stage):** No mentions of international student help in any documents/articles

**What you would change to fix it:** I would try to add a better source that provides context on housing help for international students.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Planning md helped a lot as it allowed me to plan out my chunking and retrival strategies.

**One way your implementation diverged from the spec, and why:** My implementation diverged from my spec because of my TOP K value, as I had planned for 5, but ended up implementing 8.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- _What I gave the AI:_ I gave Claude my Chunking Strategy section from planning.md and asked it to implement chunk_text() with a chunk size of 500 and an overlap of 100
- _What it produced:_ It returned a chunk_text(), clean_text(), and load_documents() in ingest.py, as these functions would ultimately return fixed split characters.
- _What I changed or overrode:_ I changed the chunk_text(), adding more splits to try to remove even more unicode that was being returned by the chunking function.

**Instance 2**

- _What I gave the AI:_ I gave claude my Retrieval strategy section from planning.md as well as my mermaid document and told it to implement a retrieve() function.
- _What it produced:_ It produced a retrieve function that retrieved embed the chunks and create queries that are on topic from the sources. In turn it had also built a build_vector_store() to handle my ChromaDB database.
- _What I changed or overrode:_ I overrode my test queries to add my actual questions I wanted to ask it, instead of some older and default questins that didn't produce enough info.
