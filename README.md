# ⚽ KS Polonia Hamburg e.V. 1988

Official website of **K.S. Polonia Hamburg e.V. 1988** — a Polish sports club in Hamburg-Uhlenhorst offering football, basketball, and badminton.

**Live:** [www.ks-polonia.de](https://www.ks-polonia.de)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Astro 5](https://astro.build/) (static output) |
| CMS | [Keystatic](https://keystatic.com/) (local-first, dev-only) |
| Content | [Markdoc](https://markdoc.dev/) via `@astrojs/markdoc` |
| UI | [Inter](https://fonts.google.com/specimen/Inter) font, vanilla CSS |
| Integrations | React 18 (for Keystatic UI) |
| Hosting | Hetzner Webspace (FTP) |
| CI/CD | GitHub Actions → build → FTP deploy |

---

## Getting Started

### Prerequisites

- **Node.js 20+** (recommend using [nvm](https://github.com/nvm-sh/nvm))
- **npm**

### Installation

```bash
cd website
npm install
```

### Development

```bash
npm run dev
```

The dev server starts at **http://localhost:4321** with network access (`--host`).

Keystatic CMS is available in development at: **http://localhost:4321/keystatic**

### Build & Preview

```bash
npm run build      # Build static site to ./dist/
npm run preview    # Preview the production build locally
```

---

## Project Structure

```
website/
├── public/
│   ├── api/                  # Server-side PHP (contact form backend)
│   ├── downloads/            # PDF files for download page
│   ├── images/               # Public static images
│   ├── favicon.svg
│   ├── favicon.ico
│   └── logo.png
├── src/
│   ├── assets/
│   │   └── images/
│   │       └── galerie/      # Gallery photos (mannschaften, events, verein, jugend, sportplatz)
│   ├── components/
│   │   └── LiveScores.astro  # Polish league live scores widget
│   ├── content/
│   │   ├── news/             # News articles (Markdoc)
│   │   ├── teams/            # Football team pages (Markdoc)
│   │   ├── pages/            # Generic CMS pages (Markdoc)
│   │   └── startpage/        # Homepage singleton (JSON)
│   ├── layouts/
│   │   └── Layout.astro      # Main layout (header, nav, footer, global styles)
│   ├── lib/
│   │   └── api.ts            # API functions (LiveScores data fetching)
│   ├── pages/
│   │   ├── index.astro       # Homepage
│   │   ├── kontakt.astro     # Contact form
│   │   ├── galerie.astro     # Photo gallery with lightbox
│   │   ├── spieltermine.astro# Match schedule (fussball.de widget)
│   │   ├── downloads.astro   # Document downloads
│   │   ├── news/             # News listing & detail ([slug].astro)
│   │   ├── football/         # Team detail pages ([team].astro)
│   │   └── seiten/           # Generic pages & probetraining form
│   └── content.config.ts     # Astro content collection schemas (Zod)
├── keystatic.config.ts       # Keystatic CMS configuration
├── astro.config.mjs          # Astro configuration
├── migrate.mjs               # WordPress → Markdoc migration script
├── extract-menu.mjs          # WordPress menu structure extractor
└── package.json
```

---

## Content Management

Content is managed through **Keystatic** (dev mode) or by editing Markdoc files directly.

### Collections

| Collection | Path | Description |
|---|---|---|
| **News** | `src/content/news/*/` | News articles with title, date, category, summary, cover image |
| **Teams** | `src/content/teams/` | Football teams with metadata, roster, fussball.de link |
| **Pages** | `src/content/pages/*/` | Generic content pages (Satzung, Datenschutz, etc.) |

### Singleton

| Singleton | Path | Description |
|---|---|---|
| **Startseite** | `src/content/startpage/index.json` | Homepage hero title & subtitle |

### Adding Content via Keystatic

1. Start the dev server: `npm run dev`
2. Open **http://localhost:4321/keystatic**
3. Create or edit entries in the CMS UI
4. Content is saved as local files — commit and push to deploy

### Adding Gallery Photos

Drop images into the appropriate subfolder:

```
src/assets/images/galerie/
├── mannschaften/   # Team photos
├── events/         # Event photos
├── verein/         # Club photos
├── jugend/         # Youth photos
└── sportplatz/     # Venue photos
```

Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`

---

## Key Features

### Navigation
The main navigation is dynamically generated from the teams content collection. Teams are split into **Herren** (senior/Ü40/Ü50) and **Jugend** (C/D/E-Junioren) sub-menus, de-duplicated by their fussball.de URL.

### Fussball.de Integration
Match widgets from [fussball.de](https://www.fussball.de) are embedded on the homepage and Spieltermine page, showing live club match data.

### Contact Forms
Two contact forms send POST requests to `/api/contact.php`:
- **Kontaktformular** (`/kontakt`) — General, Probetraining, Sponsoring subjects
- **Probetraining** (`/seiten/probetraining`) — Pre-filled subject, includes age/birth year field

Both forms include honeypot spam protection.

### SEO
- Page titles with `| KS Polonia Hamburg` suffix
- Meta descriptions (default + per-page overrides)
- Open Graph & Twitter Card meta tags
- Canonical URLs pointing to `https://www.ks-polonia.de`

---

## Deployment

Deployment is fully automated via **GitHub Actions** on push to `main`:

1. Checks out the code
2. Sets up Node.js 20
3. Runs `npm ci` and `npm run build`
4. Deploys `./dist/` via FTPS to Hetzner Webspace at `/public_html/ks-polonia/`

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `FTP_SERVER` | Hetzner FTP server hostname |
| `FTP_USERNAME` | FTP username |
| `FTP_PASSWORD` | FTP password |

### Manual Deployment

```bash
npm run build
# Upload ./dist/ contents to /public_html/ks-polonia/ on your Hetzner webspace
```

---

## Migration from WordPress

The site was migrated from WordPress using custom scripts:

| Script | Purpose |
|---|---|
| `migrate.mjs` | Converts WordPress XML export → Markdoc content collections |
| `extract-menu.mjs` | Extracts navigation menu structure from WP export |
| `scripts/scrape-teams.js` | Scrapes team data from fussball.de |

The WordPress export file is stored at the project root: `kspoloniahamburgev1988.WordPress.2026-03-15.xml`

---

## Commands Reference

| Command | Action |
|---|---|
| `npm install` | Install dependencies |
| `npm run dev` | Start dev server at `localhost:4321` |
| `npm run build` | Build production site to `./dist/` |
| `npm run preview` | Preview production build locally |
| `npm run astro ...` | Run Astro CLI commands |

---

## Environment Variables

| Variable | Description |
|---|---|
| `VITE_KEYSTATIC_GITHUB_CLIENT_ID` | Keystatic GitHub OAuth client ID (for GitHub storage mode) |

Create a `.env` file in the `website/` directory:

```env
VITE_KEYSTATIC_GITHUB_CLIENT_ID=your_client_id_here
```

---

## License

Private — K.S. Polonia Hamburg e.V. 1988
