import { defineConfig } from 'astro/config';
import keystatic from '@keystatic/astro';
import react from '@astrojs/react';
import markdoc from '@astrojs/markdoc';
import sitemap from '@astrojs/sitemap';

// =============================================
// SEO: Pages to exclude from sitemap
// These are WordPress migration remnants, empty
// Elementor pages, WooCommerce leftovers, duplicates,
// and internal utility pages.
// =============================================
const SITEMAP_EXCLUDE_PATTERNS = [
    // Empty Elementor artifacts (pages + news)
    '/seiten/elementor-',
    '/news/elementor-',
    // WooCommerce remnants (no shop on this site)
    '/seiten/kasse/',
    '/seiten/warenkorb/',
    '/seiten/mein-konto/',
    '/seiten/shop/',
    '/seiten/rueckerstattung-rueckgaben/',
    // Disabled / broken features
    '/seiten/online-antrag-2/',
    // Duplicate content (real versions exist elsewhere)
    '/seiten/home/',          // duplicate of /
    '/seiten/galerie/',       // duplicate of /galerie
    '/seiten/impressum/',     // duplicate of /seiten/impressum-2/
    '/seiten/kontaktformular/', // duplicate of /kontakt
    // Thin / low-value migrated pages
    '/seiten/sachspende/',
    '/seiten/beitraege/',
    // Empty / junk news articles
    '/news/untitled/',
    '/news/847/',
    // Internal utility pages
    '/status/',
    // Duplicate football team pages (shorter slug duplicates of full-name versions)
    '/football/polonia-1-/',
    '/football/polonia-2-/',
    '/football/polonia-3-/',
    '/football/polonia-4-/',
    '/football/polonia-1--40/',
    '/football/polonia-1-c--a1-/',
    '/football/polonia-1-e--j1-/',
    '/football/polonia-2-c--j1-/',
];

// https://astro.build/config
export default defineConfig({
    site: 'https://www.ks-polonia.de',
    integrations: [
        react(),
        markdoc(),
        sitemap({
            changefreq: 'weekly',
            lastmod: new Date(),
            filter: (page) => {
                return !SITEMAP_EXCLUDE_PATTERNS.some(pattern => page.includes(pattern));
            },
            serialize: (item) => {
                const url = item.url;
                // Homepage gets highest priority
                if (url === 'https://www.ks-polonia.de/' || url === 'https://www.ks-polonia.de') {
                    return { ...item, priority: 1.0, changefreq: 'daily' };
                }
                // Key action pages — high priority
                if (url.includes('/trainingszeiten') || url.includes('/spieltermine') ||
                    url.includes('/mitgliedsantrag') || url.includes('/probetraining')) {
                    return { ...item, priority: 0.9, changefreq: 'weekly' };
                }
                // Sport-specific landing pages
                if (url.includes('/basketball-') || url.includes('/badminton')) {
                    return { ...item, priority: 0.8, changefreq: 'weekly' };
                }
                // News index
                if (url.endsWith('/news/') || url.endsWith('/news')) {
                    return { ...item, priority: 0.8, changefreq: 'daily' };
                }
                // Individual news articles
                if (url.includes('/news/')) {
                    return { ...item, priority: 0.6, changefreq: 'monthly' };
                }
                // Football team pages
                if (url.includes('/football/')) {
                    return { ...item, priority: 0.5, changefreq: 'weekly' };
                }
                // Paginated list pages (aktuelles/2, /3, etc.)
                if (/\/seiten\/aktuelles\/\d+/.test(url)) {
                    return { ...item, priority: 0.3, changefreq: 'weekly' };
                }
                // Everything else
                return { ...item, priority: 0.7 };
            },
        }),
        process.env.NODE_ENV === 'development' ? keystatic() : null
    ].filter(Boolean),
    output: 'static'
});
