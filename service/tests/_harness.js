'use strict';
// Starts the service on a random port against a fresh in-memory store, so
// every test file is hermetic and needs no network and no fixture cleanup.
const db = require('../db');

async function start() {
  db.open(':memory:');
  delete require.cache[require.resolve('../routes')];
  const { server } = require('../server');
  require('../routes');
  const s = server().listen(0, '127.0.0.1');
  await new Promise((r) => s.once('listening', r));
  const base = `http://127.0.0.1:${s.address().port}`;

  const call = async (method, path, body, headers = {}) => {
    const res = await fetch(base + path, {
      method,
      headers: { 'content-type': 'application/json', ...headers },
      body: body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body),
    });
    const text = await res.text();
    let json; try { json = JSON.parse(text); } catch {}
    return { status: res.status, body: json, text, headers: res.headers };
  };

  return { base, call, close: () => new Promise((r) => s.close(r)) };
}

module.exports = { start };
