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

## Avvio da terminale
```bash
dotnet run --project NotepadWinForms.csproj
```

## Build release
```bash
dotnet build NotepadWinForms.csproj -c Release
```
