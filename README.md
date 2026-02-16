# Notepad- (riscritto in Python)

`Notepad-` è un editor desktop **scritto in Python** con `tkinter`, ispirato a Notepad++.

## Cosa fa
- Multi-tab
- Apri / Salva / Salva con nome / Salva tutto
- Numeri di riga attivabili
- Word wrap
- Trova / Trova e sostituisci
- Vai a riga
- Barra di stato (file + posizione cursore)
- Scorciatoie principali da tastiera

## Requisiti
- Python 3.9+
- Tkinter disponibile nella tua installazione Python

## Avvio classico
```bash
python main.py
```

Aprire un file direttamente all'avvio:
```bash
python main.py percorso/file.txt
```

## Avvio cliccando un'icona

### Windows
Hai due opzioni:
1. **Doppio click su `Notepad-.pyw`** (nessuna finestra console).
2. **Doppio click su `Notepad-.bat`**.

Per avere una vera icona sul desktop:
- click destro su `Notepad-.pyw` → **Invia a > Desktop (crea collegamento)**;
- sul collegamento: **Proprietà > Cambia icona** (facoltativo).

### Linux (desktop entry)
1. Copia `notepad.desktop` sul Desktop o in `~/.local/share/applications/`.
2. Modifica la riga `Exec=` con il percorso reale della tua cartella progetto.
3. Rendi il file eseguibile:
   ```bash
   chmod +x notepad.desktop
   ```
4. Aprilo con doppio click.

## Scorciatoie
- `Ctrl+N` nuova scheda
- `Ctrl+O` apri
- `Ctrl+S` salva
- `Ctrl+Shift+S` salva con nome
- `Ctrl+W` chiudi scheda
- `Ctrl+F` trova
- `Ctrl+H` trova e sostituisci
- `Ctrl+G` vai a riga
