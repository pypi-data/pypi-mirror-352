# pgstudio/ui/explorer.py

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIScrollingContainer, UIButton, UILabel, UITextEntryLine, UIWindow
from ..objects import ObjectNode, ObjectManager
from pygame_gui.windows import UIMessageWindow
from typing import Optional
import logging

UI_CONTEXT_MENU_OPTION_SELECTED = pygame.USEREVENT + 3224

# custom UIContextMenu (popup menu)
class UIContextMenu(UIPanel):
    def __init__(self, options_list, window_title, manager, container, object_id):
        super().__init__(
            relative_rect=pygame.Rect(0,0,200,30 + 30*len(options_list)),
            starting_height=10,
            manager=manager,
            container=container,
            object_id=object_id
        )
        self.manager = manager
        self.options = options_list
        self.user_data = None
        self.buttons = []

        self.title_label = UILabel(
            pygame.Rect(5, 5, 190, 20),
            text=window_title,
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="context_menu_title")
        )

        y = 30
        for option in options_list:
            btn = UIButton(
                pygame.Rect(5, y, 190, 25),
                text=option,
                manager=manager,
                container=self,
                object_id=ObjectID(class_id="context_menu_option")
            )
            self.buttons.append(btn)
            y += 30

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.relative_rect.collidepoint(event.pos):
                self.kill()
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.buttons:
                sel_text = event.ui_element.text
                new_event = pygame.event.Event(
                    UI_CONTEXT_MENU_OPTION_SELECTED,
                    {'text': sel_text, 'ui_element': self}
                )
                pygame.event.post(new_event)
                self.kill()

# custom UIUserEntryWindow (simple text input dialog)
class UIUserEntryWindow(UIWindow):
    def __init__(self, rect, manager, window_title, initial_text=""):
        super().__init__(rect, manager, window_title)
        self.user_data = None

        self.prompt_label = UILabel(
            pygame.Rect(10, 40, rect.width - 20, 30),
            window_title,
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="entry_window_label")
        )

        self.text_entry = UITextEntryLine(
            pygame.Rect(10, 80, rect.width - 20, 30),
            manager=manager,
            container=self
        )
        self.text_entry.set_text(initial_text)

        self.ok_button = UIButton(
            pygame.Rect(rect.width - 110, rect.height - 50, 100, 40),
            text="OK",
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="entry_window_ok_button")
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ok_button:
                new_event = pygame.event.Event(
                    pygame_gui.UI_TEXT_ENTRY_FINISHED,
                    {'text': self.text_entry.get_text(), 'ui_element': self}
                )
                pygame.event.post(new_event)
                self.kill()


class ExplorerTree:
    """
    left sidebar: shows a collapsible tree of objects.
    supports:
    - clicking to select
    - right-click (on blank) to Add Root Object
    - right-click (on object) to Add Child, Rename, Delete
    - collapse/expand nodes
    """

    def __init__(self, app, rect: pygame.Rect):
        self.app = app
        self.obj_mgr: ObjectManager = app.obj_mgr
        self.ui_mgr = app.ui_manager
        self.rect = rect

        # track which nodes are expanded
        self.expanded: set = set()

        # build panel & scroller
        self.panel = UIPanel(
            relative_rect=self.rect,
            starting_height=1,
            manager=self.ui_mgr,
            object_id=ObjectID(class_id="explorer_panel"),
            anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'bottom'}
        )
        self.scroller = UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            manager=self.ui_mgr,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # store button references: obj_id -> UIButton
        self.buttons: dict = {}
        
        self.selected_id = None
        
        logging.info("ExplorerTree initialized")

    def reload(self):
        """
        clear & recreate all buttons according to current object tree & expanded state.
        """
        # kill existing buttons/labels
        for child in list(self.scroller.get_container()):
            child.kill()
        self.buttons.clear()

        y = 10
        indent = 20

        def _draw_node(node: ObjectNode, level: int, y_pos: int) -> int:
            # collapse/expand toggle icon
            has_kids = len(node.children_ids) > 0
            icon = "▼" if (node.id in self.expanded and has_kids) else ("▶" if has_kids else " ")
            text = f"{icon} {node.name}"
            btn = UIButton(
                relative_rect=pygame.Rect(10 + level * indent, y_pos, self.rect.width - (10 + level * indent) - 20, 25),
                text=text,
                manager=self.ui_mgr,
                container=self.scroller.get_container()
            )

            if node.id == self.selected_id:
                btn.select()  # We'll define a style for this in the theme (see below)

            btn.user_data = ("explorer_obj", node.id)
            self.buttons[node.id] = btn
            y_next = y_pos + 30
            # if expanded, draw children
            if has_kids and node.id in self.expanded:
                for child_id in node.children_ids:
                    child = self.obj_mgr.get_node(child_id)
                    if child:
                        y_next = _draw_node(child, level+1, y_next)
            return y_next

        for root in self.obj_mgr.get_root_nodes():
            y = _draw_node(root, 0, y)

    def draw(self, surface):
        """
        nothing to draw manually; pygame_gui handles panel & scroller.
        """
        pass

    def process_event(self, event):
        # handle left‐clicks (select, expand/collapse)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.panel.relative_rect.collidepoint(mouse_pos):
                clicked = None
                for el in self.scroller.get_container().elements:
                    if isinstance(el, UIButton):
                        # Get absolute position of the button
                        abs_rect = el.rect.move(self.panel.rect.topleft)
                        if abs_rect.collidepoint(mouse_pos):
                            clicked = el
                            break
                if clicked and isinstance(clicked, pygame_gui.elements.UIButton):
                    ud = getattr(clicked, "user_data", None)
                    if ud and ud[0] == "explorer_obj":
                        obj_id = ud[1]
                        btn_rect: pygame.Rect = clicked.relative_rect
                        rel_x = mouse_pos[0] - btn_rect.x
                        # if clicked on icon area (<20px), toggle expand
                        if rel_x < 20:
                            if obj_id in self.expanded:
                                self.expanded.remove(obj_id)
                            else:
                                self.expanded.add(obj_id)
                            self.reload()
                        else:
                            # select object
                            self.app.set_selected(obj_id)

        # handle right‐clicks (context menus)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mouse_pos = event.pos
            if self.panel.relative_rect.collidepoint(mouse_pos):

                clicked = None
                for el in self.scroller.get_container().elements:
                    if isinstance(el, UIButton):
                        # Get absolute position of the button
                        abs_rect = el.rect.move(self.panel.rect.topleft)
                        if abs_rect.collidepoint(mouse_pos):
                            clicked = el
                            break

                if clicked and isinstance(clicked, pygame_gui.elements.UIButton):
                    ud = getattr(clicked, "user_data", None)
                    if ud and ud[0] == "explorer_obj":
                        # right‐click on object → object menu
                        obj_id = ud[1]
                        options = [
                            "Add Child Rectangle", "Add Child Button", "Add Child Label",
                            "Add Child Image", "Add Child TextInput", "Add Child Script",
                            "Rename", "Delete"
                        ]
                        menu = UIContextMenu(
                            options_list=options,
                            window_title="Object Menu",
                            manager=self.ui_mgr,
                            container=self.panel,
                            object_id=ObjectID(class_id="object_context_menu")
                        )
                        menu.user_data = obj_id
                        return

                # right‐click on blank explorer → root menu
                options = ["Add Rectangle", "Add Button", "Add Label", "Add Image", "Add TextInput", "Add Script"]
                menu = UIContextMenu(
                    options_list=options,
                    window_title="Explorer Menu",
                    manager=self.ui_mgr,
                    container=self.panel,
                    object_id=ObjectID(class_id="explorer_context_menu")
                )
                menu.user_data = None

        # handle context menu selection
        if event.type == UI_CONTEXT_MENU_OPTION_SELECTED:
            print("Got UI_CONTEXT_MENU_OPTION_SELECTED event with attributes:", event.__dict__)
            
            sel = event.text  # e.g. "Add Child Button"

            parent_id = getattr(event.ui_element, "user_data", None)
            try:
                if sel.startswith("Add Child"):
                    _, _, obj_type = sel.partition("Add Child ")
                    name = f"{obj_type}_{len(self.obj_mgr.get_all_nodes())}"
                    newnode = self.obj_mgr.add_object(name=name, obj_type=obj_type, parent_id=parent_id)
                    if parent_id and parent_id not in self.expanded:
                        self.expanded.add(parent_id)
                    self.reload()
                elif sel.startswith("Add"):
                    _, _, obj_type = sel.partition("Add ")
                    name = f"{obj_type}_{len(self.obj_mgr.get_all_nodes())}"
                    self.obj_mgr.add_object(name=name, obj_type=obj_type, parent_id=None)
                    self.reload()
                elif sel == "Rename":
                    current = self.obj_mgr.get_node(parent_id).name
                    dlg = UIUserEntryWindow(
                        rect=pygame.Rect(400, 200, 300, 200),
                        manager=self.ui_mgr,
                        window_title="Rename Object",
                        initial_text=current
                    )
                    dlg.user_data = ("rename_explorer", parent_id)
                elif sel == "Delete":
                    self.obj_mgr.delete_object(parent_id)
                    if self.app.selected_id == parent_id:
                        self.app.set_selected(None)
                    self.reload()
            except Exception as e:
                UIMessageWindow(
                    rect=pygame.Rect(300, 250, 400, 200),
                    window_title="Error Title",
                    html_message="Some message",
                    manager=self.ui_mgr
                )


        # handle rename dialog finish
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            elem = event.ui_element
            ud = getattr(elem, "user_data", None)
            if ud and ud[0] == "rename_explorer":
                obj_id = ud[1]
                newname = event.text
                try:
                    self.obj_mgr.rename_object(obj_id, newname)
                    self.reload()
                except Exception as e:
                    UIMessageWindow(
                        rect=pygame.Rect(300, 250, 400, 200),
                        window_title="Rename Error",
                        html_message=f"Couldn't rename:\n{e}",
                        manager=self.ui_mgr
                    )

    def set_selected(self, obj_id: Optional[str]):
        self.selected_id = obj_id
        self.reload()