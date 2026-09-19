'use strict';
// Every route the SPEC lists is registered here at kickoff:
//   route('GET', '/things/:id', async (ctx) => [200, { ... }]);
// A handler returns [status, body] or [status, body, headers] and throws a
// Fault for any documented refusal.
// eslint-disable-next-line no-unused-vars
const { route, Fault } = require('./server');
const db = require('./db');
