#!/usr/bin/env node
/**
 * KS Polonia Hamburg — WordPress → Astro Migration Script
 *
 * Reads the WordPress WXR export XML and produces:
 *   • src/content/news/{slug}/index.md   — for every published <post>
 *   • src/content/pages/{slug}/index.md  — for every published <page>
 *   • src/assets/images/{filename}       — downloaded attachments
 *
 * Usage:
 *   node migrate.mjs                         # default XML path
 *   node migrate.mjs --dry-run               # preview without writing
 *
 * Requirements:  npm install xml2js turndown
 */

import fs from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import { parseStringPromise } from 'xml2js';
import TurndownService from 'turndown';

// ─── Configuration ──────────────────────────────────────────────────────────────
const DEFAULT_XML = '../kspoloniahamburgev1988.WordPress.2026-03-15.xml';
const CONTENT_DIR = './src/content';
const IMAGES_DIR = './src/assets/images';

const CATEGORY_MAP = {
    allgemein: 'Allgemein',
    kinder: 'Kinder',
    merchandising: 'Merchandising',
};

const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const XML_PATH = args.find(a => !a.startsWith('--')) || DEFAULT_XML;

// ─── Turndown (HTML → Markdown) ─────────────────────────────────────────────────
const turndown = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    bulletListMarker: '-',
});

// Strip WordPress shortcodes that can't be rendered
turndown.addRule('wpShortcodes', {
    filter: (node) => node.nodeType === 3 && /\[.*?\]/.test(node.textContent),
    replacement: (content) => content.replace(/\[.*?\]/g, ''),
});

// ─── Slug / filename helpers ────────────────────────────────────────────────────
function sanitizeSlug(raw) {
    return decodeURIComponent(raw)
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9àáâãäåąæçćèéêëęìíîïłñńòóôõöøùúûüśźżß\-]/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
}

function sanitizeFilename(raw) {
    return decodeURIComponent(raw)
        .replace(/[^a-zA-Z0-9àáâãäåąæçćèéêëęìíîïłñńòóôõöøùúûüśźżß.\-_]/g, '_');
}

/**
 * Strip WordPress resize suffix from a filename.
 * "image-768x512.jpg" → "image.jpg",  "photo-300x200.png" → "photo.png"
 */
function stripResizeSuffix(filename) {
    return filename.replace(/-\d+x\d+(\.\w+)$/, '$1');
}

// ─── Image downloading ──────────────────────────────────────────────────────────
async function downloadImage(urlStr, savePath) {
    if (existsSync(savePath)) return true;
    if (DRY_RUN) {
        console.log(`  [dry-run] Would download → ${path.basename(savePath)}`);
        return true;
    }

    try {
        let fetchUrl = urlStr;
        const fetchOpts = {};

        if (urlStr.includes('@')) {
            const u = new URL(urlStr);
            if (u.username) {
                fetchOpts.headers = {
                    Authorization: `Basic ${Buffer.from(`${u.username}:${u.password}`).toString('base64')}`,
                };
                u.username = '';
                u.password = '';
                fetchUrl = u.toString();
            }
        }

        const res = await fetch(fetchUrl, fetchOpts);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const buf = Buffer.from(await res.arrayBuffer());
        await fs.writeFile(savePath, buf);
        return true;
    } catch (err) {
        console.error(`  ✗ Failed: ${path.basename(savePath)} — ${err.message}`);
        return false;
    }
}

// ─── Frontmatter builder ────────────────────────────────────────────────────────
function buildFrontmatter(fields) {
    let fm = '---\n';
    for (const [key, val] of Object.entries(fields)) {
        if (val === null || val === undefined) continue;
        if (typeof val === 'string') {
            fm += `${key}: "${val.replace(/"/g, '\\"')}"\n`;
        } else {
            fm += `${key}: ${val}\n`;
        }
    }
    fm += '---\n\n';
    return fm;
}

// ─── WordPress URL → Local path replacement ─────────────────────────────────────
/**
 * Replace ALL WordPress upload URLs in the content with local image paths.
 * Handles resized variants (e.g., image-768x512.jpg → image.jpg)
 * Also downloads any inline images not in the attachment list.
 */
async function replaceWpImageUrls(html, attachmentsByFilename) {
    // Match all WP upload URLs (with or without auth credentials)
    const wpUrlRegex = /https?:\/\/[^"'\s]*?www\.ks-polonia\.de\/wp-content\/uploads\/[^"'\s)]+/gi;
    const matches = [...new Set(html.match(wpUrlRegex) || [])];

    let inlineDownloaded = 0;
    for (const fullUrl of matches) {
        try {
            const u = new URL(fullUrl);
            const rawFilename = decodeURIComponent(path.basename(u.pathname));
            const sanitized = sanitizeFilename(rawFilename);
            const stripped = stripResizeSuffix(sanitized);

            // Try to find a matching local file:
            // 1. Exact match in attachments
            // 2. Stripped (without resize suffix) match
            // 3. Download the file directly
            let localFilename = null;

            if (attachmentsByFilename.has(sanitized)) {
                localFilename = sanitized;
            } else if (attachmentsByFilename.has(stripped)) {
                localFilename = stripped;
            } else {
                // Not in attachments — download the resized variant directly
                const dest = path.join(IMAGES_DIR, sanitized);
                const ok = await downloadImage(fullUrl, dest);
                if (ok) {
                    localFilename = sanitized;
                    inlineDownloaded++;
                }
            }

            if (localFilename) {
                // Escape the URL for regex replacement (dot, slashes, etc.)
                const escaped = fullUrl.replace(/[-[\]{}()*+?.\\^$|]/g, '\\$&');
                html = html.replace(new RegExp(escaped, 'g'), `../../../assets/images/${localFilename}`);
            }
        } catch { /* skip malformed URLs */ }
    }

    if (inlineDownloaded > 0) {
        console.log(`    ↳ Downloaded ${inlineDownloaded} additional inline images`);
    }

    return html;
}

// ─── Main ───────────────────────────────────────────────────────────────────────
async function migrate() {
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║  KS Polonia — WordPress → Astro Migration              ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    if (DRY_RUN) console.log('  ⚠  DRY RUN — no files will be written\n');

    // ── 1. Parse XML ────────────────────────────────────────────────────────────
    console.log(`Reading XML: ${XML_PATH}`);
    const xmlContent = await fs.readFile(XML_PATH, 'utf-8');
    const result = await parseStringPromise(xmlContent, {
        explicitCDATA: false,
        normalizeTags: false,
        trim: true,
    });

    const channel = result.rss.channel[0];
    const items = channel.item || [];
    console.log(`Found ${items.length} total items in XML\n`);

    // ── 2. Index attachments ────────────────────────────────────────────────────
    const attachments = new Map();       // postId → { url, filename }
    const attachmentsByFilename = new Map();  // filename → true

    for (const item of items) {
        if (item['wp:post_type']?.[0] !== 'attachment') continue;
        const rawUrl = item['wp:attachment_url']?.[0];
        if (!rawUrl) continue;

        const url = rawUrl.replace(/<!\[CDATA\[|\]\]>/g, '');
        const postId = item['wp:post_id']?.[0];
        const filename = sanitizeFilename(path.basename(new URL(url).pathname));
        attachments.set(postId, { url, filename });
        attachmentsByFilename.set(filename, true);
    }

    console.log(`📎 ${attachments.size} attachments indexed`);

    // ── 3. Download images ──────────────────────────────────────────────────────
    if (!DRY_RUN) await fs.mkdir(IMAGES_DIR, { recursive: true });

    let downloaded = 0, skipped = 0, failed = 0;
    for (const [id, att] of attachments) {
        const dest = path.join(IMAGES_DIR, att.filename);
        if (existsSync(dest)) { skipped++; continue; }
        const ok = await downloadImage(att.url, dest);
        ok ? downloaded++ : failed++;
    }
    console.log(`   ↳ Downloaded: ${downloaded}  Skipped (exist): ${skipped}  Failed: ${failed}\n`);

    // ── 4. Process posts & pages ────────────────────────────────────────────────
    const stats = { news: 0, pages: 0, drafts: 0, inlineImgs: 0 };

    for (const item of items) {
        const postType = item['wp:post_type']?.[0];
        if (postType !== 'post' && postType !== 'page') continue;

        const status = item['wp:status']?.[0];
        if (status !== 'publish') { stats.drafts++; continue; }

        // ─ Title ──────────────────────────────────────────────────────────────────
        let title = item.title?.[0];
        if (typeof title === 'object' && title._) title = title._;
        if (!title || title === '') title = 'Untitled';
        title = String(title).trim();

        // ─ Slug ───────────────────────────────────────────────────────────────────
        const rawSlug = item['wp:post_name']?.[0];
        let slug = rawSlug ? sanitizeSlug(rawSlug) : sanitizeSlug(title);
        if (!slug) slug = `post-${item['wp:post_id']?.[0] || 'unknown'}`;

        // ─ Date ───────────────────────────────────────────────────────────────────
        let dateStr = null;
        const rawDate = item['wp:post_date']?.[0];
        if (rawDate && rawDate !== '0000-00-00 00:00:00') {
            const d = new Date(rawDate);
            if (!isNaN(d.getTime())) dateStr = d.toISOString();
        }

        // ─ Category (posts only) ──────────────────────────────────────────────────
        let category = 'Allgemein';
        if (postType === 'post') {
            const cats = (item.category || [])
                .filter(c => c?.$ && c.$.domain === 'category')
                .map(c => (c._ || c.$.nicename || '').toLowerCase());
            for (const [key, label] of Object.entries(CATEGORY_MAP)) {
                if (cats.includes(key)) { category = label; break; }
            }
        }

        // ─ Cover Image ────────────────────────────────────────────────────────────
        let coverImage = null;
        const thumbMeta = (item['wp:postmeta'] || [])
            .find(m => m['wp:meta_key']?.[0] === '_thumbnail_id');
        if (thumbMeta?.['wp:meta_value']?.[0]) {
            const att = attachments.get(thumbMeta['wp:meta_value'][0]);
            if (att) coverImage = `../../../assets/images/${att.filename}`;
        }

        // ─ Content: HTML → replace images → Markdown ──────────────────────────────
        let html = item['content:encoded']?.[0] || '';
        if (typeof html === 'object' && html._) html = html._;
        html = String(html).replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1');

        // Strip WordPress shortcodes (contact forms, galleries, etc.)
        html = html.replace(/\[contact-form-7[^\]]*\]/g, '');
        html = html.replace(/\[gallery[^\]]*\]/g, '');
        html = html.replace(/\[vc_[^\]]*\]/g, '');
        html = html.replace(/\[\/vc_[^\]]*\]/g, '');

        // Replace ALL WordPress upload URLs with local paths
        html = await replaceWpImageUrls(html, attachmentsByFilename);

        const markdown = html ? turndown.turndown(html) : '';

        // ─ Build output ───────────────────────────────────────────────────────────
        const dirType = postType === 'post' ? 'news' : 'pages';
        const outputDir = path.join(CONTENT_DIR, dirType, slug);

        const frontmatterFields = { title };
        if (postType === 'post') {
            if (dateStr) frontmatterFields.date = dateStr;
            frontmatterFields.category = category;
            if (coverImage) frontmatterFields.coverImage = coverImage;
        }

        const fileContent = buildFrontmatter(frontmatterFields) + markdown + '\n';

        if (DRY_RUN) {
            console.log(`  [dry-run] ${dirType}/${slug}/index.md  (${title})`);
        } else {
            await fs.mkdir(outputDir, { recursive: true });
            await fs.writeFile(path.join(outputDir, 'index.md'), fileContent, 'utf-8');
        }

        stats[dirType === 'news' ? 'news' : 'pages']++;
    }

    // ── 5. Summary ──────────────────────────────────────────────────────────────
    console.log('\n─── Migration Summary ────────────────────────────────────');
    console.log(`  📰 News posts:    ${stats.news}`);
    console.log(`  📄 Static pages:  ${stats.pages}`);
    console.log(`  🚫 Drafts skipped: ${stats.drafts}`);
    console.log(`  🖼  Images:        ${attachments.size} (${downloaded} new, ${skipped} existing, ${failed} failed)`);
    console.log('──────────────────────────────────────────────────────────\n');
    console.log('✅ Migration complete!');
}

migrate().catch(err => {
    console.error('\n❌ Migration failed:', err);
    process.exit(1);
});
