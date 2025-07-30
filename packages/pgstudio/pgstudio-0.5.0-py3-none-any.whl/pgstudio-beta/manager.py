# pgstudio/manager.py

import os
import pygame
import logging
from .objects import ObjectManager
from .ui.app import PgStudioApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class PgStudioManager:
    """
    central manager: configure() sets up project folder & ObjectManager.
    launch() initializes pygame + PgStudioApp.
    """

    def __init__(self):
        self.project_root = None
        self.obj_mgr: ObjectManager = None

    def configure(self, core: str):
        """
        core: path to project directory.
        sets up folder, objects.json, scripts/, images/.
        """
        core_path = os.path.abspath(core)
        os.makedirs(core_path, exist_ok=True)
        logging.info(f"configuring project at {core_path}")
        self.project_root = core_path
        self.obj_mgr = ObjectManager(self.project_root)

    def launch(self):
        """
        launch the editor UI. must have called configure() first.
        """
        if not self.project_root or not self.obj_mgr:
            raise RuntimeError("u gotta call pgstudio.configure(core=...) before launch()")
        pygame.init()
        app = PgStudioApp(self.obj_mgr)
        app.run()
        pygame.quit()
        logging.info("exiting PgStudio")

def main():
    """
    entrypoint for console_scripts. so `pgstudio some_folder` works.
    """
    import sys
    if len(sys.argv) < 2:
        print("usage: pgstudio <project_folder>")
        sys.exit(1)
    core = sys.argv[1]
    mgr = PgStudioManager()
    mgr.configure(core)
    mgr.launch()
