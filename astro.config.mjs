import { defineConfig } from 'astro/config';
import keystatic from '@keystatic/astro';
import react from '@astrojs/react';
import markdoc from '@astrojs/markdoc';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
    site: 'https://www.ks-polonia.de',
    integrations: [
        react(),
        markdoc(),
        sitemap({
            changefreq: 'weekly',
            priority: 0.7,
            lastmod: new Date(),
        }),
        process.env.NODE_ENV === 'development' ? keystatic() : null
    ].filter(Boolean),
    output: 'static'
});
