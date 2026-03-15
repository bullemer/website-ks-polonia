const spawn = require('child_process').spawn;
const astro = spawn('./node_modules/.bin/astro', ['dev', '--host'], { stdio: 'inherit' });
astro.on('close', code => console.log('Astro closed', code));
astro.on('error', err => console.error('Astro error', err));
