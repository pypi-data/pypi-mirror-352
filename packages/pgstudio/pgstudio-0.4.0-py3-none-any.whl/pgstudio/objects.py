# pgstudio/objects.py

import os
from typing import List, Optional, Dict, Any, Tuple
from .utils import sanitize_name, load_json, save_json, ensure_folder, gen_id, open_in_editor
from .undo_manager import UndoManager
import logging

# constants
OBJECTS_JSON = "objects.json"
SCRIPTS_DIR = "scripts"
IMAGES_DIR = "images"

BUILTIN_TYPES = [
    "Rectangle",
    "Button",
    "Label",
    "Image",
    "TextInput",
    "Script"
]

class ObjectNode:
    """
    represents an Object in the scene. can have children.
    stores props: id, name, type, x,y,w,h, visible, z_order, parent_id, children_ids, extra_props, events
    extra_props = type‐specific (color, text, font_size, image_path, placeholder, etc)
    events = dict of custom event hookups, e.g. {"on_click": "<script_name>"} 
    x,y are relative to parent; drawing uses compute_abs_pos
    """

    def __init__(
        self,
        obj_id: str,
        name: str,
        obj_type: str,
        x: int = 0,
        y: int = 0,
        w: int = 100,
        h: int = 50,
        visible: bool = True,
        z_order: int = 0,
        parent_id: Optional[str] = None,
        children_ids: Optional[List[str]] = None,
        extra_props: Optional[Dict[str, Any]] = None,
        events: Optional[Dict[str, str]] = None
    ):
        self.id = obj_id
        self.name = name
        self.type = obj_type
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.visible = visible
        self.z_order = z_order
        self.parent_id = parent_id
        self.children_ids = children_ids if children_ids is not None else []
        self.extra_props = extra_props if extra_props is not None else {}
        self.events = events if events is not None else {}  # custom event hookups

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "visible": self.visible,
            "z_order": self.z_order,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "extra_props": self.extra_props,
            "events": self.events,
        }

    @staticmethod
    def from_dict(dct: Dict[str, Any]):
        return ObjectNode(
            obj_id=dct["id"],
            name=dct["name"],
            obj_type=dct["type"],
            x=dct.get("x", 0),
            y=dct.get("y", 0),
            w=dct.get("w", 100),
            h=dct.get("h", 50),
            visible=dct.get("visible", True),
            z_order=dct.get("z_order", 0),
            parent_id=dct.get("parent_id"),
            children_ids=dct.get("children_ids", []),
            extra_props=dct.get("extra_props", {}),
            events=dct.get("events", {}),
        )


class ObjectManager:
    """
    handles loading/saving/manipulating the tree of ObjectNodes inside project dir.
    - keeps objects.json updated
    - manages scripts/ and images/ folders
    - nested transforms: x,y are *relative* to parent; drawing & dragging use absolute calculations.
    - undo/redo integrated
    - event hookups stored in each ObjectNode.events
    """

    def __init__(self, project_root: str):
        self.project_root = project_root
        ensure_folder(self.project_root)

        self.objects_path = os.path.join(self.project_root, OBJECTS_JSON)
        self.scripts_folder = os.path.join(self.project_root, SCRIPTS_DIR)
        ensure_folder(self.scripts_folder)
        self.images_folder = os.path.join(self.project_root, IMAGES_DIR)
        ensure_folder(self.images_folder)

        # id -> ObjectNode
        self.nodes: Dict[str, ObjectNode] = {}
        self._load_all()

        # set up undo_manager (pass self so it can read/write nodes)
        self.undo_manager = UndoManager(self)

    def _load_all(self):
        """load objects.json into self.nodes, or initialize empty tree."""
        data = load_json(self.objects_path)
        if not data:
            self.nodes = {}
            self._save_all()
            return
        self.nodes = {}
        for d in data:
            node = ObjectNode.from_dict(d)
            self.nodes[node.id] = node

    def _save_all(self):
        """write all self.nodes to objects.json (list of dicts)."""
        data = [node.to_dict() for node in self.nodes.values()]
        save_json(self.objects_path, data)

    def _generate_new_id(self) -> str:
        """short wrapper for gen_id()."""
        return gen_id()

    def add_object(
        self,
        name: str,
        obj_type: str = "Rectangle",
        parent_id: Optional[str] = None,
    ) -> ObjectNode:
        """
        create and register a new ObjectNode. 
        sets default props based on type. returns the node.
        """
        # record state for undo
        self.undo_manager.record_state()

        clean_name = sanitize_name(name)
        new_id = self._generate_new_id()

        # default extra_props by type:
        default_extra = {}
        if obj_type == "Label":
            default_extra = {"text": clean_name, "font_size": 20, "color": [255, 255, 255]}
        elif obj_type == "Button":
            default_extra = {"text": clean_name, "font_size": 18, "color": [100, 200, 100]}
        elif obj_type == "Rectangle":
            default_extra = {"color": [200, 100, 100]}
        elif obj_type == "Image":
            default_extra = {"image_path": ""}
        elif obj_type == "TextInput":
            default_extra = {"placeholder": "Enter text...", "text_color": [0, 0, 0], "bg_color": [255, 255, 255]}
        elif obj_type == "Script":
            default_extra = {}

        node = ObjectNode(
            obj_id=new_id,
            name=clean_name,
            obj_type=obj_type,
            x=50,
            y=50,
            w=100,
            h=50,
            visible=True,
            z_order=0,
            parent_id=parent_id,
            children_ids=[],
            extra_props=default_extra,
            events={},  # start with no event hookups
        )
        self.nodes[new_id] = node

        # register child under parent
        if parent_id:
            parent = self.nodes.get(parent_id)
            if parent:
                parent.children_ids.append(new_id)

        self._save_all()

        # if it's a Script, create the stub file
        if obj_type == "Script":
            script_fname = f"{clean_name}.py"
            script_path = os.path.join(self.scripts_folder, script_fname)
            if not os.path.isfile(script_path):
                try:
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(f"# script for {clean_name}\n\n")
                        f.write("def run(obj, event=None):\n")
                        f.write("    # write your custom code here\n")
                        f.write("    print(f\"Script {clean_name} running for {{obj.name}}\")\n")
                    logging.info(f"created script stub: {script_path}")
                except Exception as e:
                    logging.error(f"couldn't create script file {script_path}: {e}")

        return node

    def delete_object(self, obj_id: str):
        """
        delete an object and all its descendants recursively.
        also remove it from its parent’s children_ids.
        if Script: delete .py; 
        """
        if obj_id not in self.nodes:
            return

        # record state for undo
        self.undo_manager.record_state()

        node = self.nodes.get(obj_id)
        if not node:
            return
        # delete children first
        for child_id in node.children_ids[:]:
            self.delete_object(child_id)

        # remove from parent
        if node.parent_id:
            parent = self.nodes.get(node.parent_id)
            if parent and obj_id in parent.children_ids:
                parent.children_ids.remove(obj_id)

        # if Script: delete file
        if node.type == "Script":
            stub = os.path.join(self.scripts_folder, f"{node.name}.py")
            if os.path.isfile(stub):
                try:
                    os.remove(stub)
                    logging.info(f"deleted script file: {stub}")
                except Exception as e:
                    logging.error(f"error deleting script file {stub}: {e}")

        # Finally, remove node
        del self.nodes[obj_id]
        self._save_all()

    def rename_object(self, obj_id: str, new_name: str):
        """
        rename an object. sanitize new_name. 
        for Script: rename its .py file stub too. 
        update children or extra if needed.
        """
        node = self.nodes.get(obj_id)
        if not node:
            return

        # record state for undo
        self.undo_manager.record_state()

        clean_new = sanitize_name(new_name)
        old_name = node.name
        node.name = clean_new

        # if Script: rename file
        if node.type == "Script":
            old_path = os.path.join(self.scripts_folder, f"{old_name}.py")
            new_path = os.path.join(self.scripts_folder, f"{clean_new}.py")
            try:
                if os.path.isfile(old_path):
                    os.rename(old_path, new_path)
                    logging.info(f"renamed script {old_path} -> {new_path}")
                else:
                    with open(new_path, "w", encoding="utf-8") as f:
                        f.write(f"# script for {clean_new}\n\n")
                        f.write("def run(obj, event=None):\n")
                        f.write("    print(f\"Script {clean_new} running for {obj.name}\")\n")
                    logging.info(f"created new script file {new_path}")
            except Exception as e:
                logging.error(f"error renaming script file: {e}")

        self._save_all()

    def update_properties(self, obj_id: str, **kwargs):
        """
        update basic props (x, y, w, h, visible, z_order, events) or extra_props.
        z_order must be an int. visible a bool. 
        if key matches attribute, set it; else, update extra_props or events.
        """
        node = self.nodes.get(obj_id)
        if not node:
            return

        # record state for undo
        self.undo_manager.record_state()

        for k, v in kwargs.items():
            if hasattr(node, k):
                setattr(node, k, v)
            else:
                # if it’s an event hookup (like "on_click"), store in node.events
                if k.startswith("event_"):
                    ev_name = k.replace("event_", "")
                    node.events[ev_name] = v
                else:
                    node.extra_props[k] = v
        self._save_all()

    def get_node(self, obj_id: str) -> Optional[ObjectNode]:
        return self.nodes.get(obj_id)

    def get_all_nodes(self) -> List[ObjectNode]:
        return list(self.nodes.values())

    def get_root_nodes(self) -> List[ObjectNode]:
        """roots = nodes with no parent."""
        return [n for n in self.nodes.values() if n.parent_id is None]

    def get_children(self, parent_id: str) -> List[ObjectNode]:
        parent = self.nodes.get(parent_id)
        if not parent:
            return []
        return [self.nodes[ch_id] for ch_id in parent.children_ids if ch_id in self.nodes]

    def move_node(self, obj_id: str, new_parent_id: Optional[str]):
        """
        reparent a node: remove from old parent, assign new_parent_id, add to new parent’s children.
        used if we implement drag&drop in Explorer later.
        """
        node = self.nodes.get(obj_id)
        if not node:
            return

        # record state for undo
        self.undo_manager.record_state()

        old_pid = node.parent_id
        if old_pid:
            old_parent = self.nodes.get(old_pid)
            if old_parent and obj_id in old_parent.children_ids:
                old_parent.children_ids.remove(obj_id)
        node.parent_id = new_parent_id
        if new_parent_id:
            new_parent = self.nodes.get(new_parent_id)
            if new_parent:
                new_parent.children_ids.append(obj_id)
        self._save_all()

    def compute_abs_pos(self, node: ObjectNode) -> Tuple[int, int]:
        """
        recursive: if node has parent, get parent’s absolute pos + node.x/y; else, (node.x, node.y).
        returns (abs_x, abs_y).
        """
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            px, py = self.compute_abs_pos(parent)
            return px + node.x, py + node.y
        else:
            return node.x, node.y

    def export_to_python(self, export_path: str):
        """
        generate a `main.py` in export_path that recreates the GUI tree using pygame & pygame_gui.
        also includes event hookups: for Buttons that have node.events["on_click"], it will import the script and call run().
        """
        try:
            lines = []
            lines.append("import pygame")
            lines.append("import pygame_gui")
            lines.append("import os")
            lines.append("")
            lines.append("def run():")
            lines.append("    pygame.init()")
            lines.append("    window_size = (800, 600)")
            lines.append("    screen = pygame.display.set_mode(window_size)")
            lines.append("    pygame.display.set_caption('PgStudio Export')")
            lines.append("    manager = pygame_gui.UIManager(window_size)")
            lines.append("")
            lines.append("    # dictionary to hold elements: id -> element or (type, data)")
            lines.append("    elements = {}")
            lines.append("")
            # sort by z_order so parents come first
            sorted_nodes = sorted(self.get_all_nodes(), key=lambda n: n.z_order)
            for node in sorted_nodes:
                nid = node.id
                ax, ay = self.compute_abs_pos(node)
                w, h = node.w, node.h
                if node.type == "Rectangle":
                    color = node.extra_props.get("color", [200,100,100])
                    lines.append(f"    # Rectangle: {node.name}")
                    lines.append(f"    rect_{nid} = pygame.Rect({ax}, {ay}, {w}, {h})")
                    lines.append(f"    elements['{nid}'] = ('Rectangle', rect_{nid}, {color})")
                elif node.type == "Button":
                    txt = node.extra_props.get("text", node.name).replace("'", "\\'")
                    fs = node.extra_props.get("font_size", 18)
                    clr = node.extra_props.get("color", [100,200,100])
                    lines.append(f"    # Button: {node.name}")
                    lines.append(f"    btn_{nid} = pygame_gui.elements.UIButton(")
                    lines.append(f"        relative_rect=pygame.Rect({ax}, {ay}, {w}, {h}),")
                    lines.append(f"        text='{txt}',")
                    lines.append(f"        manager=manager")
                    lines.append("    )")
                    lines.append(f"    elements['{nid}'] = btn_{nid}")
                    # event hookup?
                    if "on_click" in node.events:
                        script_name = node.events["on_click"]
                        script_module = f"scripts.{script_name}"
                        lines.append(f"    import {script_module} as script_{nid}")
                elif node.type == "Label":
                    txt = node.extra_props.get("text", node.name).replace("'", "\\'")
                    fs = node.extra_props.get("font_size", 20)
                    clr = node.extra_props.get("color", [255,255,255])
                    lines.append(f"    # Label: {node.name}")
                    lines.append(f"    lbl_{nid} = pygame_gui.elements.UILabel(")
                    lines.append(f"        relative_rect=pygame.Rect({ax}, {ay}, {w}, {h}),")
                    lines.append(f"        text='{txt}',")
                    lines.append(f"        manager=manager"
                                  f")")
                    lines.append(f"    elements['{nid}'] = lbl_{nid}")
                elif node.type == "TextInput":
                    placeholder = node.extra_props.get("placeholder", "")
                    lines.append(f"    # TextInput: {node.name}")
                    lines.append(f"    inp_{nid} = pygame_gui.elements.UITextEntryLine(")
                    lines.append(f"        relative_rect=pygame.Rect({ax}, {ay}, {w}, {h}),")
                    lines.append(f"        manager=manager"
                                  f")")
                    lines.append(f"    inp_{nid}.set_text('{placeholder}')")
                    lines.append(f"    elements['{nid}'] = inp_{nid}")
                elif node.type == "Image":
                    imgpath = node.extra_props.get("image_path", "")
                    lines.append(f"    # Image: {node.name}")
                    lines.append(f"    surf_{nid} = pygame.image.load(r'{imgpath}')")
                    lines.append(f"    surf_{nid} = pygame.transform.scale(surf_{nid}, ({w}, {h}))")
                    lines.append(f"    elements['{nid}'] = ('Image', surf_{nid}, ({ax}, {ay}))")
                elif node.type == "Script":
                    script_file = os.path.join(SCRIPTS_DIR, f"{node.name}.py")
                    lines.append(f"    # Script: {node.name} (not instantiated)")
                    lines.append(f"    # you can import and use: {script_file}")
                lines.append("")

            # build event loop & handle button press events
            lines.append("    clock = pygame.time.Clock()")
            lines.append("    running = True")
            lines.append("    while running:")
            lines.append("        time_delta = clock.tick(60)/1000.0")
            lines.append("        for e in pygame.event.get():")
            lines.append("            if e.type == pygame.QUIT:")
            lines.append("                running = False")
            lines.append("            manager.process_events(e)")
            lines.append("")
            # button click handling
            lines.append("            # custom Button on_click event handlers")
            for node in sorted_nodes:
                if node.type == "Button" and "on_click" in node.events:
                    nid = node.id
                    script_name = node.events["on_click"]
                    lines.append(f"            if e.type == pygame_gui.UI_BUTTON_PRESSED and e.ui_element == elements['{nid}']:")
                    lines.append(f"                script_{nid}.run(elements['{nid}'], event=e)")
            lines.append("")
            lines.append("        manager.update(time_delta)")
            lines.append("        screen.fill((30,30,30))")
            lines.append("")
            lines.append("        # draw rectangles and images manually")
            lines.append("        for key, elem in elements.items():")
            lines.append("            if isinstance(elem, tuple) and elem[0] == 'Rectangle':")
            lines.append("                _, rect, color = elem")
            lines.append("                pygame.draw.rect(screen, tuple(color), rect)")
            lines.append("            elif isinstance(elem, tuple) and elem[0] == 'Image':")
            lines.append("                _, surf, (ix,iy) = elem")
            lines.append("                screen.blit(surf, (ix,iy))")
            lines.append("")
            lines.append("        manager.draw_ui(screen)")
            lines.append("        pygame.display.update()")
            lines.append("")
            lines.append("    pygame.quit()")
            lines.append("")
            lines.append("if __name__ == '__main__':")
            lines.append("    run()")

            export_file = os.path.join(export_path, "main.py")
            with open(export_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            logging.info(f"exported project to {export_file}")
        except Exception as e:
            logging.error(f"error exporting to Python: {e}")
