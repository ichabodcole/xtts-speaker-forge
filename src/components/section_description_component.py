import gradio as gr


def SectionDescriptionComponent(value: str, label: str | None = None):
    # Gradio 5 has updated Markdown styling but the API remains compatible
    return gr.Markdown(
        label=label,
        value=value,
        elem_classes=["section-description"]
    )
