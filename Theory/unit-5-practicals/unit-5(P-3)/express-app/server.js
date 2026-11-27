'use strict';
const { createApp } = require('./app');
const port = Number(process.env.PORT || 3000);
createApp().listen(port, () => console.log(`SMS API with profiling on http://localhost:${port}  (try /api/ping and /metrics)`));
