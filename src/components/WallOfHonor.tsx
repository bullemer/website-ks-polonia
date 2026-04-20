import React, { useState, useEffect, useCallback } from 'react';
import { Trophy, Star, Shield, Heart, Ticket, Award, Gem, X, CheckCircle, AlertTriangle, Users } from 'lucide-react';
import './WallOfHonor.css';

// ═══════════════════════════════════════
//  TRANSLATIONS (DE / PL)
// ═══════════════════════════════════════
const T = {
  de: {
    heroTitle: 'Wall of Honor',
    heroSubtitle: 'Werde Teil der Geschichte von KS Polonia Hamburg. Sichere deinen Platz auf unserer Ehrenwand im Vereinsheim.',
    badgeLabel: 'Vereinsheim · Finkenau',
    progressTitle: 'Sponsoring-Status',
    progressStat: (t: number, a: number) => `${t - a} von ${t} Plätzen vergeben`,
    tierNames: {
      platin: 'Legende – Platin',
      gold: 'Kapitän – Gold',
      traeger: 'Träger',
      silber: 'Freunde – Silber',
      kibice: 'Kibice',
    },
    available: 'Verfügbar',
    taken: 'Vergeben',
    reserved: 'Reserviert',
    spotAvailable: 'Noch verfügbar',
    secureSpot: 'Diesen Platz sichern',
    modalAvailableText: 'Dieser Platz wartet auf dich!',
    modalTakenText: 'Platz vergeben an:',
    benefits: 'Deine Vorteile',
    price: 'Beitrag',
    yourName: 'Dein Name auf der Wand',
    yourEmail: 'Deine E-Mail-Adresse',
    yourMessage: 'Persönliche Nachricht (optional)',
    reserveBtn: 'Jetzt reservieren',
    reserving: 'Wird reserviert...',
    successTitle: 'Reservierung erfolgreich!',
    successMsg: 'Wir melden uns in Kürze bei dir.',
    errorLoad: 'Daten konnten nicht geladen werden.',
    loading: 'Wall of Honor wird geladen...',
    perTier: (n: number) => `${n} Plätze`,
    benefitsList: {
      platin: ['Lifetime Dauerkarte', 'Name groß auf goldener Platte', 'VIP-Einladung zu allen Events', 'Ehrenplatz im Vereinsheim'],
      gold: ['Season Ticket (1 Saison)', 'Name auf goldener Platte', 'Vereinstrikot', 'Einladung zur Jahresfeier'],
      traeger: ['Name auf rundem Ehrenplatz', 'Vereinsschal', 'Erwähnung auf der Website'],
      silber: ['Name auf Silberplatte', 'Erwähnung auf der Website'],
      kibice: ['Name auf Gedenkstein', 'Ewiger Fan-Status'],
    },
  },
  pl: {
    heroTitle: 'Ściana Honoru',
    heroSubtitle: 'Zostań częścią historii KS Polonia Hamburg. Zarezerwuj swoje miejsce na naszej Ścianie Honoru w siedzibie klubu.',
    badgeLabel: 'Siedziba Klubu · Finkenau',
    progressTitle: 'Status Sponsoringu',
    progressStat: (t: number, a: number) => `${t - a} z ${t} miejsc zajętych`,
    tierNames: {
      platin: 'Legenda – Platyna',
      gold: 'Kapitan – Złoto',
      traeger: 'Filary Klubu',
      silber: 'Przyjaciele – Srebro',
      kibice: 'Kibice',
    },
    available: 'Dostępne',
    taken: 'Zajęte',
    reserved: 'Zarezerwowane',
    spotAvailable: 'Jeszcze dostępne',
    secureSpot: 'Zarezerwuj to miejsce',
    modalAvailableText: 'To miejsce czeka na Ciebie!',
    modalTakenText: 'Miejsce przyznane:',
    benefits: 'Twoje korzyści',
    price: 'Wkład',
    yourName: 'Twoje imię na ścianie',
    yourEmail: 'Twój adres e-mail',
    yourMessage: 'Wiadomość osobista (opcjonalnie)',
    reserveBtn: 'Zarezerwuj teraz',
    reserving: 'Rezerwacja...',
    successTitle: 'Rezerwacja udana!',
    successMsg: 'Skontaktujemy się wkrótce.',
    errorLoad: 'Nie udało się załadować danych.',
    loading: 'Ładowanie Ściany Honoru...',
    perTier: (n: number) => `${n} miejsc`,
    benefitsList: {
      platin: ['Dożywotni karnet', 'Imię na złotej tablicy', 'Zaproszenia VIP na wszystkie wydarzenia', 'Honorowe miejsce w siedzibie'],
      gold: ['Karnet sezonowy (1 sezon)', 'Imię na złotej tablicy', 'Koszulka klubowa', 'Zaproszenie na galę'],
      traeger: ['Imię na okrągłej tablicy', 'Szalik klubowy', 'Wzmianka na stronie'],
      silber: ['Imię na srebrnej tablicy', 'Wzmianka na stronie'],
      kibice: ['Imię na kamieniu pamiątkowym', 'Wieczny status kibica'],
    },
  },
};

type Lang = 'de' | 'pl';
type Category = 'platin' | 'gold' | 'traeger' | 'silber' | 'kibice';

interface DonorSpot {
  id: number;
  category: Category;
  position: number;
  donor_name: string | null;
  donor_message: string | null;
  status: 'available' | 'reserved' | 'taken';
}

interface WallStats {
  total: number;
  taken: number;
  available: number;
  percent: number;
}

const PRICES: Record<Category, string> = {
  platin: '5.000 €',
  gold: '2.500 €',
  traeger: '1.000 €',
  silber: '250 €',
  kibice: '50 €',
};

const TIER_ICONS: Record<Category, React.ReactNode> = {
  platin: <Gem size={18} />, 
  gold: <Trophy size={18} />,
  traeger: <Shield size={18} />,
  silber: <Star size={18} />,
  kibice: <Heart size={18} />,
};

const TIER_ORDER: Category[] = ['platin', 'gold', 'traeger', 'silber', 'kibice'];
const TIER_EMOJIS: Record<Category, string> = {
  platin: '👑',
  gold: '🏅',
  traeger: '🛡️',
  silber: '⭐',
  kibice: '❤️',
};

const API_BASE = '/api';

// ═══════════════════════════════════════
//  COMPONENT
// ═══════════════════════════════════════
export default function WallOfHonor() {
  const [lang, setLang] = useState<Lang>('de');
  const [spots, setSpots] = useState<DonorSpot[]>([]);
  const [stats, setStats] = useState<WallStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSpot, setSelectedSpot] = useState<DonorSpot | null>(null);

  // Reservation form state
  const [reserveName, setReserveName] = useState('');
  const [reserveEmail, setReserveEmail] = useState('');
  const [reserveMessage, setReserveMessage] = useState('');
  const [reserving, setReserving] = useState(false);
  const [reserveSuccess, setReserveSuccess] = useState(false);

  const t = T[lang];

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [spotsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/wall/spots`),
        fetch(`${API_BASE}/wall/stats`),
      ]);

      if (!spotsRes.ok || !statsRes.ok) throw new Error('API error');

      const spotsData = await spotsRes.json();
      const statsData = await statsRes.json();

      setSpots(spotsData.spots || []);
      setStats(statsData);
    } catch {
      setError(t.errorLoad);
      // Fallback: generate mock spots for demo/dev
      const mockSpots: DonorSpot[] = [];
      let pos = 1;
      const layout: [Category, number][] = [['platin', 2], ['gold', 2], ['traeger', 5], ['silber', 20], ['kibice', 50]];
      for (const [cat, count] of layout) {
        for (let i = 0; i < count; i++) {
          mockSpots.push({
            id: pos,
            category: cat,
            position: pos,
            donor_name: null,
            donor_message: null,
            status: 'available',
          });
          pos++;
        }
      }
      setSpots(mockSpots);
      setStats({ total: 79, taken: 0, available: 79, percent: 0 });
      setError(null); // Clear error since we have fallback data
    } finally {
      setLoading(false);
    }
  }, [t.errorLoad]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const openModal = (spot: DonorSpot) => {
    setSelectedSpot(spot);
    setReserveName('');
    setReserveEmail('');
    setReserveMessage('');
    setReserving(false);
    setReserveSuccess(false);
  };

  const closeModal = () => {
    setSelectedSpot(null);
  };

  const handleReserve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSpot || !reserveName.trim() || !reserveEmail.trim()) return;

    setReserving(true);
    try {
      const res = await fetch(`${API_BASE}/wall/reserve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          spot_id: selectedSpot.id,
          donor_name: reserveName.trim(),
          donor_message: reserveMessage.trim(),
          email: reserveEmail.trim(),
        }),
      });

      if (res.ok) {
        setReserveSuccess(true);
        // Refresh data
        setTimeout(() => fetchData(), 1500);
      } else {
        const data = await res.json();
        alert(data.error || 'Fehler bei der Reservierung.');
      }
    } catch {
      alert('Verbindungsfehler. Bitte versuche es erneut.');
    } finally {
      setReserving(false);
    }
  };

  // ── Group spots by tier ──
  const spotsByTier = TIER_ORDER.reduce((acc, tier) => {
    acc[tier] = spots.filter(s => s.category === tier);
    return acc;
  }, {} as Record<Category, DonorSpot[]>);

  // ── Render ──
  if (loading) {
    return (
      <div className="woh-container">
        <div className="woh-inner">
          <div className="woh-loading">
            <div className="woh-spinner" />
            <p>{t.loading}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="woh-container">
      <div className="woh-inner">
        {/* Language Toggle */}
        <div className="woh-lang-toggle">
          <button
            className={`woh-lang-btn ${lang === 'de' ? 'active' : ''}`}
            onClick={() => setLang('de')}
          >
            🇩🇪 DE
          </button>
          <button
            className={`woh-lang-btn ${lang === 'pl' ? 'active' : ''}`}
            onClick={() => setLang('pl')}
          >
            🇵🇱 PL
          </button>
        </div>

        {/* Hero */}
        <div className="woh-hero">
          <div className="woh-hero-badge">
            <Award size={14} />
            {t.badgeLabel}
          </div>
          <h1>{t.heroTitle}</h1>
          <p>{t.heroSubtitle}</p>
        </div>

        {/* Progress Bar */}
        {stats && (
          <div className="woh-progress-section">
            <div className="woh-progress-label">
              <span className="woh-progress-title">{t.progressTitle}</span>
              <span className="woh-progress-stat">
                {t.progressStat(stats.total, stats.available)}
              </span>
            </div>
            <div className="woh-progress-track">
              <div
                className="woh-progress-fill"
                style={{ width: `${Math.max(stats.percent, 2)}%` }}
              />
            </div>
          </div>
        )}

        {/* Tier Sections */}
        {TIER_ORDER.map(tier => (
          <div className="woh-tier" key={tier}>
            <div className="woh-tier-header">
              <span className="woh-tier-icon">{TIER_EMOJIS[tier]}</span>
              <span className="woh-tier-title">{t.tierNames[tier]}</span>
              <span className="woh-tier-subtitle">
                {t.perTier(spotsByTier[tier].length)} · {PRICES[tier]}
              </span>
            </div>
            <div className={`woh-grid-${tier}`}>
              {spotsByTier[tier].map(spot => (
                <button
                  key={spot.id}
                  className={`woh-spot woh-spot-${tier} ${spot.status !== 'available' ? 'taken' : ''}`}
                  onClick={() => openModal(spot)}
                  title={spot.donor_name || t.spotAvailable}
                >
                  <span className={`woh-spot-name ${spot.status === 'available' ? 'woh-spot-available' : ''}`}>
                    {spot.donor_name || t.spotAvailable}
                  </span>
                  {spot.status === 'available' && (
                    <span className="woh-spot-label">{PRICES[tier]}</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        ))}

        {/* Modal */}
        {selectedSpot && (
          <div className="woh-modal-overlay" onClick={(e) => {
            if (e.target === e.currentTarget) closeModal();
          }}>
            <div className="woh-modal">
              <button className="woh-modal-close" onClick={closeModal}>
                <X size={16} />
              </button>

              {/* Tier Badge */}
              <div className={`woh-modal-tier-badge ${selectedSpot.category}`}>
                {TIER_ICONS[selectedSpot.category]}
                {t.tierNames[selectedSpot.category]}
              </div>

              {reserveSuccess ? (
                /* ── Success State ── */
                <div className="woh-success-msg">
                  <CheckCircle className="check-icon" size={48} />
                  <h3>{t.successTitle}</h3>
                  <p>{t.successMsg}</p>
                </div>
              ) : selectedSpot.status === 'available' ? (
                /* ── Available Spot — Show Reserve Form ── */
                <>
                  <h2>{t.secureSpot}</h2>
                  <p className="woh-modal-status available">✓ {t.modalAvailableText}</p>

                  {/* Benefits */}
                  <ul className="woh-benefits">
                    {t.benefitsList[selectedSpot.category].map((b, i) => (
                      <li key={i} className="woh-benefit-item">
                        {i === 0 && selectedSpot.category === 'platin' ? (
                          <Ticket size={20} className="woh-benefit-icon" />
                        ) : (
                          <Star size={20} className="woh-benefit-icon" />
                        )}
                        {b}
                      </li>
                    ))}
                  </ul>

                  <div className="woh-modal-price">
                    {PRICES[selectedSpot.category]}
                    <br />
                    <span>{t.price}</span>
                  </div>

                  <form className="woh-reserve-form" onSubmit={handleReserve}>
                    <input
                      type="text"
                      className="woh-input"
                      placeholder={t.yourName}
                      value={reserveName}
                      onChange={(e) => setReserveName(e.target.value)}
                      required
                    />
                    <input
                      type="email"
                      className="woh-input"
                      placeholder={t.yourEmail}
                      value={reserveEmail}
                      onChange={(e) => setReserveEmail(e.target.value)}
                      required
                    />
                    <input
                      type="text"
                      className="woh-input"
                      placeholder={t.yourMessage}
                      value={reserveMessage}
                      onChange={(e) => setReserveMessage(e.target.value)}
                    />
                    <button
                      type="submit"
                      className="woh-cta-btn"
                      disabled={reserving || !reserveName.trim() || !reserveEmail.trim()}
                    >
                      {reserving ? t.reserving : t.reserveBtn}
                    </button>
                  </form>
                </>
              ) : (
                /* ── Taken / Reserved Spot ── */
                <>
                  <h2>{selectedSpot.donor_name}</h2>
                  <p className={`woh-modal-status ${selectedSpot.status}`}>
                    {selectedSpot.status === 'taken' ? `🏆 ${t.taken}` : `⏳ ${t.reserved}`}
                  </p>

                  {selectedSpot.donor_message && (
                    <div className="woh-modal-donor-msg">
                      „{selectedSpot.donor_message}"
                    </div>
                  )}

                  {/* Benefits for this tier */}
                  <ul className="woh-benefits">
                    {t.benefitsList[selectedSpot.category].map((b, i) => (
                      <li key={i} className="woh-benefit-item">
                        <Star size={20} className="woh-benefit-icon" />
                        {b}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
