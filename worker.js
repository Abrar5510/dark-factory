// POST /api/run {task} -> NDJSON stream of seat events. Seats = mandates/*.md as system prompts,
// each run on the model its mandate names. Featherless is OpenAI-compatible.
// Secrets: FEATHERLESS_API_KEY (required), ACCESS_CODE (optional gate).
const MAX_TASK = 4000;

async function ask(env, mandate, user) {
  const model = mandate.match(/^Model:\s*(.+)$/m)[1].trim();
  const r = await fetch("https://api.featherless.ai/v1/chat/completions", {
    method: "POST",
    headers: { authorization: `Bearer ${env.FEATHERLESS_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ model, max_tokens: 4096, messages: [{ role: "system", content: mandate }, { role: "user", content: user }] }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error?.message || j.error || r.statusText);
  return j.choices[0].message.content;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname !== "/api/run") return env.ASSETS.fetch(req);
    if (req.method !== "POST") return new Response("POST only", { status: 405 });
    if (env.ACCESS_CODE && req.headers.get("x-access-code") !== env.ACCESS_CODE)
      return new Response("bad access code", { status: 401 });
    const { task } = await req.json().catch(() => ({}));
    if (!task || task.length > MAX_TASK) return new Response(`task required, <= ${MAX_TASK} chars`, { status: 400 });

    const mandate = async (n) => (await env.ASSETS.fetch(new URL(`/mandates/${n}.md`, url))).text();

    const { readable, writable } = new TransformStream();
    const w = writable.getWriter();
    const enc = new TextEncoder();
    const emit = (o) => w.write(enc.encode(JSON.stringify(o) + "\n"));

    // Runs one seat: announces it, calls the model, posts the reply.
    const seat = async (name, file, input) => {
      await emit({ seat: name, status: "working" });
      try {
        const text = await ask(env, await mandate(file), input);
        await emit({ seat: name, status: "done", text });
        return text;
      } catch (e) {
        await emit({ seat: name, status: "error", text: String(e.message) });
        throw e;
      }
    };

    (async () => {
      try {
        const spec = await seat("Lead", "lead",
          `Dispatch from the human:\n\n${task}\n\nWrite the full-text handoff every seat will receive: the complete requirements, nothing summarised.`);
        // Blind step: each seat sees only the handoff, never another seat's output.
        // ponytail: sequential, Featherless plans cap concurrent large models; Promise.all if yours allows it
        const built = await seat("Builder", "builder", spec);
        const ui = await seat("Surface", "surface", spec);
        const kit = await seat("Second Reader", "second-reader", spec);
        const verdict = await seat("Referee", "referee",
          `HANDOFF:\n${spec}\n\nSERVICE (Builder):\n${built}\n\nSURFACE:\n${ui}\n\nCONFORMANCE KIT (Second Reader):\n${kit}\n\nReport divergences as two unattributed behaviours plus a minimal trace.`);
        await seat("Lead", "lead",
          `HANDOFF:\n${spec}\n\nREFEREE REPORT:\n${verdict}\n\nSERVICE:\n${built}\n\nRule on each divergence quoting the spec word for word, then give the stage report.`);
      } catch (_) { /* seat error already emitted */ }
      await emit({ done: true });
      await w.close();
    })();

    return new Response(readable, { headers: { "content-type": "application/x-ndjson", "cache-control": "no-store" } });
  },
};
