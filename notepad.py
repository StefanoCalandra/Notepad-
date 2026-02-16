from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Notepad-"
DEFAULT_FONT = ("Consolas", 11)


@dataclass
class TabState:
    frame: ttk.Frame
    text: tk.Text
    line_numbers: tk.Text
    file_path: Path | None = None
    dirty: bool = False
    show_line_numbers: bool = True
    word_wrap: bool = False

    @property
    def title(self) -> str:
        name = self.file_path.name if self.file_path else "Senza titolo"
        return f"{name} *" if self.dirty else name


class NotepadApp:
    def __init__(self, root: tk.Tk, open_path: str | None = None):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1100x700")

        self.tabs: dict[str, TabState] = {}

        self._build_menu()
        self._build_statusbar()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self.new_tab()
        if open_path:
            self.open_file(path_hint=open_path)

    # ----------------------------- UI setup -----------------------------
    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Nuova scheda", command=self.new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Apri...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Salva", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Salva con nome...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Salva tutto", command=self.save_all)
        file_menu.add_separator()
        file_menu.add_command(label="Chiudi scheda", command=self.close_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Chiudi tutte", command=self.close_all_tabs)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.quit)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=False)
        edit_menu.add_command(label="Annulla", command=lambda: self._text_event("<<Undo>>"), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Ripristina", command=lambda: self._text_event("<<Redo>>"), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Taglia", command=lambda: self._text_event("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copia", command=lambda: self._text_event("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Incolla", command=lambda: self._text_event("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_command(label="Seleziona tutto", command=lambda: self._text_event("<<SelectAll>>"), accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Vai a riga...", command=self.go_to_line, accelerator="Ctrl+G")
        menu.add_cascade(label="Modifica", menu=edit_menu)

        search_menu = tk.Menu(menu, tearoff=False)
        search_menu.add_command(label="Trova...", command=self.open_find_dialog, accelerator="Ctrl+F")
        search_menu.add_command(label="Trova e sostituisci...", command=self.open_replace_dialog, accelerator="Ctrl+H")
        menu.add_cascade(label="Cerca", menu=search_menu)

        view_menu = tk.Menu(menu, tearoff=False)
        view_menu.add_command(label="Mostra/Nascondi numeri riga", command=self.toggle_line_numbers)
        view_menu.add_command(label="Attiva/Disattiva word wrap", command=self.toggle_word_wrap)
        menu.add_cascade(label="Vista", menu=view_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Info", command=self.show_about)
        menu.add_cascade(label="Aiuto", menu=help_menu)

        self.root.config(menu=menu)

        self.root.bind_all("<Control-n>", lambda _e: self.new_tab())
        self.root.bind_all("<Control-o>", lambda _e: self.open_file())
        self.root.bind_all("<Control-s>", lambda _e: self.save_file())
        self.root.bind_all("<Control-S>", lambda _e: self.save_file_as())
        self.root.bind_all("<Control-w>", lambda _e: self.close_tab())
        self.root.bind_all("<Control-f>", lambda _e: self.open_find_dialog())
        self.root.bind_all("<Control-h>", lambda _e: self.open_replace_dialog())
        self.root.bind_all("<Control-g>", lambda _e: self.go_to_line())

    def _build_statusbar(self) -> None:
        self.status = ttk.Label(self.root, text="Pronto", anchor="w")
        self.status.pack(side="bottom", fill="x")

    # ----------------------------- Tabs -----------------------------
    def new_tab(self) -> None:
        frame = ttk.Frame(self.notebook)

        line_numbers = tk.Text(
            frame,
            width=4,
            padx=4,
            takefocus=0,
            border=0,
            state="disabled",
            background="#f0f0f0",
            foreground="#666",
        )

        text = tk.Text(frame, wrap="none", undo=True, font=DEFAULT_FONT)
        scroll = ttk.Scrollbar(frame, orient="vertical")
        scroll.configure(command=lambda *a: self._on_scroll(frame, *a))

        text.configure(yscrollcommand=lambda first, last: self._on_text_scroll(frame, first, last))

        line_numbers.pack(side="left", fill="y")
        scroll.pack(side="right", fill="y")
        text.pack(side="right", fill="both", expand=True)

        state = TabState(frame=frame, text=text, line_numbers=line_numbers)
        tab_id = str(frame)
        self.tabs[tab_id] = state

        self.notebook.add(frame, text=state.title)
        self.notebook.select(frame)

        text.bind("<<Modified>>", lambda _e, tid=tab_id: self._on_modified(tid))
        text.bind("<KeyRelease>", lambda _e: self._update_status())
        text.bind("<ButtonRelease>", lambda _e: self._update_status())
        text.bind("<Configure>", lambda _e, tid=tab_id: self._redraw_line_numbers(tid))
        text.bind("<MouseWheel>", lambda e, tid=tab_id: self._on_mousewheel(tid, e))
        text.bind("<Button-4>", lambda e, tid=tab_id: self._on_mousewheel(tid, e))
        text.bind("<Button-5>", lambda e, tid=tab_id: self._on_mousewheel(tid, e))

        self._redraw_line_numbers(tab_id)
        self._update_status()

    def _current_tab(self) -> tuple[str, TabState] | tuple[None, None]:
        selected = self.notebook.select()
        if not selected:
            return None, None
        return selected, self.tabs.get(selected)

    def _set_tab_title(self, tab_id: str) -> None:
        state = self.tabs[tab_id]
        self.notebook.tab(state.frame, text=state.title)

    def _on_tab_change(self, _event=None) -> None:
        tab_id, _ = self._current_tab()
        if tab_id:
            self._redraw_line_numbers(tab_id)
        self._update_status()

    # ----------------------------- Text events -----------------------------
    def _on_modified(self, tab_id: str) -> None:
        state = self.tabs.get(tab_id)
        if not state:
            return
        if state.text.edit_modified():
            state.text.edit_modified(False)
            state.dirty = True
            self._set_tab_title(tab_id)
            self._redraw_line_numbers(tab_id)
            self._update_status()

    def _on_scroll(self, frame: ttk.Frame, *args) -> None:
        tab_id = str(frame)
        state = self.tabs.get(tab_id)
        if not state:
            return
        state.text.yview(*args)
        self._sync_line_number_scroll(tab_id)

    def _on_text_scroll(self, frame: ttk.Frame, first: str, last: str) -> None:
        tab_id = str(frame)
        state = self.tabs.get(tab_id)
        if not state:
            return
        for child in frame.winfo_children():
            if isinstance(child, ttk.Scrollbar):
                child.set(first, last)
        self._sync_line_number_scroll(tab_id)

    def _on_mousewheel(self, tab_id: str, event) -> str:
        state = self.tabs.get(tab_id)
        if not state:
            return "break"
        if getattr(event, "num", None) == 4:
            delta = -1
        elif getattr(event, "num", None) == 5:
            delta = 1
        else:
            delta = int(-1 * (event.delta / 120))
        state.text.yview_scroll(delta, "units")
        self._sync_line_number_scroll(tab_id)
        return "break"

    def _sync_line_number_scroll(self, tab_id: str) -> None:
        state = self.tabs[tab_id]
        if state.show_line_numbers:
            state.line_numbers.yview_moveto(state.text.yview()[0])
        self._redraw_line_numbers(tab_id)

    def _redraw_line_numbers(self, tab_id: str) -> None:
        state = self.tabs.get(tab_id)
        if not state or not state.show_line_numbers:
            return

        end_line = int(state.text.index("end-1c").split(".")[0])
        numbers = "\n".join(str(i) for i in range(1, end_line + 1))

        state.line_numbers.configure(state="normal")
        state.line_numbers.delete("1.0", tk.END)
        state.line_numbers.insert("1.0", numbers)
        state.line_numbers.configure(state="disabled")

    def _text_event(self, event_name: str) -> None:
        _, state = self._current_tab()
        if state:
            state.text.event_generate(event_name)

    # ----------------------------- File actions -----------------------------
    def open_file(self, path_hint: str | None = None) -> None:
        file_str = path_hint or filedialog.askopenfilename()
        if not file_str:
            return

        path = Path(file_str)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="latin-1")
            except OSError as exc:
                messagebox.showerror("Errore", f"Impossibile aprire il file:\n{exc}")
                return
        except OSError as exc:
            messagebox.showerror("Errore", f"Impossibile aprire il file:\n{exc}")
            return

        tab_id, state = self._current_tab()
        if state and not state.dirty and not state.text.get("1.0", "end-1c"):
            target_id, target = tab_id, state
        else:
            self.new_tab()
            target_id, target = self._current_tab()

        if not target_id or not target:
            return

        target.text.delete("1.0", tk.END)
        target.text.insert("1.0", content)
        target.file_path = path
        target.dirty = False
        target.text.edit_modified(False)
        self._set_tab_title(target_id)
        self._redraw_line_numbers(target_id)
        self._update_status()

    def save_file(self) -> None:
        tab_id, state = self._current_tab()
        if not tab_id or not state:
            return
        if state.file_path is None:
            self.save_file_as()
            return
        self._write_tab(tab_id, state.file_path)

    def save_file_as(self) -> None:
        tab_id, state = self._current_tab()
        if not tab_id or not state:
            return
        file_str = filedialog.asksaveasfilename(defaultextension=".txt")
        if not file_str:
            return
        path = Path(file_str)
        state.file_path = path
        self._write_tab(tab_id, path)

    def save_all(self) -> None:
        for tab_id, state in list(self.tabs.items()):
            if not state.dirty:
                continue
            self.notebook.select(state.frame)
            if state.file_path is None:
                self.save_file_as()
            else:
                self._write_tab(tab_id, state.file_path)

    def _write_tab(self, tab_id: str, path: Path) -> bool:
        state = self.tabs[tab_id]
        text = state.text.get("1.0", "end-1c")
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Errore", f"Impossibile salvare il file:\n{exc}")
            return False

        state.file_path = path
        state.dirty = False
        state.text.edit_modified(False)
        self._set_tab_title(tab_id)
        self._update_status()
        return True

    # ----------------------------- Close / quit -----------------------------
    def _confirm_unsaved(self, tab_id: str, intent: str) -> bool:
        state = self.tabs[tab_id]
        if not state.dirty:
            return True

        response = messagebox.askyesnocancel(
            "Modifiche non salvate",
            f"Il file '{state.file_path.name if state.file_path else 'Senza titolo'}' ha modifiche non salvate. {intent}?",
        )

        if response is None:
            return False
        if response:
            self.notebook.select(state.frame)
            self.save_file()
            return not self.tabs[tab_id].dirty
        return True

    def close_tab(self) -> None:
        tab_id, state = self._current_tab()
        if not tab_id or not state:
            return
        if not self._confirm_unsaved(tab_id, "Vuoi salvare prima di chiudere"):
            return

        self.notebook.forget(state.frame)
        self.tabs.pop(tab_id, None)

        if not self.tabs:
            self.new_tab()
        else:
            self._update_status()

    def close_all_tabs(self) -> None:
        for tab_id in list(self.tabs.keys()):
            if not self._confirm_unsaved(tab_id, "Vuoi salvare prima di chiudere"):
                return

        for tab_id, state in list(self.tabs.items()):
            self.notebook.forget(state.frame)
            self.tabs.pop(tab_id, None)

        self.new_tab()

    def quit(self) -> None:
        for tab_id in list(self.tabs.keys()):
            if not self._confirm_unsaved(tab_id, "Vuoi salvare prima di uscire"):
                return
        self.root.destroy()

    # ----------------------------- Search / replace / goto -----------------------------
    def open_find_dialog(self) -> None:
        self._open_search_dialog(with_replace=False)

    def open_replace_dialog(self) -> None:
        self._open_search_dialog(with_replace=True)

    def _open_search_dialog(self, with_replace: bool) -> None:
        _, state = self._current_tab()
        if not state:
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Trova" if not with_replace else "Trova e sostituisci")
        dlg.transient(self.root)
        dlg.resizable(False, False)

        ttk.Label(dlg, text="Trova:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        find_entry = ttk.Entry(dlg, width=35)
        find_entry.grid(row=0, column=1, padx=8, pady=8)
        find_entry.focus()

        replace_entry = None
        if with_replace:
            ttk.Label(dlg, text="Sostituisci:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
            replace_entry = ttk.Entry(dlg, width=35)
            replace_entry.grid(row=1, column=1, padx=8, pady=8)

        def find_next() -> None:
            query = find_entry.get()
            if not query:
                return
            start = state.text.search(query, "insert", tk.END)
            if not start:
                start = state.text.search(query, "1.0", tk.END)
                if not start:
                    messagebox.showinfo("Trova", "Nessuna occorrenza trovata.")
                    return

            end = f"{start}+{len(query)}c"
            state.text.tag_remove("search", "1.0", tk.END)
            state.text.tag_add("search", start, end)
            state.text.tag_config("search", background="yellow")
            state.text.mark_set("insert", end)
            state.text.see(start)
            self._update_status()

        def replace_one() -> None:
            if not replace_entry:
                return
            ranges = state.text.tag_ranges("search")
            if not ranges:
                find_next()
                ranges = state.text.tag_ranges("search")
                if not ranges:
                    return
            state.text.delete(ranges[0], ranges[1])
            state.text.insert(ranges[0], replace_entry.get())
            state.text.tag_remove("search", "1.0", tk.END)
            state.text.edit_modified(True)
            self._on_modified(str(state.frame))

        def replace_all() -> None:
            if not replace_entry:
                return
            query = find_entry.get()
            replacement = replace_entry.get()
            if not query:
                return
            full = state.text.get("1.0", tk.END)
            if query not in full:
                messagebox.showinfo("Sostituisci", "Nessuna occorrenza trovata.")
                return
            state.text.delete("1.0", tk.END)
            state.text.insert("1.0", full.replace(query, replacement))
            state.text.edit_modified(True)
            self._on_modified(str(state.frame))

        row = 2 if with_replace else 1
        ttk.Button(dlg, text="Trova successivo", command=find_next).grid(row=row, column=0, padx=8, pady=8)
        if with_replace:
            ttk.Button(dlg, text="Sostituisci", command=replace_one).grid(row=row, column=1, padx=8, pady=8, sticky="w")
            ttk.Button(dlg, text="Sostituisci tutto", command=replace_all).grid(row=row + 1, column=1, padx=8, pady=(0, 8), sticky="w")

    def go_to_line(self) -> None:
        _, state = self._current_tab()
        if not state:
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Vai a riga")
        dlg.transient(self.root)
        dlg.resizable(False, False)

        ttk.Label(dlg, text="Numero riga:").grid(row=0, column=0, padx=8, pady=8)
        entry = ttk.Entry(dlg, width=10)
        entry.grid(row=0, column=1, padx=8, pady=8)
        entry.focus()

        def submit() -> None:
            value = entry.get().strip()
            if not value.isdigit():
                messagebox.showerror("Errore", "Inserisci un numero valido.")
                return

            max_line = int(state.text.index("end-1c").split(".")[0])
            line = max(1, min(int(value), max_line))
            state.text.mark_set("insert", f"{line}.0")
            state.text.see(f"{line}.0")
            state.text.focus_set()
            self._update_status()
            dlg.destroy()

        ttk.Button(dlg, text="Vai", command=submit).grid(row=1, column=0, columnspan=2, pady=(0, 8))

    # ----------------------------- View / status -----------------------------
    def toggle_line_numbers(self) -> None:
        tab_id, state = self._current_tab()
        if not tab_id or not state:
            return

        state.show_line_numbers = not state.show_line_numbers
        if state.show_line_numbers:
            state.line_numbers.pack(side="left", fill="y")
        else:
            state.line_numbers.pack_forget()
        self._redraw_line_numbers(tab_id)

    def toggle_word_wrap(self) -> None:
        _, state = self._current_tab()
        if not state:
            return
        state.word_wrap = not state.word_wrap
        state.text.configure(wrap="word" if state.word_wrap else "none")

    def _update_status(self) -> None:
        _, state = self._current_tab()
        if not state:
            self.status.config(text="Pronto")
            return

        line, col = state.text.index("insert").split(".")
        name = str(state.file_path) if state.file_path else "Senza titolo"
        dirty = " *" if state.dirty else ""
        self.status.config(text=f"{name}{dirty} | Riga {line}, Colonna {int(col) + 1}")

    def show_about(self) -> None:
        messagebox.showinfo("Info", "Notepad-\nEditor testuale scritto in Python (tkinter).")


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Notepad-: programma desktop in Python")
    parser.add_argument("file", nargs="?", help="file da aprire all'avvio")
    return parser.parse_args(argv)


def run(open_path: str | None = None) -> None:
    root = tk.Tk()
    NotepadApp(root, open_path=open_path)
    root.mainloop()


if __name__ == "__main__":
    args = parse_args()
    run(args.file)
