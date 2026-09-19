'use strict';
// Transport layer. Domain-free on purpose: routes and their shapes come from
// the SPEC and are registered in routes.js.
const http = require('node:http');
const { readFile } = require('node:fs/promises');
const { join, normalize, extname } = require('node:path');
const db = require('./db');

const MAX_BODY = 1 << 20; // 1 MiB; a larger request is refused, not buffered.
const PUBLIC = join(__dirname, 'public');

// A fault the caller is meant to see, with the code the SPEC documents for it.
class Fault extends Error {
  constructor(status, code, message, extra) {
    super(message);
    Object.assign(this, { status, code, extra });
  }
}

const routes = [];
// path may contain :params, e.g. '/things/:id'
function route(method, path, handler) {
  const names = [];
  const rx = new RegExp('^' + path.replace(/:(\w+)/g, (_, n) => (names.push(n), '([^/]+)')) + '$');
  routes.push({ method, rx, names, handler });
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };

function send(res, status, body, headers = {}) {
  if (body === undefined || body === null) return res.writeHead(status, headers).end();
  const buf = Buffer.isBuffer(body) ? body : Buffer.from(JSON.stringify(body));
  res.writeHead(status, { 'content-type': 'application/json', 'content-length': buf.length, ...headers });
  res.end(buf);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > MAX_BODY) { reject(new Fault(413, 'payload_too_large', 'Request body is too large')); req.destroy(); return; }
      chunks.push(c);
    });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

async function serveStatic(url, res) {
  const rel = normalize(url === '/' ? '/index.html' : url).replace(/^(\.\.[/\\])+/, '');
  const file = join(PUBLIC, rel);
  if (!file.startsWith(PUBLIC)) return false; // refuse traversal out of public/
  try {
    const buf = await readFile(file);
    send(res, 200, buf, { 'content-type': MIME[extname(file)] || 'application/octet-stream' });
    return true;
  } catch { return false; }
}

async function handle(req, res) {
  const url = new URL(req.url, 'http://localhost');
  const path = url.pathname.replace(/\/+$/, '') || '/';

  if (req.method === 'GET' && path === '/health') return send(res, 200, { status: 'ok' });

  const match = routes.find((r) => r.method === req.method && r.rx.test(path));
  if (!match) {
    if (req.method === 'GET' && (await serveStatic(url.pathname, res))) return;
    throw new Fault(404, 'not_found', 'No such resource');
  }

  const raw = await readBody(req);
  let body;
  if (raw.length) {
    try { body = JSON.parse(raw); }
    // Malformed input is a documented refusal, never an unhandled throw.
    catch { throw new Fault(400, 'invalid_json', 'Request body is not valid JSON'); }
  }

  const params = Object.fromEntries(match.names.map((n, i) => [n, decodeURIComponent(path.match(match.rx)[i + 1])]));
  const ctx = { params, query: url.searchParams, body, headers: req.headers, method: req.method, path };
  const [status, payload, headers] = await match.handler(ctx);
  send(res, status, payload, headers);
}

function server() {
  return http.createServer((req, res) => {
    handle(req, res).catch((e) => {
      if (e instanceof Fault) return send(res, e.status, { error: { code: e.code, message: e.message, ...(e.extra || {}) } });
      // Anything unforeseen still leaves as a documented shape, never a bare crash.
      console.error('unhandled', e);
      send(res, 500, { error: { code: 'internal_error', message: 'Unexpected server error' } });
    });
  });
}

module.exports = { server, route, Fault, send };

if (require.main === module) {
  db.open();
  require('./routes');
  const port = Number(process.env.PORT || 3000);
  server().listen(port, '0.0.0.0', () => console.log(`listening on ${port}`));
}
