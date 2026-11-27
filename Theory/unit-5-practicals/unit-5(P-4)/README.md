# Unit 5 (P-4): Assignment III, Presentation Architecture and Evidence (Lecture 59)

Lecture 59 has **no coding task**: you prepare an 8 to 12 slide, 15-minute presentation on your assigned advanced topic and your draft is peer-reviewed. So this folder is a preparation kit, not a program.

| File | What it is |
|---|---|
| `PRESENTATION_GUIDE.md` | the blueprint, the required-content checklist, a 15-minute plan, where to find evidence for each topic, rehearsal checklist |
| `templates/slide-outline-template.md` | a fill-in outline (slide table, diagram description, trade-off table, Q&A, contributions, annotated references) |
| `examples/event-driven-serverless/` | a complete **worked example** on event-driven serverless: 12-slide outline with timings, the main diagram (`architecture.mmd` source, `.svg`, `.png`), comparison slide, Q&A, annotated references |
| `PEER_REVIEW_RUBRIC.md` | the rubric for reviewing a classmate's draft (conceptual clarity, diagram accuracy, evidence, originality, timing, equal participation, reference quality) |

## What I did not do, and why
- **Your topic was not in the files you sent**, and the actual presentation, team split and real contributions are yours. I did not fill the template for you or pretend to know your assigned topic. Tell me the topic and I can draft the slide outline for it.
- **The worked example is a model, not a submission.** It is built from the practicals in this repository, so every technical claim on it points to a test or file you can run. The "real-world example" slide is deliberately left for you to source: I did not invent a company case study.
- **No slide deck file** is included. The outline is written to be pasted into PowerPoint, Google Slides or similar; say if you want it built as a deck.
- **References:** only two web pages were opened and read for the example (AWS Lambda SQS error handling; Lambda runtimes). Check every link yourself and read each source before you cite it.

## Using the Mermaid diagram
`architecture.png` and `architecture.svg` are ready to insert. To change the diagram, edit `architecture.mmd` and re-render with `npx -p @mermaid-js/mermaid-cli mmdc -i architecture.mmd -o architecture.png -b white -s 2`, or paste the text into any Mermaid editor.
