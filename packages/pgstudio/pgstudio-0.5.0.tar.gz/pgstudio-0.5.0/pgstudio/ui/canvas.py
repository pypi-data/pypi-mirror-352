# pgstudio/ui/canvas.py

import pygame
from typing import Optional, Tuple
from ..objects import ObjectManager, ObjectNode
from pygame_gui.windows import UIMessageWindow
import logging

class Canvas:
    """
    central area where objects are drawn & can be selected/dragged/resized.
    uses nested transforms: children follow parent. z_order respected.
    draws:
      - Rectangle
      - Button (rectangle+text)
      - Label (text)
      - Image (loads from path)
      - TextInput (placeholder draw)
      - Script (gray box)
    """

    def __init__(self, app, rect: pygame.Rect):
        self.app = app
        self.obj_mgr: ObjectManager = app.obj_mgr
        self.ui_mgr = app.ui_manager
        self.rect = rect

        self.dragging = False
        self.drag_offset: Tuple[int,int] = (0, 0)
        self.resizing = False
        self.resize_start = (0, 0, 0, 0)  # x,y,w,h
        self.resize_mouse_start = (0, 0)

        logging.info("Canvas initialized")

    def draw(self, surface):
        # draw background
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        # draw all objects by z_order ascending
        nodes = sorted(self.obj_mgr.get_all_nodes(), key=lambda n: (n.z_order, n.id))
        for node in nodes:
            if not node.visible:
                continue
            try:
                ax, ay = self.obj_mgr.compute_abs_pos(node)
                x = self.rect.x + ax
                y = self.rect.y + ay
                w = node.w
                h = node.h

                if node.type == "Rectangle":
                    clr = node.extra_props.get("color", [200,100,100])
                    pygame.draw.rect(surface, tuple(clr), (x, y, w, h))
                elif node.type == "Button":
                    clr = node.extra_props.get("color", [100,200,100])
                    pygame.draw.rect(surface, tuple(clr), (x, y, w, h))
                    font = pygame.font.SysFont(None, node.extra_props.get("font_size", 18))
                    txt_surf = font.render(node.extra_props.get("text", node.name), True, (255,255,255))
                    surface.blit(txt_surf, (x+5, y+5))
                elif node.type == "Label":
                    font = pygame.font.SysFont(None, node.extra_props.get("font_size", 20))
                    clr = node.extra_props.get("color", [255,255,255])
                    txt_surf = font.render(node.extra_props.get("text", node.name), True, tuple(clr))
                    surface.blit(txt_surf, (x, y))
                elif node.type == "Image":
                    img_path = node.extra_props.get("image_path", "")
                    if img_path:
                        try:
                            surf = pygame.image.load(img_path)
                            surf = pygame.transform.scale(surf, (w, h))
                            surface.blit(surf, (x, y))
                        except Exception:
                            pygame.draw.rect(surface, (80,80,80), (x, y, w, h))
                            font = pygame.font.SysFont(None, 14)
                            err = font.render("Image Err", True, (255,0,0))
                            surface.blit(err, (x+5, y+5))
                    else:
                        pygame.draw.rect(surface, (120,120,120), (x, y, w, h))
                        font = pygame.font.SysFont(None, 14)
                        txt = font.render("No Image", True, (200,200,200))
                        surface.blit(txt, (x+5, y+5))
                elif node.type == "TextInput":
                    bg = node.extra_props.get("bg_color", [255,255,255])
                    pygame.draw.rect(surface, tuple(bg), (x, y, w, h))
                    font = pygame.font.SysFont(None, node.extra_props.get("font_size", 18))
                    txt = node.extra_props.get("placeholder", "")
                    txt_surf = font.render(txt, True, tuple(node.extra_props.get("text_color", [0,0,0])))
                    surface.blit(txt_surf, (x+5, y+5))
                elif node.type == "Script":
                    pygame.draw.rect(surface, (80,80,80), (x, y, w, h))
                    font = pygame.font.SysFont(None, 14)
                    lbl = font.render(f"Script: {node.name}", True, (220,220,220))
                    surface.blit(lbl, (x+5, y+5))

                # if selected, draw outline & resize handle
                if self.app.selected_id == node.id:
                    pygame.draw.rect(surface, (255,255,0), (x, y, w, h), 2)
                    # bottom-right handle
                    hs = 10
                    pygame.draw.rect(surface, (255,255,0), (x + w - hs, y + h - hs, hs, hs))
            except Exception as e:
                # show error dialog if anything in draw breaks
                UIMessageWindow(
                    pygame.Rect(self.rect.x + 50, self.rect.y + 50, 400, 200),
                    "Canvas Draw Error",
                    f"Error drawing object {node.name}:\n{e}",
                    self.ui_mgr
                )
                logging.error(f"Canvas draw error on {node.id}: {e}")

    def process_event(self, event):
        # left-click for selecting, dragging, resizing
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.rect.collidepoint((mx, my)):
                rel_x = mx - self.rect.x
                rel_y = my - self.rect.y
                clicked = self._get_topmost(rel_x, rel_y)
                if clicked:
                    self.app.set_selected(clicked.id)
                    # check if resizing (10x10 corner)
                    ax, ay = self.obj_mgr.compute_abs_pos(clicked)
                    local_x = rel_x - ax
                    local_y = rel_y - ay
                    if local_x >= clicked.w - 10 and local_y >= clicked.h - 10:
                        self.resizing = True
                        self.resize_mouse_start = (rel_x, rel_y)
                        self.resize_start = (clicked.x, clicked.y, clicked.w, clicked.h)
                        logging.debug(f"start resizing {clicked.id}")
                    else:
                        # dragging
                        self.dragging = True
                        abs_x, abs_y = self.obj_mgr.compute_abs_pos(clicked)
                        self.drag_offset = (rel_x - abs_x, rel_y - abs_y)
                        logging.debug(f"start dragging {clicked.id}")
                else:
                    self.app.set_selected(None)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            self.resizing = False

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            rel_x = mx - self.rect.x
            rel_y = my - self.rect.y
            sel = self.app.get_selected()
            if sel:
                try:
                    if self.dragging:
                        new_abs_x = rel_x - self.drag_offset[0]
                        new_abs_y = rel_y - self.drag_offset[1]
                        if sel.parent_id:
                            px, py = self.obj_mgr.compute_abs_pos(self.obj_mgr.get_node(sel.parent_id))
                            new_rel_x = new_abs_x - px
                            new_rel_y = new_abs_y - py
                        else:
                            new_rel_x = new_abs_x
                            new_rel_y = new_abs_y
                        sel.x = new_rel_x
                        sel.y = new_rel_y
                        self.obj_mgr.update_properties(sel.id, x=new_rel_x, y=new_rel_y)
                        self.app.properties._rebuild()
                    if self.resizing:
                        mx2, my2 = event.pos
                        rel_x2 = mx2 - self.rect.x
                        rel_y2 = my2 - self.rect.y
                        dx = rel_x2 - self.resize_mouse_start[0]
                        dy = rel_y2 - self.resize_mouse_start[1]
                        orig_x, orig_y, orig_w, orig_h = self.resize_start
                        new_w = max(10, orig_w + dx)
                        new_h = max(10, orig_h + dy)
                        sel.w = new_w
                        sel.h = new_h
                        self.obj_mgr.update_properties(sel.id, w=new_w, h=new_h)
                        self.app.properties._rebuild()
                except Exception as e:
                    UIMessageWindow(
                        pygame.Rect(self.rect.x + 50, self.rect.y + 50, 400, 200),
                        "Canvas Error",
                        f"Error during drag/resize:\n{e}",
                        self.ui_mgr
                    )
                    logging.error(f"Canvas process_event error on {sel.id}: {e}")

        # pass event to UIManager (for embedded dialogs)
        self.ui_mgr.process_events(event)

    def _get_topmost(self, x: int, y: int) -> Optional[ObjectNode]:
        """
        return the topmost (highest z_order) node under canvas coords x,y.
        """
        candidates = []
        for node in self.obj_mgr.get_all_nodes():
            if not node.visible:
                continue
            ax, ay = self.obj_mgr.compute_abs_pos(node)
            rect = pygame.Rect(ax, ay, node.w, node.h)
            if rect.collidepoint((x, y)):
                candidates.append(node)
        if not candidates:
            return None
        candidates.sort(key=lambda n: (n.z_order, n.id), reverse=True)
        return candidates[0]
