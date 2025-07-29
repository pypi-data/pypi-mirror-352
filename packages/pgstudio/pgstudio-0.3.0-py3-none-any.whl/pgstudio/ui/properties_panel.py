# pgstudio/ui/properties_panel.py

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIDropDownMenu, UIButton
from pygame_gui.windows import UIColourPickerDialog as UIColorPickerDialog, UIFileDialog, UIMessageWindow
from pygame_gui.core import ObjectID
from typing import Optional
from ..objects import ObjectManager
from ..utils import open_in_editor
import os
import logging

class PropertiesPanel:
    """
    right sidebar: shows/edit properties of the currently selected object.
    supports editing:
      - x, y (absolute), w, h, visible, z_order, name
      - type-specific extra_props (color picker, text, font_size, image picker, placeholder, text_color, etc.)
      - event hookups: e.g. on_click for Button (choose existing Script)
      - Delete Object & Edit Script (for Script nodes)
    """

    def __init__(self, app, rect: pygame.Rect):
        self.app = app
        self.obj_mgr: ObjectManager = app.obj_mgr
        self.ui_mgr = app.ui_manager
        self.rect = rect

        self.panel = UIPanel(
            relative_rect=self.rect,
            starting_height=1,
            manager=self.ui_mgr,
            object_id=ObjectID(class_id="properties_panel"),
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        self.elements = []  # track current widgets so we can kill them on clear
        self.selected_id: Optional[str] = None
        logging.info("PropertiesPanel initialized")

    def clear(self):
        """display “No object selected”."""
        for elm in self.elements:
            elm.kill()
        self.elements.clear()
        UILabel(
            relative_rect=pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, 30),
            text="No object selected",
            manager=self.ui_mgr,
            container=self.panel
        )

    def set_selected(self, obj_id: Optional[str]):
        """rebuild the panel based on new selection."""
        self.selected_id = obj_id
        self._rebuild()

    def _rebuild(self):
        # kill old widgets
        for elm in list(self.panel.get_container()):
            elm.kill()
        self.elements.clear()

        if not self.selected_id:
            UILabel(
                relative_rect=pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, 30),
                text="No object selected",
                manager=self.ui_mgr,
                container=self.panel
            )
            return

        node = self.obj_mgr.get_node(self.selected_id)
        if not node:
            return

        x0 = self.rect.x + 10
        y0 = self.rect.y + 10
        line_h = 30
        label_w = 100
        input_w = self.rect.width - label_w - 30

        # Title
        lbl_title = UILabel(
            relative_rect=pygame.Rect(x0, y0, self.rect.width - 20, 25),
            text=f"Props: {node.name}",
            manager=self.ui_mgr,
            container=self.panel
        )
        self.elements.append(lbl_title)
        y0 += line_h

        # ABS X:
        lbl_x = UILabel(
            relative_rect=pygame.Rect(x0, y0, label_w, 20),
            text="abs_x:",
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_x = UITextEntryLine(
            relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
            manager=self.ui_mgr,
            container=self.panel
        )
        abs_x, abs_y = self.obj_mgr.compute_abs_pos(node)
        inp_x.set_text(str(abs_x))
        inp_x.user_data = ("prop_abs_x", node.id)
        self.elements += [lbl_x, inp_x]
        y0 += line_h

        # ABS Y:
        lbl_y = UILabel(
            relative_rect=pygame.Rect(x0, y0, label_w, 20),
            text="abs_y:",
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_y = UITextEntryLine(
            relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_y.set_text(str(abs_y))
        inp_y.user_data = ("prop_abs_y", node.id)
        self.elements += [lbl_y, inp_y]
        y0 += line_h

        # width:
        lbl_w = UILabel(
            relative_rect=pygame.Rect(x0, y0, label_w, 20),
            text="w:",
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_w = UITextEntryLine(
            relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_w.set_text(str(node.w))
        inp_w.user_data = ("prop_w", node.id)
        self.elements += [lbl_w, inp_w]
        y0 += line_h

        # height:
        lbl_h = UILabel(
            relative_rect=pygame.Rect(x0, y0, label_w, 20),
            text="h:",
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_h = UITextEntryLine(
            relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_h.set_text(str(node.h))
        inp_h.user_data = ("prop_h", node.id)
        self.elements += [lbl_h, inp_h]
        y0 += line_h

        # visible:
        lbl_vis = UILabel(
            relative_rect=pygame.Rect(x0, y0, label_w, 20),
            text="visible:",
            manager=self.ui_mgr,
            container=self.panel
        )
        dd_vis = UIDropDownMenu(
            options_list=["True", "False"],
            starting_option="True" if node.visible else "False",
            relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
            manager=self.ui_mgr,
            container=self.panel
        )
        dd_vis.user_data = ("prop_visible", node.id)
        self.elements += [lbl_vis, dd_vis]
        y0 += line_h

        # z_order:
        lbl_z = UILabel(
            relative_rect=pygame.Rect(x0, y0, label_w, 20),
            text="z_order:",
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_z = UITextEntryLine(
            relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_z.set_text(str(node.z_order))
        inp_z.user_data = ("prop_z", node.id)
        self.elements += [lbl_z, inp_z]
        y0 += line_h

        # name:
        lbl_name = UILabel(
            relative_rect=pygame.Rect(x0, y0, label_w, 20),
            text="name:",
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_name = UITextEntryLine(
            relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
            manager=self.ui_mgr,
            container=self.panel
        )
        inp_name.set_text(node.name)
        inp_name.user_data = ("prop_name", node.id)
        self.elements += [lbl_name, inp_name]
        y0 += line_h

        # type (read‐only)
        lbl_type = UILabel(
            relative_rect=pygame.Rect(x0, y0, self.rect.width - 20, 20),
            text=f"type: {node.type}",
            manager=self.ui_mgr,
            container=self.panel
        )
        self.elements.append(lbl_type)
        y0 += line_h

        # TYPE-SPECIFIC PROPS & EVENT HOOKUPS:
        # Rectangle: color picker
        if node.type == "Rectangle":
            lbl_c = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="color:",
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_c = UIButton(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                text=str(tuple(node.extra_props.get("color", [200,100,100]))),
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_c.user_data = ("pick_color", node.id)
            self.elements += [lbl_c, btn_c]
            y0 += line_h

        # Button: text, font_size, color, on_click (dropdown of available scripts)
        elif node.type == "Button":
            # text
            lbl_txt = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="text:",
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_txt = UITextEntryLine(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_txt.set_text(node.extra_props.get("text", ""))
            inp_txt.user_data = ("prop_extra_text", node.id)
            self.elements += [lbl_txt, inp_txt]
            y0 += line_h

            # font_size
            lbl_fs = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="font_sz:",
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_fs = UITextEntryLine(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_fs.set_text(str(node.extra_props.get("font_size", 18)))
            inp_fs.user_data = ("prop_extra_font", node.id)
            self.elements += [lbl_fs, inp_fs]
            y0 += line_h

            # color picker
            lbl_c = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="color:",
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_c = UIButton(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                text=str(tuple(node.extra_props.get("color", [100,200,100]))),
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_c.user_data = ("pick_color", node.id)
            self.elements += [lbl_c, btn_c]
            y0 += line_h

            # on_click event hookup
            lbl_ev = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="on_click:",
                manager=self.ui_mgr,
                container=self.panel
            )
            # collect all script names from scripts folder
            scripts = []
            try:
                for fname in os.listdir(self.obj_mgr.scripts_folder):
                    if fname.endswith(".py"):
                        scripts.append(fname[:-3])  # strip .py
            except Exception as e:
                logging.warning(f"couldn't list scripts: {e}")

            # add option “None” plus each script
            options = ["None"] + scripts
            starting = node.events.get("on_click", "None")
            dd_ev = UIDropDownMenu(
                options_list=options,
                starting_option=starting,
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                manager=self.ui_mgr,
                container=self.panel
            )
            dd_ev.user_data = ("prop_event_on_click", node.id)
            self.elements += [lbl_ev, dd_ev]
            y0 += line_h

        # Label: text, font_size, color
        elif node.type == "Label":
            lbl_txt = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="text:",
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_txt = UITextEntryLine(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_txt.set_text(node.extra_props.get("text", ""))
            inp_txt.user_data = ("prop_extra_text", node.id)
            self.elements += [lbl_txt, inp_txt]
            y0 += line_h

            lbl_fs = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="font_sz:",
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_fs = UITextEntryLine(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_fs.set_text(str(node.extra_props.get("font_size", 20)))
            inp_fs.user_data = ("prop_extra_font", node.id)
            self.elements += [lbl_fs, inp_fs]
            y0 += line_h

            lbl_c = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="color:",
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_c = UIButton(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                text=str(tuple(node.extra_props.get("color", [255,255,255]))),
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_c.user_data = ("pick_color", node.id)
            self.elements += [lbl_c, btn_c]
            y0 += line_h

        # Image: pick file
        elif node.type == "Image":
            lbl_img = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="file:",
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_img = UIButton(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                text=(node.extra_props.get("image_path", "") or "Pick Image"),
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_img.user_data = ("pick_image", node.id)
            self.elements += [lbl_img, btn_img]
            y0 += line_h

        # TextInput: placeholder, text_color, bg_color
        elif node.type == "TextInput":
            lbl_ph = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="placeholder:",
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_ph = UITextEntryLine(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                manager=self.ui_mgr,
                container=self.panel
            )
            inp_ph.set_text(node.extra_props.get("placeholder", ""))
            inp_ph.user_data = ("prop_extra_placeholder", node.id)
            self.elements += [lbl_ph, inp_ph]
            y0 += line_h

            lbl_tc = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="text_color:",
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_tc = UIButton(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                text=str(tuple(node.extra_props.get("text_color", [0,0,0]))),
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_tc.user_data = ("pick_color_text", node.id)
            self.elements += [lbl_tc, btn_tc]
            y0 += line_h

            lbl_bc = UILabel(
                relative_rect=pygame.Rect(x0, y0, label_w, 20),
                text="bg_color:",
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_bc = UIButton(
                relative_rect=pygame.Rect(x0 + label_w, y0, input_w, 25),
                text=str(tuple(node.extra_props.get("bg_color", [255,255,255]))),
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_bc.user_data = ("pick_color_bg", node.id)
            self.elements += [lbl_bc, btn_bc]
            y0 += line_h

        # Script: Edit Script but also show event hookups? 
        elif node.type == "Script":
            btn_edit = UIButton(
                relative_rect=pygame.Rect(x0, y0, self.rect.width - 20, 30),
                text="Edit Script",
                manager=self.ui_mgr,
                container=self.panel
            )
            btn_edit.user_data = ("edit_script", node.id)
            self.elements.append(btn_edit)
            y0 += 40

        # Delete button (for all)
        btn_del = UIButton(
            relative_rect=pygame.Rect(x0, y0, self.rect.width - 20, 30),
            text="Delete Object",
            manager=self.ui_mgr,
            container=self.panel
        )
        btn_del.user_data = ("delete_obj", node.id)
        self.elements.append(btn_del)

    def draw(self, surface):
        # nothing manual; pygame_gui draws the panel + widgets
        pass

    def process_event(self, event):
        if not self.selected_id:
            return

        node = self.obj_mgr.get_node(self.selected_id)
        if not node:
            return

        # TEXT ENTRY FINISHED
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            ud = getattr(event.ui_element, "user_data", None)
            if not ud: return
            action, oid = ud
            text = event.text
            try:
                if action == "prop_abs_x":
                    new_abs = int(text)
                    parent_id = node.parent_id
                    if parent_id:
                        px, py = self.obj_mgr.compute_abs_pos(self.obj_mgr.get_node(parent_id))
                        new_rel = new_abs - px
                    else:
                        new_rel = new_abs
                    self.obj_mgr.update_properties(node.id, x=new_rel)
                elif action == "prop_abs_y":
                    new_abs = int(text)
                    parent_id = node.parent_id
                    if parent_id:
                        px, py = self.obj_mgr.compute_abs_pos(self.obj_mgr.get_node(parent_id))
                        new_rel = new_abs - py
                    else:
                        new_rel = new_abs
                    self.obj_mgr.update_properties(node.id, y=new_rel)
                elif action == "prop_w":
                    self.obj_mgr.update_properties(node.id, w=int(text))
                elif action == "prop_h":
                    self.obj_mgr.update_properties(node.id, h=int(text))
                elif action == "prop_z":
                    self.obj_mgr.update_properties(node.id, z_order=int(text))
                elif action == "prop_name":
                    self.obj_mgr.rename_object(node.id, text)
                    self.app.explorer.reload()
                elif action == "prop_extra_text":
                    node.extra_props["text"] = text
                    self.obj_mgr._save_all()
                elif action == "prop_extra_font":
                    node.extra_props["font_size"] = int(text)
                    self.obj_mgr._save_all()
                elif action == "prop_extra_placeholder":
                    node.extra_props["placeholder"] = text
                    self.obj_mgr._save_all()
                # after changes, reload explorer & properties
                self.app.explorer.reload()
                self._rebuild()
            except Exception as e:
                UIMessageWindow(
                    pygame.Rect(300, 250, 400, 200),
                    "Property Error",
                    f"Invalid property input:\n{e}",
                    self.ui_mgr
                )

        # DROPDOWN CHANGES (visible, event_on_click)
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            ud = getattr(event.ui_element, "user_data", None)
            if not ud: return
            action, oid = ud
            try:
                if action == "prop_visible":
                    val = event.text == "True"
                    self.obj_mgr.update_properties(node.id, visible=val)
                    self.app.explorer.reload()
                elif action == "prop_event_on_click":
                    if event.text == "None":
                        # remove any existing hookup
                        if "on_click" in node.events:
                            del node.events["on_click"]
                            self.obj_mgr._save_all()
                    else:
                        # record state & store new hookup
                        script_name = event.text
                        self.obj_mgr.update_properties(node.id, event_on_click=script_name)
                    self._rebuild()
            except Exception as e:
                UIMessageWindow(
                    pygame.Rect(300, 250, 400, 200),
                    "Event Error",
                    f"Couldn't set event:\n{e}",
                    self.ui_mgr
                )

        # BUTTON PRESSES (color picker, image picker, edit script, delete)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ud = getattr(event.ui_element, "user_data", None)
            if not ud: return
            action, oid = ud

            try:
                if action == "pick_color":
                    cur = node.extra_props.get("color", [255,255,255])
                    dlg = UIColorPickerDialog(
                        pygame.Rect(self.rect.x+50, self.rect.y+50, 400, 400),
                        manager=self.ui_mgr,
                        window_title="Pick Color",
                        initial_colour=pygame.Color(*cur)
                    )
                    dlg.user_data = ("color_result", oid, "color")
                elif action == "pick_color_text":
                    cur = node.extra_props.get("text_color", [0,0,0])
                    dlg = UIColorPickerDialog(
                        pygame.Rect(self.rect.x+50, self.rect.y+50, 400, 400),
                        manager=self.ui_mgr,
                        window_title="Pick Text Color",
                        initial_colour=pygame.Color(*cur)
                    )
                    dlg.user_data = ("color_result", oid, "text_color")
                elif action == "pick_color_bg":
                    cur = node.extra_props.get("bg_color", [255,255,255])
                    dlg = UIColorPickerDialog(
                        pygame.Rect(self.rect.x+50, self.rect.y+50, 400, 400),
                        manager=self.ui_mgr,
                        window_title="Pick BG Color",
                        initial_colour=pygame.Color(*cur)
                    )
                    dlg.user_data = ("color_result", oid, "bg_color")
                elif action == "pick_image":
                    dlg = UIFileDialog(
                        pygame.Rect(self.rect.x+50, self.rect.y+50, 600, 400),
                        manager=self.ui_mgr,
                        window_title="Select Image File",
                        initial_file_path=self.obj_mgr.images_folder,
                        allow_existing_files_only=True,
                        file_extensions=[".png", ".jpg", ".bmp", ".jpeg"]
                    )
                    dlg.user_data = ("image_result", oid)
                elif action == "edit_script":
                    script_path = os.path.join(self.obj_mgr.scripts_folder, f"{node.name}.py")
                    open_in_editor(script_path)
                elif action == "delete_obj":
                    self.obj_mgr.delete_object(node.id)
                    self.app.set_selected(None)
                    self.app.explorer.reload()
                    self.clear()
            except Exception as e:
                UIMessageWindow(
                    pygame.Rect(300, 250, 400, 200),
                    "Action Error",
                    f"Couldn't complete action:\n{e}",
                    self.ui_mgr
                )

        # COLOR PICKER RESULT
        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            ud = getattr(event.ui_element, "user_data", None)
            if not ud: return
            _, oid, key = ud
            col = event.colour
            rgb = [col.r, col.g, col.b]
            try:
                node.extra_props[key] = rgb
                self.obj_mgr._save_all()
                self._rebuild()
                self.app.explorer.reload()
            except Exception as e:
                UIMessageWindow(
                    pygame.Rect(300, 250, 400, 200),
                    "Color Error",
                    f"Couldn't set color:\n{e}",
                    self.ui_mgr
                )

        # FILE DIALOG RESULT (image)
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            ud = getattr(event.ui_element, "user_data", None)
            if ud and ud[0] == "image_result":
                oid = ud[1]
                try:
                    path = event.text  # full path
                    node.extra_props["image_path"] = path
                    self.obj_mgr._save_all()
                    self._rebuild()
                except Exception as e:
                    UIMessageWindow(
                        pygame.Rect(300, 250, 400, 200),
                        "Image Error",
                        f"Couldn't set image:\n{e}",
                        self.ui_mgr
                    )
