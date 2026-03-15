import { getCollection } from 'astro:content';
const teams = await getCollection('teams');
console.log(teams.map(t => t.id));
