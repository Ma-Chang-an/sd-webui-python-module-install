import launch
import gradio as gr
from modules import paths, shared, script_callbacks, scripts, images


tsinghua_url = 'https://pypi.tuna.tsinghua.edu.cn/simple/'
install_path = '/mnt/auto/sd/python'
def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as module_installer:
        create_ui()

    return (module_installer, "Python Module Installer", "python module installer"),


def create_ui():

    with gr.Column():
        with gr.Row(scale=1):
            name_box = gr.Textbox(label="Module Name", placeholder="module name to install")
        with gr.Row(scale=1):
            version_box = gr.Textbox(label="Module Version", placeholder="module version to install")
        with gr.Row(scale=1):
            install_button = gr.Button(value="Install", variant='primary')

    with gr.Row():
        with gr.Column(scale=10):
            warning_box = gr.HTML("", elem_id=f"module_installer_warning_box", elem_classes="moduleInstallerWarning")

    install_button.click(
        fn=module_install,
        inputs=[name_box, version_box],
        outputs=[warning_box],
        show_progress=True
    )


def module_install(name_box, version_box):
    result = "<div style='color:#999; font-size:10px' align='center'>"
    if name_box == "":
        result += f"please input module name you would like to install</div>"
        return result

    module_name = name_box if version_box == "" else name_box + "==" + version_box
    install_module(name_box, version_box)
    result += f"{module_name} install success</div>"
    return result


def install_module(module_name, version_box):
    if not launch.is_installed(module_name):
        module = module_name if version_box == "" else module_name + "==" + version_box
        index_url = f'--index-url {launch.index_url}' if launch.index_url != '' else f'--index-url {tsinghua_url}'
        launch.run(f'"{launch.python}" -m pip install {module} -t {install_path} --prefer-binary {index_url}',
                   desc=f"Installing {module}",
                   errdesc=f"Couldn't install {module}")

    return True


script_callbacks.on_ui_tabs(on_ui_tabs)
