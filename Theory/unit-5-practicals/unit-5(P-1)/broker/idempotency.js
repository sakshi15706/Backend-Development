'use strict';
const fs = require('fs');

/** In-memory set of processed eventIds. Lost on restart: fine for a demo, not for production. */
class MemoryStore {
  constructor() { this.ids = new Set(); }
  async has(id) { return this.ids.has(id); }
  async add(id) { this.ids.add(id); }
}

/**
 * Survives restarts: one eventId per line in a file. Still a teaching stand-in; in production
 * use a database table with a UNIQUE key on eventId (ideally written in the same transaction
 * as the side effect) or DynamoDB with attribute_not_exists (see unit-5(P-2)).
 */
class FileStore {
  constructor(filePath) {
    this.filePath = filePath;
    this.ids = new Set(fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8').split('\n').filter(Boolean) : []);
  }
  async has(id) { return this.ids.has(id); }
  async add(id) {
    if (this.ids.has(id)) return;
    fs.appendFileSync(this.filePath, id + '\n');
    this.ids.add(id);
  }
}

module.exports = { MemoryStore, FileStore };
