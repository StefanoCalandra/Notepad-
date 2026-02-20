using System.Text;

namespace NotepadWinForms;

public class MainForm : Form
{
    private readonly TabControl _tabControl = new() { Dock = DockStyle.Fill };
    private readonly StatusStrip _statusStrip = new();
    private readonly ToolStripStatusLabel _statusLabel = new() { Text = "Pronto" };

    public MainForm()
    {
        Text = "Notepad- (C# WinForms)";
        Width = 1100;
        Height = 700;

        Controls.Add(_tabControl);

        _statusStrip.Items.Add(_statusLabel);
        Controls.Add(_statusStrip);

        MainMenuStrip = BuildMenu();
        Controls.Add(MainMenuStrip);

        _tabControl.SelectedIndexChanged += (_, _) => UpdateStatus();

        NewTab();
    }

    private MenuStrip BuildMenu()
    {
        var menu = new MenuStrip();

        var fileMenu = new ToolStripMenuItem("File");
        fileMenu.DropDownItems.Add("Nuova scheda", null, (_, _) => NewTab()).ShortcutKeys = Keys.Control | Keys.N;
        fileMenu.DropDownItems.Add("Apri...", null, (_, _) => OpenFile()).ShortcutKeys = Keys.Control | Keys.O;
        fileMenu.DropDownItems.Add("Salva", null, (_, _) => SaveCurrent()).ShortcutKeys = Keys.Control | Keys.S;
        fileMenu.DropDownItems.Add("Salva con nome...", null, (_, _) => SaveCurrentAs()).ShortcutKeys = Keys.Control | Keys.Shift | Keys.S;
        fileMenu.DropDownItems.Add("Salva tutto", null, (_, _) => SaveAll());
        fileMenu.DropDownItems.Add(new ToolStripSeparator());
        fileMenu.DropDownItems.Add("Chiudi scheda", null, (_, _) => CloseCurrent()).ShortcutKeys = Keys.Control | Keys.W;
        fileMenu.DropDownItems.Add("Esci", null, (_, _) => Close());

        var editMenu = new ToolStripMenuItem("Modifica");
        editMenu.DropDownItems.Add("Annulla", null, (_, _) => CurrentEditor()?.Undo()).ShortcutKeys = Keys.Control | Keys.Z;
        editMenu.DropDownItems.Add("Taglia", null, (_, _) => CurrentEditor()?.Cut()).ShortcutKeys = Keys.Control | Keys.X;
        editMenu.DropDownItems.Add("Copia", null, (_, _) => CurrentEditor()?.Copy()).ShortcutKeys = Keys.Control | Keys.C;
        editMenu.DropDownItems.Add("Incolla", null, (_, _) => CurrentEditor()?.Paste()).ShortcutKeys = Keys.Control | Keys.V;
        editMenu.DropDownItems.Add("Seleziona tutto", null, (_, _) => CurrentEditor()?.SelectAll()).ShortcutKeys = Keys.Control | Keys.A;

        var searchMenu = new ToolStripMenuItem("Cerca");
        searchMenu.DropDownItems.Add("Trova...", null, (_, _) => FindText()).ShortcutKeys = Keys.Control | Keys.F;
        searchMenu.DropDownItems.Add("Sostituisci...", null, (_, _) => ReplaceText()).ShortcutKeys = Keys.Control | Keys.H;
        searchMenu.DropDownItems.Add("Vai a riga...", null, (_, _) => GoToLine()).ShortcutKeys = Keys.Control | Keys.G;

        var helpMenu = new ToolStripMenuItem("Aiuto");
        helpMenu.DropDownItems.Add("Info", null, (_, _) => MessageBox.Show("Notepad- in C# WinForms", "Info"));

        menu.Items.Add(fileMenu);
        menu.Items.Add(editMenu);
        menu.Items.Add(searchMenu);
        menu.Items.Add(helpMenu);

        return menu;
    }

    private void NewTab(string? title = null, string content = "", string? filePath = null)
    {
        var editor = new RichTextBox
        {
            Dock = DockStyle.Fill,
            AcceptsTab = true,
            WordWrap = false,
            Font = new Font("Consolas", 11),
            Text = content
        };

        var page = new TabPage(title ?? "Senza titolo") { Tag = new DocumentState(filePath) };
        page.Controls.Add(editor);

        editor.TextChanged += (_, _) =>
        {
            if (page.Tag is not DocumentState doc || doc.IsLoading)
            {
                UpdateStatus();
                return;
            }

            doc.Dirty = true;
            UpdateTabTitle(page, doc);
            UpdateStatus();
        };
        editor.SelectionChanged += (_, _) => UpdateStatus();

        _tabControl.TabPages.Add(page);
        _tabControl.SelectedTab = page;

        if (page.Tag is DocumentState document)
        {
            document.Dirty = false;
            UpdateTabTitle(page, document);
        }
        UpdateStatus();
    }

    private RichTextBox? CurrentEditor() => _tabControl.SelectedTab?.Controls.OfType<RichTextBox>().FirstOrDefault();

    private DocumentState? CurrentDocument() => _tabControl.SelectedTab?.Tag as DocumentState;

    private void UpdateTabTitle(TabPage page, DocumentState doc)
    {
        var baseName = string.IsNullOrWhiteSpace(doc.FilePath) ? "Senza titolo" : Path.GetFileName(doc.FilePath);
        page.Text = doc.Dirty ? $"{baseName} *" : baseName;
    }

    private bool IsEmptyUntouchedTab(TabPage? page)
    {
        if (page is null) return false;
        if (page.Tag is not DocumentState doc) return false;
        var editor = page.Controls.OfType<RichTextBox>().FirstOrDefault();
        return editor is not null && !doc.Dirty && string.IsNullOrWhiteSpace(doc.FilePath) && editor.TextLength == 0;
    }

    private void LoadDocumentIntoTab(TabPage page, string filePath, string text)
    {
        if (page.Tag is not DocumentState doc) return;
        var editor = page.Controls.OfType<RichTextBox>().FirstOrDefault();
        if (editor is null) return;

        doc.IsLoading = true;
        editor.Text = text;
        doc.FilePath = filePath;
        doc.Dirty = false;
        doc.IsLoading = false;
        UpdateTabTitle(page, doc);
        UpdateStatus();
    }

    private void OpenFile()
    {
        using var dialog = new OpenFileDialog
        {
            Filter = "Text files|*.txt;*.cs;*.json;*.xml;*.md|All files|*.*"
        };
        if (dialog.ShowDialog() != DialogResult.OK)
            return;

        try
        {
            var text = File.ReadAllText(dialog.FileName, Encoding.UTF8);
            var current = _tabControl.SelectedTab;

            if (IsEmptyUntouchedTab(current) && current is not null)
            {
                LoadDocumentIntoTab(current, dialog.FileName, text);
            }
            else
            {
                NewTab(Path.GetFileName(dialog.FileName), string.Empty, dialog.FileName);
                if (_tabControl.SelectedTab is { } selected)
                    LoadDocumentIntoTab(selected, dialog.FileName, text);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Errore in apertura file:
{ex.Message}", "Errore", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private bool SaveCurrent()
    {
        var doc = CurrentDocument();
        var editor = CurrentEditor();
        var page = _tabControl.SelectedTab;
        if (doc is null || editor is null || page is null)
            return false;

        if (string.IsNullOrWhiteSpace(doc.FilePath))
            return SaveCurrentAs();

        try
        {
            File.WriteAllText(doc.FilePath, editor.Text, Encoding.UTF8);
            doc.Dirty = false;
            UpdateTabTitle(page, doc);
            UpdateStatus();
            return true;
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Errore in salvataggio:
{ex.Message}", "Errore", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return false;
        }
    }

    private bool SaveCurrentAs()
    {
        var doc = CurrentDocument();
        if (doc is null)
            return false;

        using var dialog = new SaveFileDialog
        {
            Filter = "Text files|*.txt|All files|*.*",
            FileName = string.IsNullOrWhiteSpace(doc.FilePath) ? "documento.txt" : Path.GetFileName(doc.FilePath)
        };
        if (dialog.ShowDialog() != DialogResult.OK)
            return false;

        doc.FilePath = dialog.FileName;
        return SaveCurrent();
    }

    private bool SaveAll()
    {
        var current = _tabControl.SelectedTab;

        foreach (TabPage page in _tabControl.TabPages)
        {
            _tabControl.SelectedTab = page;
            if (page.Tag is DocumentState { Dirty: true } && !SaveCurrent())
            {
                _tabControl.SelectedTab = current;
                return false;
            }
        }

        _tabControl.SelectedTab = current;
        UpdateStatus();
        return true;
    }

    private bool ConfirmClose(TabPage page)
    {
        if (page.Tag is not DocumentState doc || !doc.Dirty)
            return true;

        var answer = MessageBox.Show(
            $"Salvare le modifiche in '{(string.IsNullOrWhiteSpace(doc.FilePath) ? "Senza titolo" : Path.GetFileName(doc.FilePath))}'?",
            "Conferma",
            MessageBoxButtons.YesNoCancel,
            MessageBoxIcon.Question);

        if (answer == DialogResult.Cancel)
            return false;

        if (answer == DialogResult.Yes)
        {
            _tabControl.SelectedTab = page;
            return SaveCurrent();
        }

        return true;
    }

    private void CloseCurrent()
    {
        var page = _tabControl.SelectedTab;
        if (page is null)
            return;

        if (!ConfirmClose(page))
            return;

        _tabControl.TabPages.Remove(page);
        if (_tabControl.TabPages.Count == 0)
            NewTab();

        UpdateStatus();
    }

    private void FindText()
    {
        var editor = CurrentEditor();
        if (editor is null) return;

        var query = PromptDialog.Show("Testo da cercare:", "Trova");
        if (string.IsNullOrEmpty(query)) return;

        var start = editor.SelectionStart + editor.SelectionLength;
        var index = editor.Text.IndexOf(query, start, StringComparison.CurrentCultureIgnoreCase);
        if (index < 0)
            index = editor.Text.IndexOf(query, 0, StringComparison.CurrentCultureIgnoreCase);

        if (index >= 0)
        {
            editor.Select(index, query.Length);
            editor.ScrollToCaret();
            editor.Focus();
        }
        else
        {
            MessageBox.Show("Nessuna occorrenza trovata.", "Trova");
        }
    }

    private void ReplaceText()
    {
        var editor = CurrentEditor();
        if (editor is null) return;

        using var dialog = new ReplaceDialog();
        if (dialog.ShowDialog() != DialogResult.OK)
            return;

        if (string.IsNullOrEmpty(dialog.FindTextValue))
            return;

        editor.Text = editor.Text.Replace(dialog.FindTextValue, dialog.ReplaceTextValue, StringComparison.CurrentCultureIgnoreCase);
        if (CurrentDocument() is { } doc && _tabControl.SelectedTab is { } page)
        {
            doc.Dirty = true;
            UpdateTabTitle(page, doc);
        }
        UpdateStatus();
    }

    private void GoToLine()
    {
        var editor = CurrentEditor();
        if (editor is null) return;

        var input = PromptDialog.Show("Numero riga:", "Vai a riga");
        if (!int.TryParse(input, out var line) || line <= 0)
            return;

        line = Math.Min(line, editor.Lines.Length == 0 ? 1 : editor.Lines.Length);
        var charIndex = editor.GetFirstCharIndexFromLine(line - 1);
        if (charIndex >= 0)
        {
            editor.SelectionStart = charIndex;
            editor.SelectionLength = 0;
            editor.ScrollToCaret();
            editor.Focus();
        }
    }

    private void UpdateStatus()
    {
        var editor = CurrentEditor();
        var doc = CurrentDocument();
        if (editor is null || doc is null)
        {
            _statusLabel.Text = "Pronto";
            return;
        }

        var line = editor.GetLineFromCharIndex(editor.SelectionStart) + 1;
        var col = editor.SelectionStart - editor.GetFirstCharIndexOfCurrentLine() + 1;
        var name = string.IsNullOrWhiteSpace(doc.FilePath) ? "Senza titolo" : doc.FilePath;
        var dirty = doc.Dirty ? " *" : string.Empty;
        _statusLabel.Text = $"{name}{dirty} | Riga {line}, Colonna {col}";
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        foreach (TabPage page in _tabControl.TabPages)
        {
            if (!ConfirmClose(page))
            {
                e.Cancel = true;
                return;
            }
        }

        base.OnFormClosing(e);
    }

    private sealed class DocumentState(string? filePath)
    {
        public string? FilePath { get; set; } = filePath;
        public bool Dirty { get; set; }
        public bool IsLoading { get; set; }
    }
}

internal static class PromptDialog
{
    public static string? Show(string label, string title)
    {
        using var form = new Form
        {
            Text = title,
            Width = 420,
            Height = 150,
            FormBorderStyle = FormBorderStyle.FixedDialog,
            StartPosition = FormStartPosition.CenterParent,
            MinimizeBox = false,
            MaximizeBox = false
        };

        var lbl = new Label { Left = 12, Top = 12, Text = label, Width = 380 };
        var txt = new TextBox { Left = 12, Top = 36, Width = 380 };
        var ok = new Button { Text = "OK", Left = 236, Width = 75, Top = 70, DialogResult = DialogResult.OK };
        var cancel = new Button { Text = "Annulla", Left = 317, Width = 75, Top = 70, DialogResult = DialogResult.Cancel };

        form.Controls.AddRange([lbl, txt, ok, cancel]);
        form.AcceptButton = ok;
        form.CancelButton = cancel;

        return form.ShowDialog() == DialogResult.OK ? txt.Text : null;
    }
}

internal sealed class ReplaceDialog : Form
{
    private readonly TextBox _find = new() { Left = 130, Top = 14, Width = 240 };
    private readonly TextBox _replace = new() { Left = 130, Top = 44, Width = 240 };

    public string FindTextValue => _find.Text;
    public string ReplaceTextValue => _replace.Text;

    public ReplaceDialog()
    {
        Text = "Sostituisci";
        Width = 400;
        Height = 150;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        StartPosition = FormStartPosition.CenterParent;
        MinimizeBox = false;
        MaximizeBox = false;

        Controls.Add(new Label { Text = "Trova:", Left = 12, Top = 18, Width = 110 });
        Controls.Add(new Label { Text = "Sostituisci con:", Left = 12, Top = 48, Width = 110 });
        Controls.Add(_find);
        Controls.Add(_replace);

        var ok = new Button { Text = "OK", Left = 214, Width = 75, Top = 78, DialogResult = DialogResult.OK };
        var cancel = new Button { Text = "Annulla", Left = 295, Width = 75, Top = 78, DialogResult = DialogResult.Cancel };
        Controls.Add(ok);
        Controls.Add(cancel);

        AcceptButton = ok;
        CancelButton = cancel;
    }
}
