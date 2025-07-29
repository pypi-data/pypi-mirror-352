# pgstudio/undo_manager.py

import json
import logging

class UndoManager:
    """
    snapshot‐based undo/redo. it stores JSON dumps of the ObjectManager’s entire node state.
    before each mutating action, call record_state(). then if user hits Undo, pop from undo_stack and restore.
    """

    def __init__(self, obj_mgr):
        self.obj_mgr = obj_mgr
        self.undo_stack = []  # list of JSON strings
        self.redo_stack = []

    def record_state(self):
        """
        push the current object state onto undo_stack, clear redo_stack.
        call this at the start of any add/delete/rename/update.
        """
        try:
            # get current state (list of dicts) and dump to string
            state = [n.to_dict() for n in self.obj_mgr.nodes.values()]
            state_json = json.dumps(state)
            self.undo_stack.append(state_json)
            # once you record a new action, redo_stack resets
            self.redo_stack.clear()
        except Exception as e:
            logging.error(f"UndoManager.record_state failed: {e}")

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def undo(self):
        """
        pop last state from undo_stack, push current state to redo_stack, then restore popped.
        returns True if success, False if nothing to undo.
        """
        if not self.can_undo():
            return False
        try:
            current_state = [n.to_dict() for n in self.obj_mgr.nodes.values()]
            self.redo_stack.append(json.dumps(current_state))

            state_json = self.undo_stack.pop()
            state = json.loads(state_json)

            # restore nodes
            self.obj_mgr.nodes.clear()
            for d in state:
                node = self.obj_mgr.ObjectNode.from_dict(d)  # we'll set a reference in ObjectManager
                self.obj_mgr.nodes[node.id] = node

            # save to disk & done
            self.obj_mgr._save_all()
            return True
        except Exception as e:
            logging.error(f"UndoManager.undo failed: {e}")
            return False

    def redo(self):
        """
        pop last state from redo_stack, push current state to undo_stack, then restore popped.
        returns True if success.
        """
        if not self.can_redo():
            return False
        try:
            current_state = [n.to_dict() for n in self.obj_mgr.nodes.values()]
            self.undo_stack.append(json.dumps(current_state))

            state_json = self.redo_stack.pop()
            state = json.loads(state_json)

            # restore nodes
            self.obj_mgr.nodes.clear()
            for d in state:
                node = self.obj_mgr.ObjectNode.from_dict(d)
                self.obj_mgr.nodes[node.id] = node

            self.obj_mgr._save_all()
            return True
        except Exception as e:
            logging.error(f"UndoManager.redo failed: {e}")
            return False
