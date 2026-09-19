'use strict';
// Guards the transport contract the whole service rests on. These hold before
// a single route from the SPEC exists, and must keep holding after.
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { start } = require('./_harness');
const { route, Fault } = require('../server');

let app;
before(async () => {
  route('POST', '/_probe/:id', async (c) => {
    if (!c.body || c.body.ok !== true) throw new Fault(422, 'probe_invalid', 'ok must be true');
    return [201, { id: c.params.id, got: c.body }];
  });
  app = await start();
});
after(() => app.close());

test('health reports ok', async () => {
  const r = await app.call('GET', '/health');
  assert.equal(r.status, 200);
  assert.equal(r.body.status, 'ok');
});

test('path parameters are decoded', async () => {
  const r = await app.call('POST', '/_probe/a%20b', { ok: true });
  assert.equal(r.status, 201);
  assert.equal(r.body.id, 'a b');
});

test('a documented refusal keeps its code and shape', async () => {
  const r = await app.call('POST', '/_probe/x', { ok: false });
  assert.equal(r.status, 422);
  assert.equal(r.body.error.code, 'probe_invalid');
});

test('malformed input is refused, never a crash', async () => {
  for (const bad of ['{nope', '[', 'null-ish', '{"a":]']) {
    const r = await app.call('POST', '/_probe/x', bad);
    assert.ok(r.status < 500, `${bad} produced ${r.status}`);
  }
});

test('an unknown path is refused in the documented shape', async () => {
  const r = await app.call('GET', '/definitely/not/here');
  assert.equal(r.status, 404);
  assert.ok(r.body.error.code);
});

test('a traversal attempt does not escape the served folder', async () => {
  const r = await app.call('GET', '/../db.js');
  assert.ok(r.status >= 400, `traversal returned ${r.status}`);
  assert.ok(!r.text.includes('DatabaseSync'));
});
