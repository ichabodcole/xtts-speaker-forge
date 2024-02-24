import gradio as gr

from utils.utils import format_notification


def TextboxSubmitComponent(textbox_label: str | None = "Input Text", button_label: str = "Submit Value", placeholder: str | None = None, notification_message: str | None = "Success!"):
    with gr.Group(visible=False) as textbox_submit_group:
        with gr.Row():
            textbox_input = gr.Textbox(
                label=textbox_label,
                placeholder=placeholder,
                interactive=True,
                scale=3
            )

            submit_btn = gr.Button(button_label, scale=1)

    notification_text = gr.Markdown(
        value=format_notification(
            notification_message) if notification_message else "",
        visible=False
    )

    return textbox_submit_group, textbox_input, submit_btn, notification_text
