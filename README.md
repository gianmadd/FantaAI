# FantaAI

**FantaAI** è un sistema di raccomandazione basato sull’intelligenza artificiale per ottimizzare la formazione al fantacalcio della Serie A. Analizza le statistiche dei giocatori, la forma attuale, le condizioni fisiche, e gli avversari per suggerire la formazione ideale per ciascuna giornata di campionato.

## Funzionalità Principali

- **Raccolta Dati**: Recupera dati aggiornati sulle prestazioni dei giocatori tramite API, inclusi gol, assist, medie voto, ecc.
- **Analisi e Predizione**: Utilizza algoritmi di machine learning per prevedere le prestazioni dei giocatori.
- **Ottimizzazione della Formazione**: Calcola la formazione ottimale basata sul punteggio stimato, rispettando le regole del fantacalcio.

## Struttura del Progetto

- `config/`: File di configurazione, incluse le credenziali API (`.env`).
- `data/`: Contiene i dati grezzi e processati.
- `notebooks/`: Jupyter Notebooks per analisi esplorative e visualizzazioni.
- `src/`: Codice sorgente del progetto, suddiviso in sotto-moduli:
  - `data_preparation/`: Script per la pulizia e il preprocessamento dei dati.
  - `models/`: Definizione e addestramento dei modelli di machine learning.
  - `optimization/`: Algoritmi per ottimizzare la formazione.
  - `utils/`: Funzioni e helper.
- `tests/`: Test automatici per garantire il corretto funzionamento del codice.

