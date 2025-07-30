
# PgStudio 0.5.0

## 🚧 Notice: Beta Software

PgStudio is in **early beta** and still under active development. Please expect bugs and incomplete features. We welcome your feedback—submit bug reports and feature requests via our Discord server: [Taireru LLC ™ // PgStudio // #bugs-and-stuff](https://discord.gg/36xVkTcuz5).

> **Note:** PgStudio is **not affiliated** with `pygame`, `pygame_gui`, or PostgreSQL. Despite the name, PgStudio is a standalone GUI editor built to assist with development of `pygame` applications using `pygame_gui`.

---

PgStudio is a drag-and-drop GUI editor for **pygame**, powered by **pygame_gui**.

---

## 🔄 What’s New in 0.5.0

- **Error Dialogs:** Clear `UIMessageWindow` pop-ups appear when operations like save/export/draw fail.
- **Theming Support:** PgStudio will automatically apply styles from `themes/pgstudio_theme.json` if it exists.
- **Undo/Redo:** All object edits (add, delete, rename, property changes) are tracked with full undo/redo support.
- **Custom Button Events:** You can now assign scripts to **Button** `on_click` events using your `/scripts/` folder.

---

## 📜 License Agreement

Upon launching PgStudio, a **Software User Agreement** will appear. You must accept the agreement to use the software.

Key terms:
- You must agree to the terms before use.
- **Do not** copy, modify, redistribute, or create derivatives of PgStudio.
- Viewing source code is allowed for learning, not modification.
- Content you create is yours; PgStudio itself remains proprietary.
- Declining or closing the prompt will attempt to uninstall the software.
- Usage is governed under the laws of Arkansas, USA.

**If you do not agree, you may not use PgStudio.**

---

## 📦 Installation

```bash
pip install pgstudio
````

---

## 🚀 Quickstart

```python
import pgstudio

pgstudio.configure(core="path/to/my_project_folder")
pgstudio.launch()
```

This creates:

* `my_project_folder/objects.json`
* `my_project_folder/scripts/`
* `my_project_folder/images/`
* *(optional)* `my_project_folder/themes/pgstudio_theme.json` — for custom theming

---

## 🧭 UI Overview

### 1. **Toolbar (Top)**

* **Undo/Redo:** Revert or reapply recent changes
* **Save:** Manually save `objects.json`
* **Export:** Generate `main.py` with event bindings
* **New Project:** Clears all objects/scripts/images (with confirmation)

### 2. **Explorer (Left)**

* Hierarchical tree of all objects
* Right-click blank → add root object
* Right-click object → add child / rename / delete
* Arrow icon ▶/▼ toggles expansion

### 3. **Canvas (Center)**

* Drag objects with real-time layout updates
* Resize using bottom-right corner
* Draw order determined by `z_order`
* Yellow outline highlights selected objects

### 4. **Properties (Right)**

* Editable fields:

  * **abs\_x**, **abs\_y**, **w**, **h**, **visible**, **z\_order**, **name**
* Type-specific options:

  * **Rectangle:** color
  * **Button:** text, font size, color, `on_click` script
  * **Label:** text, font size, color
  * **Image:** file picker
  * **TextInput:** placeholder, text color, background
  * **Script:** “Edit Script” button
* Delete object button at bottom

### 5. **Error Handling**

* All errors (I/O, invalid inputs, etc.) open a `UIMessageWindow` with details.

### 6. **Theming**

* Load `themes/pgstudio_theme.json` if present.
* Customizable UI: buttons, panels, fonts, etc.

---

## ↩️ Undo/Redo Details

* Every mutation (add/delete/rename/update) snapshots the full `nodes` structure.
* Undo: reverts to last snapshot.
* Redo: reapplies previously undone snapshot.
* Supported operations:

  * `add_object`
  * `delete_object`
  * `rename_object`
  * `update_properties`
  * `move_node`

---

## ⚡ Custom Button Events

* Only **Buttons** currently support event bindings.
* In Properties panel, select an `on_click` script from `/scripts/`.
* On export, `main.py` is generated with proper event wiring:

```python
import scripts.MyScript as script_<button_id>

...

if e.type == pygame_gui.UI_BUTTON_PRESSED and e.ui_element == elements['<button_id>']:
    script_<button_id>.run(elements['<button_id>'], event=e)
```

In `scripts/MyScript.py`:

```python
def run(obj, event=None):
    # Do something with the clicked button
```

---

## 🎨 Theming

* The default theme file is `themes/pgstudio_theme.json`
* Customize fonts, button colors, panel styles, and more.
* If missing or renamed, PgStudio falls back to default `pygame_gui` theme.

---

## ❗ Error Dialogs

* Any failure—drawing, file I/O, invalid user actions—triggers a `UIMessageWindow` with a descriptive message.

---

## 🧪 Local Development

1. Open terminal and run:

   ```bash
   pip install pgstudio
   ```
2. Open your IDE.
3. Create and run this test script:

   ```python
   import pgstudio
   pgstudio.configure("my_test_project")
   pgstudio.launch()
   ```

---

Enjoy building UIs without writing boilerplate—just drag, drop, click, and export!
**Happy coding!** 🚀🎨