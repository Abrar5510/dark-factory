'use strict';
// Storage layer. Every write goes through tx(): one immediate transaction per
// request, so a check and the act that depends on it cannot be interleaved.
const { DatabaseSync } = require('node:sqlite');
const { readFileSync, existsSync } = require('node:fs');
const { join } = require('node:path');

let db;

function open(path = process.env.DB_PATH || ':memory:') {
  db = new DatabaseSync(path);
  db.exec('PRAGMA foreign_keys = ON');
  if (path !== ':memory:') db.exec('PRAGMA journal_mode = WAL');
  db.exec('PRAGMA busy_timeout = 5000');
  const schema = join(__dirname, 'schema.sql');
  if (existsSync(schema)) db.exec(readFileSync(schema, 'utf8'));
  return db;
}

// BEGIN IMMEDIATE takes the write lock up front, so two concurrent callers
// serialize here instead of both reading a stale value and both writing.
function tx(fn) {
  db.exec('BEGIN IMMEDIATE');
  try {
    const out = fn(db);
    db.exec('COMMIT');
    return out;
  } catch (e) {
    try { db.exec('ROLLBACK'); } catch {}
    throw e;
  }
}

const get = (sql, ...a) => db.prepare(sql).get(...a);
const all = (sql, ...a) => db.prepare(sql).all(...a);
const run = (sql, ...a) => db.prepare(sql).run(...a);

module.exports = { open, tx, get, all, run, handle: () => db };
