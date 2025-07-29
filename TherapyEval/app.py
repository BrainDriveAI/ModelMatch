import gradio as gr
from ui import create_app

# Local entry point
if __name__ == "__main__":
    demo = create_app()
    demo.launch(server_name="127.0.0.1", server_port=7860, show_error=True, share= True)
