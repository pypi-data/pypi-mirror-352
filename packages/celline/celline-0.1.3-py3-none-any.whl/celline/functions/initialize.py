import subprocess

import inquirer

from celline.config import Setting
from celline.functions._base import CellineFunction


class Initialize(CellineFunction):
    def register(self) -> str:
        return "init"

    def call(self, project):
        settings = Setting()
        proc = subprocess.Popen("which R", stdout=subprocess.PIPE, shell=True)
        result = proc.communicate()
        default_r = result[0].decode("utf-8").replace("\n", "")
        questions = [
            inquirer.Text(name="projname", message="What is a name of your project?"),
            inquirer.Path(name="rpath", message="Where is R?", default=default_r),
        ]
        result = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        if result is None:
            quit()
        settings.name = result["projname"]
        settings.r_path = result["rpath"]
        settings.version = "0.1"
        settings.wait_time = 4
        settings.flush()
        print("Completed.")
        return project
