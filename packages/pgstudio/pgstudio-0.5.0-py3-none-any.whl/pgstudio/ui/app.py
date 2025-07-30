# pgstudio/ui/app.py

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIButton
from pygame_gui.windows import UIConfirmationDialog, UIMessageWindow
from typing import Optional
from ..objects import ObjectManager, ObjectNode
from .explorer import ExplorerTree
from .properties_panel import PropertiesPanel
from .canvas import Canvas
from ..utils import ensure_folder
import os
import logging

class PgStudioApp:
    """
    entrypoint for the editor. composes:
    - a top Toolbar (Undo, Redo, Save, Export, New)
    - an ExplorerTree panel on left
    - a Canvas in the center (draw & interact with objects)
    - a PropertiesPanel on the right
    uses pygame + pygame_gui with theming.
    """

    def __init__(self, object_manager: ObjectManager):
        self.obj_mgr = object_manager

        # pygame setup
        self.window_size = (1280, 800)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("PgStudio - pygame GUI Editor")
        self.clock = pygame.time.Clock()

        # load the theme (if exists)
        theme_path = os.path.join(os.path.dirname(__file__), os.pardir, "themes", "pgstudio_theme.json")
        if os.path.isfile(theme_path):
            self.ui_manager = pygame_gui.UIManager(self.window_size, theme_path)
            logging.info(f"Loaded theme from {theme_path}")
        else:
            self.ui_manager = pygame_gui.UIManager(self.window_size)
            logging.warning("Theme file not found; using default theme.")

        # define panel widths/heights
        self.toolbar_height = 40
        self.explorer_width = 300
        self.properties_width = 300

        # current selection
        self.selected_id: Optional[str] = None

        # build UI components
        self._build_toolbar()
        self.explorer = ExplorerTree(self, pygame.Rect(0, self.toolbar_height, self.explorer_width, self.window_size[1]-self.toolbar_height))
        self.properties = PropertiesPanel(self, pygame.Rect(self.window_size[0]-self.properties_width, self.toolbar_height, self.properties_width, self.window_size[1]-self.toolbar_height))
        self.canvas = Canvas(self, pygame.Rect(self.explorer_width, self.toolbar_height, self.window_size[0]-self.explorer_width-self.properties_width, self.window_size[1]-self.toolbar_height))

        # initial populate
        self.explorer.reload()
        self.properties.clear()
        logging.info("PgStudioApp initialized")

    def _build_toolbar(self):
        """
        top toolbar with buttons: Undo, Redo, Save, Export, New Project.
        """
        y = 0
        h = self.toolbar_height
        self.toolbar_panel = UIPanel(
            relative_rect=pygame.Rect(0, y, self.window_size[0], h),
            starting_height=1,
            manager=self.ui_manager,
            object_id=ObjectID(class_id="toolbar_panel"),
            anchors={'left': 'left', 'right': 'right', 'top': 'top'}
        )
        btn_w = 80
        padding = 10

        # Undo button
        self.undo_button = UIButton(
            relative_rect=pygame.Rect(padding, padding // 2, btn_w, h - padding),
            text="Undo",
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        # Redo button
        self.redo_button = UIButton(
            relative_rect=pygame.Rect(padding*2 + btn_w, padding // 2, btn_w, h - padding),
            text="Redo",
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        # Save button
        self.save_button = UIButton(
            relative_rect=pygame.Rect(padding*3 + btn_w*2, padding // 2, btn_w, h - padding),
            text="Save",
            manager=self.ui_manager,
            container=self.toolbar_panel
        )
        # Export button
        self.export_button = UIButton(
            relative_rect=pygame.Rect(padding*4 + btn_w*3, padding // 2, btn_w, h - padding),
            text="Export",
            manager=self.ui_manager,
            container=self.toolbar_panel
        )
        # New Project button
        self.new_button = UIButton(
            relative_rect=pygame.Rect(padding*5 + btn_w*4, padding // 2, btn_w, h - padding),
            text="New Prjct",
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

    def run(self):
        """
        main loop: handle events, update UI, draw panels & canvas each frame.
        """
        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # pass to individual components
                self.explorer.process_event(event)
                self.canvas.process_event(event)
                self.properties.process_event(event)

                # toolbar button presses
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.undo_button:
                        if self.obj_mgr.undo_manager.can_undo():
                            success = self.obj_mgr.undo_manager.undo()
                            if success:
                                self.explorer.reload()
                                self.properties.clear()
                                self.canvas  # no explicit method, canvas auto‐updates on next draw
                        else:
                            UIMessageWindow(
                                pygame.Rect(300, 250, 400, 200),
                                "Nothing to Undo",
                                "There are no more actions to undo.",
                                self.ui_manager
                            )
                    elif event.ui_element == self.redo_button:
                        if self.obj_mgr.undo_manager.can_redo():
                            success = self.obj_mgr.undo_manager.redo()
                            if success:
                                self.explorer.reload()
                                self.properties.clear()
                        else:
                            UIMessageWindow(
                                pygame.Rect(300, 250, 400, 200),
                                "Nothing to Redo",
                                "There are no more actions to redo.",
                                self.ui_manager
                            )
                    elif event.ui_element == self.save_button:
                        try:
                            self.obj_mgr._save_all()
                            logging.info("Saved project data.")
                        except Exception as e:
                            UIMessageWindow(
                                pygame.Rect(300, 250, 400, 200),
                                "Save Error",
                                f"Couldn't save project:\n{e}",
                                self.ui_manager
                            )
                    elif event.ui_element == self.export_button:
                        dlg = UIConfirmationDialog(
                            rect=pygame.Rect(400, 300, 400, 200),
                            manager=self.ui_manager,
                            window_title="Export Confirmation",
                            action_long_desc="This will generate a main.py in your project folder. Continue?",
                        )
                        dlg.confirm_button.text = "Yes"
                        dlg.cancel_button.text = "No"
                        dlg.user_data = ("export_confirm", None)
                    elif event.ui_element == self.new_button:
                        dlg = UIConfirmationDialog(
                            rect=pygame.Rect(400, 300, 400, 200),
                            manager=self.ui_manager,
                            window_title="New Project?",
                            action_long_desc="This will delete ALL objects, scripts, and images in this project folder. Continue?",
                        )
                        dlg.confirm_button.text = "Yes"
                        dlg.cancel_button.text = "No"
                        dlg.user_data = ("new_confirm", None)

                # handle confirmation dialogs
                if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    user_data = getattr(event.ui_element, "user_data", None)
                    if user_data and user_data[0] == "export_confirm":
                        try:
                            self.obj_mgr.export_to_python(self.obj_mgr.project_root)
                        except Exception as e:
                            UIMessageWindow(
                                pygame.Rect(300, 250, 400, 200),
                                "Export Error",
                                f"Couldn't export project:\n{e}",
                                self.ui_manager
                            )
                    elif user_data and user_data[0] == "new_confirm":
                        import shutil
                        try:
                            # record state so user can undo the “new project”?
                            self.obj_mgr.undo_manager.record_state()
                            for node in list(self.obj_mgr.nodes.values()):
                                self.obj_mgr.delete_object(node.id)
                            shutil.rmtree(self.obj_mgr.scripts_folder, ignore_errors=True)
                            shutil.rmtree(self.obj_mgr.images_folder, ignore_errors=True)
                            ensure_folder(self.obj_mgr.scripts_folder)
                            ensure_folder(self.obj_mgr.images_folder)
                            self.obj_mgr._save_all()
                            self.selected_id = None
                            self.explorer.reload()
                            self.properties.clear()
                            logging.info("New project: all data cleared.")
                        except Exception as e:
                            UIMessageWindow(
                                pygame.Rect(300, 250, 400, 200),
                                "New Project Error",
                                f"Couldn't reset project:\n{e}",
                                self.ui_manager
                            )

                # pass everything else to pygame_gui
                self.ui_manager.process_events(event)

            # update UI manager
            self.ui_manager.update(time_delta)

            # draw background
            self.screen.fill((30, 30, 30))

            # draw panels
            self.explorer.draw(self.screen)
            self.canvas.draw(self.screen)
            self.properties.draw(self.screen)
            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()

        logging.info("exiting editor")

    def set_selected(self, obj_id: Optional[str]):
        """
        centralize selection change: notify explorer & properties.
        """
        self.selected_id = obj_id
        self.explorer.set_selected(obj_id)
        self.properties.set_selected(obj_id)

    def get_selected(self) -> Optional[ObjectNode]:
        if self.selected_id:
            return self.obj_mgr.get_node(self.selected_id)
        return None
