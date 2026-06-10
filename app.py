"""
Milestone 5 — Gradio Web Interface
Run with: python app.py
Then open http://127.0.0.1:7860 in your browser.
"""

import gradio as gr
from query import ask


def handle_query(question: str):
    """Called by Gradio on every button click or Enter keypress."""
    question = question.strip()
    if not question:
        return "Please enter a question.", "", ""

    result = ask(question)

    answer = result["answer"]

    # Format sources as a bullet list
    sources_text = "\n".join(f"• {s}" for s in result["sources"])

    # Format retrieved chunks for the expandable details box
    chunk_lines = []
    for hit in result["chunks"]:
        chunk_lines.append(
            f"Rank {hit['rank']} | {hit['source']} | Chunk #{hit['chunk_index']} "
            f"| Distance: {hit['distance']:.4f} | {hit['chunk_size']} chars\n"
            f"{hit['text']}\n"
        )
    chunks_text = "\n---\n".join(chunk_lines)

    return answer, sources_text, chunks_text


# ---------------------------------------------------------------------------
# UI layout
# ---------------------------------------------------------------------------
with gr.Blocks(title="Off-Campus Housing Guide") as demo:

    gr.Markdown(
        """
        # Off-Campus Housing — Unofficial Guide
        Ask questions about off-campus housing in Arizona. Answers are drawn
        entirely from student reviews, Reddit threads, and housing articles —
        no AI hallucination, sources cited.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. Which apartments near ASU are most recommended by students?",
                lines=2,
            )
            ask_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_box = gr.Textbox(
            label="Answer",
            lines=8,
            interactive=False,
        )

    with gr.Row():
        sources_box = gr.Textbox(
            label="Retrieved from (sources)",
            lines=4,
            interactive=False,
        )

    with gr.Accordion("Retrieved chunks (for inspection)", open=False):
        chunks_box = gr.Textbox(
            label="Top chunks passed to the model",
            lines=20,
            interactive=False,
        )

    # Wire up button click and Enter key
    ask_btn.click(
        fn=handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box, chunks_box],
    )
    question_box.submit(
        fn=handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box, chunks_box],
    )

if __name__ == "__main__":
    demo.launch()
