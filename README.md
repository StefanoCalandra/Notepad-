# Notepad- (C# WinForms)

Versione desktop di Notepad- riscritta in **C# WinForms** per essere usata facilmente con **Visual Studio**.

## Funzionalità
- Multi-tab
- Apri / Salva / Salva con nome / Salva tutto
- Trova / Sostituisci / Vai a riga
- Barra di stato con riga/colonna
- Conferma modifiche non salvate in chiusura
- Scorciatoie principali (`Ctrl+N`, `Ctrl+O`, `Ctrl+S`, `Ctrl+F`, ...)

## Requisiti
- Windows
- .NET 8 SDK (oppure Visual Studio 2022 con workload ".NET desktop development")

## Aprire in Visual Studio
1. Apri la cartella del progetto oppure il file `NotepadWinForms.csproj`.
2. Premi **F5** (Debug) oppure **Ctrl+F5** (Run).

## Avvio con un click (icona)
- Doppio click su **`NotepadWinForms.bat`**.
- Se `NotepadWinForms.exe` esiste già (Release), viene avviato subito.
- Se non esiste, il `.bat` prova a fare la build Release e poi avvia l'exe.

Per avere un'icona desktop:
1. Click destro su `NotepadWinForms.bat` → **Invia a > Desktop (crea collegamento)**.
2. (Opzionale) Proprietà collegamento → **Cambia icona**.

## Avvio da terminale
```bash
dotnet run --project NotepadWinForms.csproj
```

## Build release
```bash
dotnet build NotepadWinForms.csproj -c Release
```

## Come verificare che funziona
1. Avvia l'app (`F5` in VS o doppio click su `NotepadWinForms.bat`).
2. Crea una nuova scheda e scrivi testo.
3. Salva con `Ctrl+S`, chiudi e riapri il file.
4. Prova `Ctrl+F` (Trova), `Ctrl+H` (Sostituisci), `Ctrl+G` (Vai a riga).
5. Modifica un tab e chiudi l'app: deve chiedere conferma salvataggio.
