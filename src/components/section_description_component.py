import gradio as gr


def SectionDescriptionComponent(value: str, label: str | None = None):
    return gr.Markdown(
        label=label,
        value=value,
        elem_classes=["section-description"]
    )
