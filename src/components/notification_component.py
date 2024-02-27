import gradio as gr

from utils.utils import format_notification


def NotificationComponent(value: str = "", label: str | None = None):
    notification_text = gr.Markdown(
        label=label,
        value=format_notification(value),
        elem_classes=['processing-text'],
        visible=False
    )

    return notification_text
