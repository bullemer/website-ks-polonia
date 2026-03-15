import { config, collection, singleton, fields } from '@keystatic/core';

export default config({
  storage: {
    kind: 'local',
  },
  collections: {
    news: collection({
      label: 'News',
      slugField: 'title',
      path: 'src/content/news/*/',
      format: { contentField: 'content' },
      schema: {
        title: fields.slug({ name: { label: 'Title' } }),
        date: fields.datetime({
          label: 'Date',
          validation: { isRequired: false },
        }),
        category: fields.select({
          label: 'Category',
          options: [
            { label: 'Allgemein', value: 'Allgemein' },
            { label: 'Kinder', value: 'Kinder' },
            { label: 'Merchandising', value: 'Merchandising' },
          ],
          defaultValue: 'Allgemein',
        }),
        summary: fields.text({ label: 'Summary', multiline: true }),
        coverImage: fields.image({
          label: 'Cover Image',
          directory: 'src/assets/images',
          publicPath: '../../../assets/images/',
        }),
        teamLink: fields.relationship({
          label: 'Related Team',
          collection: 'teams',
        }),
        content: fields.markdoc({ label: 'Content' }),
      },
    }),
    teams: collection({
      label: 'Teams',
      slugField: 'title',
      path: 'src/content/teams/*',
      format: { contentField: 'content' },
      schema: {
        title: fields.slug({ name: { label: 'Team Title' } }),
        externalUrl: fields.url({ label: 'Fussball.de URL' }),
        sport: fields.text({ label: 'Sport', defaultValue: 'Football' }),
        spielklasse: fields.text({ label: 'Spielklasse' }),
        wettbewerb: fields.text({ label: 'Wettbewerb' }),
        logoUrl: fields.text({ label: 'Logo Image Path' }),
        ageGroup: fields.text({ label: 'Age Group' }),
        coach: fields.text({ label: 'Coach' }),
        trainingTimes: fields.text({ label: 'Training Times', multiline: true }),
        roster: fields.array(
          fields.object({
            name: fields.text({ label: 'Name', validation: { isRequired: true } }),
            position: fields.text({ label: 'Position' }),
            number: fields.integer({ label: 'Jersey Number' }),
          }),
          {
            label: 'Roster',
            itemLabel: (props) => props.fields.name.value || 'New Player',
          }
        ),
        content: fields.markdoc({ label: 'Content' }),
      },
    }),
    pages: collection({
      label: 'Pages',
      slugField: 'title',
      path: 'src/content/pages/*/',
      format: { contentField: 'content' },
      schema: {
        title: fields.slug({ name: { label: 'Title' } }),
        content: fields.markdoc({ label: 'Content' }),
      },
    }),
  },
  singletons: {
    startpage: singleton({
      label: 'Startseite',
      path: 'src/content/startpage/index',
      format: { data: 'json' },
      schema: {
        heroTitle: fields.text({ label: 'Hero Title', defaultValue: 'KS Polonia Hamburg' }),
        heroSubtitle: fields.text({ label: 'Hero Subtitle', defaultValue: 'Polnischer Sportverein in Hamburg · seit 1988' }),
      },
    }),
  },
});
