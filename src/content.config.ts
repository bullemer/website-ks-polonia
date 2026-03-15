import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const news = defineCollection({
    loader: glob({ pattern: '**/*.{md,mdoc}', base: './src/content/news' }),
    schema: ({ image }) => z.object({
        title: z.string(),
        date: z.coerce.date().optional(),
        category: z.enum(['Allgemein', 'Kinder', 'Merchandising']).default('Allgemein'),
        summary: z.string().optional(),
        coverImage: image().optional(),
        teamLink: z.string().optional(),
    }),
});

const teams = defineCollection({
    loader: glob({ pattern: '**/*.{md,mdoc}', base: './src/content/teams' }),
    schema: z.object({
        title: z.string().optional(),
        externalUrl: z.string().optional(),
        sport: z.string().optional(),
        spielklasse: z.string().optional(),
        wettbewerb: z.string().optional(),
        logoUrl: z.string().optional(),
        ageGroup: z.string().optional(),
        coach: z.string().optional(),
        trainingTimes: z.string().optional(),
        roster: z.array(
            z.object({
                name: z.string(),
                position: z.string().optional(),
                number: z.number().optional(),
            })
        ).optional(),
    }),
});

const pages = defineCollection({
    loader: glob({ pattern: '**/*.{md,mdoc}', base: './src/content/pages' }),
    schema: z.object({
        title: z.string(),
    }),
});

export const collections = {
    news,
    teams,
    pages,
};
