console.log("Starting script");
import fs from 'fs/promises';
import { parseStringPromise } from 'xml2js';
console.log("Imports done");
fs.readFile('../kspoloniahamburgev1988.WordPress.2026-03-15.xml', 'utf-8').then(async xml => {
  console.log("File read");
  console.log("Parsing XML...");
  const result = await parseStringPromise(xml);
  console.log("JSON parsed. channels: ", result.rss.channel.length);
}).catch(console.error);
