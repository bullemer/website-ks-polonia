/**
 * API fetching functions for KS Polonia
 */

export interface LiveScore {
    id: string;
    homeTeam: string;
    awayTeam: string;
    homeScore: number | null;
    awayScore: number | null;
    status: 'SCHEDULED' | 'IN_PLAY' | 'FINISHED' | 'POSTPONED';
    minute?: number;
    league: string;
}

/**
 * Fetches current live scores or recent matches from Polish leagues (e.g. Ekstraklasa).
 * This will eventually pull from an external API or a local JSON file.
 */
export async function fetchPolishLeagues(): Promise<LiveScore[]> {
    // TODO: Replace with actual external API integration or local JSON parsing
    // const response = await fetch('https://api.example.com/polish-leagues/live');
    // const data = await response.json();
    // return data;

    // Returning mock data for now to demonstrate component rendering
    return [
        {
            id: "match-1",
            homeTeam: "Legia Warszawa",
            awayTeam: "Lech Poznań",
            homeScore: 1,
            awayScore: 0,
            status: "IN_PLAY",
            minute: 45,
            league: "Ekstraklasa"
        },
        {
            id: "match-2",
            homeTeam: "Raków Częstochowa",
            awayTeam: "Pogoń Szczecin",
            homeScore: null,
            awayScore: null,
            status: "SCHEDULED",
            league: "Ekstraklasa"
        },
        {
            id: "match-3",
            homeTeam: "Cracovia",
            awayTeam: "Wisła Kraków",
            homeScore: 2,
            awayScore: 2,
            status: "FINISHED",
            league: "I liga"
        }
    ];
}
