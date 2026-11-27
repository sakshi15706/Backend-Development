'use strict';
// The slide's discover.js: node registry/discover.js
const { discoverHealthy } = require('./consul-client');

discoverHealthy('attendance')
  .then((instances) => console.log('healthy attendance instances:', instances.map((i) => `${i.address}:${i.port}`)))
  .catch((e) => { console.error(e.message); process.exit(1); });
