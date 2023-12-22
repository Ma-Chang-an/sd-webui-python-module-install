import os
import shutil

import launch
import re
import subprocess
import importlib
import gradio as gr
from modules import paths, shared, script_callbacks, scripts, images

tsinghua_url = 'https://pypi.tuna.tsinghua.edu.cn/simple/'
default_install_path = '/mnt/auto/sd/python'
tmpdir = "/tmp"


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as module_installer:
        create_ui()

    return (module_installer, "Python Module Installer", "python module installer"),


def create_ui():
    with gr.Tab(label="Install By Name"):
        with gr.Column():
            checkbox = gr.CheckboxGroup(["Input Version", "Install Path", "Index URL"], show_label=False)
            name_box = gr.Textbox(label="Module Name", placeholder="module name to install")
            version_box = gr.Textbox(label="Module Version", placeholder="module version to install", visible=False)
            install_path = gr.Textbox(label="Install Path", visible=False, interactive=True,
                                      placeholder="path to install, default path is /mnt/auto/sd/python")
            index_url = gr.Textbox(label="Index URL", visible=False, interactive=True,
                                   placeholder="Index URL, default: https://pypi.tuna.tsinghua.edu.cn/simple/")
            install_button = gr.Button(value="Install", variant='primary')

    with gr.Tab(label="Install By Requirements"):
        checkbox2 = gr.CheckboxGroup(["Install Path", "Index URL"], show_label=False)
        file_upload = gr.File()
        install_path2 = gr.Textbox(label="Install Path", visible=False, interactive=True,
                                   placeholder="path to install, default path is /mnt/auto/sd/python")
        index_url2 = gr.Textbox(label="Index URL", visible=False, interactive=True,
                                placeholder="Index URL, default: https://pypi.tuna.tsinghua.edu.cn/simple/")
        install_requirement = gr.Button(label="Install", variant="primary")

    with gr.Row():
        with gr.Column(scale=10):
            warning_box = gr.HTML("install result", elem_id=f"module_installer_warning_box",
                                  elem_classes="moduleInstallerWarning")

    def checkbox_handler(input_str):
        a = version_box.update(visible=True) if "Input Version" in input_str else version_box.update(visible=False)
        b = install_path.update(visible=True) if "Install Path" in input_str else install_path.update(visible=False)
        c = index_url.update(visible=True) if "Index URL" in input_str else index_url.update(visible=False)
        return a, b, c

    def checkbox2_handler(input_str):
        a = install_path2.update(visible=True) if "Install Path" in input_str else install_path2.update(visible=False)
        b = index_url2.update(visible=True) if "Index URL" in input_str else index_url2.update(visible=False)
        return a, b

    install_button.click(
        fn=module_install,
        inputs=[name_box, version_box, install_path, index_url],
        outputs=[warning_box],
        show_progress=True
    )

    checkbox.change(
        fn=checkbox_handler,
        inputs=[checkbox],
        outputs=[version_box, install_path, index_url]
    )
    checkbox2.change(
        fn=checkbox2_handler,
        inputs=[checkbox2],
        outputs=[install_path2, index_url2]
    )

    install_requirement.click(
        fn=module_install_byfile,
        inputs=[file_upload, install_path, index_url],
        outputs=[warning_box],
        show_progress=True
    )


def module_install(name_box, version_box, install_path, index_url):
    result = "<div style='color:#999; font-size:10px' align='center'>"
    if name_box == "":
        result += f"please input module name you would like to install</div>"
        return result

    result += install_module(name_box, version_box, install_path, index_url)
    return result


def install_module(module_name, version_box, install_path, index_url):
    module = module_name if version_box == "" else module_name + "==" + version_box
    index_url = launch.index_url if launch.index_url != '' else (index_url if index_url != "" else tsinghua_url)
    install_path = install_path if install_path != "" else default_install_path

    if not launch.is_installed(module_name):
        cmd = [launch.python, "-m", "pip", "install", module, "-t", install_path, "--prefer-binary", "--index-url",
               index_url]
        try:
            subprocess.run(cmd, check=True)
            print(f"Installing {module}")
            # 尝试导入模块来检查是否安装成功
            importlib.import_module(module_name)
            print(f"{module} installed successfully")
            return f"{module} install success</div>"
        except subprocess.CalledProcessError:
            print(f"Couldn't install {module}")
            return f"Couldn't install {module}</div>"
        except ImportError:
            print(f"{module} not found after installation")
            return f"{module} not found after installation</div>"

    return f"{module} install success</div>"


def module_install_byfile(file, install_path, index_url):
    if file is None:
        return f"please upload requirements file</div>"
    shutil.copy(file.name, tmpdir)
    file_name = os.path.basename(file.name)
    index_url = launch.index_url if launch.index_url != '' else (index_url if index_url != "" else tsinghua_url)
    install_path = install_path if install_path != "" else default_install_path
    cmd = [launch.python, "-m", "pip", "install", "-r", tmpdir+"/"+file_name, "-t", install_path, "--prefer-binary",
           "--index-url", index_url]
    try:
        subprocess.run(cmd, check=True)
        print(f"{file_name} installed successfully")
        return f"{file_name} install success</div>"
    except subprocess.CalledProcessError:
        print(f"Couldn't install {file.name}")
        return f"Couldn't install {file.name}</div>"


def is_valid_module_name(module_name):
    """Check if a module name is valid according to Python's naming rules."""
    # The regular expression pattern for a valid Python identifier
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, module_name))


script_callbacks.on_ui_tabs(on_ui_tabs)
