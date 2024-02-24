import gradio as gr


def NotificationComponent(value: str = "", label: str | None = None):
    notification_text = gr.Markdown(
        label=label,
        value=f"### _{value}_",
        elem_classes=['processing-text'],
        visible=True
    )

    return notification_text
