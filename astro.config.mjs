import { defineConfig } from 'astro/config';
import keystatic from '@keystatic/astro';
import react from '@astrojs/react';
import markdoc from '@astrojs/markdoc';

// https://astro.build/config
export default defineConfig({
    integrations: [
        react(),
        markdoc(),
        process.env.NODE_ENV === 'development' ? keystatic() : null
    ].filter(Boolean),
    output: 'static'
});
