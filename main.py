from src.scraping.scraper import TransfermarktScraper
from src.processing.processing import scrape_and_save_teams, scrape_and_save_players
import config


def main():
    print("Inizio il processo di scraping.")

    # Inizializza lo scraper
    scraper = TransfermarktScraper()

    # Scraping delle squadre e dei giocatori sequenzialmente
    for campionato in config.campionati.values():
        for stagione in config.stagioni:
            print(f"Scraping per {campionato['nome']} stagione {stagione}...")
            # Scraping delle squadre del campionato
            squadre_df = scrape_and_save_teams(scraper, campionato, stagione)

            if squadre_df.empty:
                print(f"Nessuna squadra trovata per {campionato['nome']} stagione {stagione}.")
                continue

            # Scraping dei giocatori e dei loro dettagli per tutte le squadre
            for _, team in squadre_df.iterrows():
                scrape_and_save_players(scraper, team, campionato["nome"], stagione)

    print("Scraping completato per tutti i campionati e tutte le squadre.")

if __name__ == "__main__":
    main()
