import gradio as gr
from utils.utils import format_notification, is_empty_string


def TextboxSubmitComponent(
        textbox_label: str | None = "Input Text",
        textbox_value: str | None = None,
        button_label: str = "Submit Value", placeholder: str | None = None,
        notification_message: str | None = "Success!"):

    with gr.Group(visible=False) as textbox_submit_group:
        with gr.Row():
            textbox_input = gr.Textbox(
                label=textbox_label,
                value=textbox_value,
                placeholder=placeholder,
                interactive=True,
                scale=3
            )

            submit_btn = gr.Button(button_label, scale=1, interactive=False)

    notification_text = gr.Markdown(
        value=format_notification(
            notification_message) if notification_message else "",
        visible=False
    )

    textbox_input.change(
        lambda text: gr.Button(
            interactive=(not is_empty_string(text))
        ),
        inputs=[textbox_input],
        outputs=[submit_btn]
    )

    submit_btn.click(lambda: ([
        gr.Textbox(value=None),
        gr.Markdown(visible=True)
    ]), outputs=[
        textbox_input,
        notification_text
    ])

    return textbox_submit_group, textbox_input, submit_btn, notification_text
