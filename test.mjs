console.log("Running test");
import fs from 'fs/promises';
fs.readFile('../kspoloniahamburgev1988.WordPress.2026-03-15.xml', 'utf-8')
  .then(d => console.log("Read " + d.length + " bytes"))
  .catch(console.error);
