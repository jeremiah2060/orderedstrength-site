#!/usr/bin/env node
/* Measure the rendered page with real geometry, over the Chrome DevTools Protocol.
   Zero dependencies: node's global WebSocket + the local Chrome binary.
   A screenshot shows you that something is wrong; this tells you by how many pixels. */
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync, mkdirSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
// 🔒 THE DEBUGGING PORT IS PER RUN, NOT A CONSTANT. It was `const PORT = 9333` until
// 2026-08-31, so two harness runs at once both spawned Chrome on the same port and the
// second one DROVE THE FIRST ONE'S BROWSER. Measured: two ./check.sh runs started seconds
// apart wedged with no log output for twenty minutes and left eleven headless Chromes alive,
// because killing the run from outside never let node reach the `finally` that reaps the
// group. Nothing reported a collision; it simply hung, which is the worst way for a harness
// to fail. `--remote-debugging-port=0` makes the OS choose, and Chrome writes the number it
// got into DevToolsActivePort inside the profile directory, already unique per run.
const activePort = (profile) => {
  const f = join(profile, 'DevToolsActivePort');
  if (!existsSync(f)) return null;
  const n = parseInt(readFileSync(f, 'utf8').split('\n')[0], 10);
  return Number.isFinite(n) ? n : null;
};

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function httpJSON(port, path) {
  const r = await fetch(`http://127.0.0.1:${port}${path}`);
  return r.json();
}

class CDP {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); this.handlers = new Map();
    ws.onmessage = e => { const m = JSON.parse(e.data);
      if (m.id && this.pending.has(m.id)) { const { res, rej } = this.pending.get(m.id); this.pending.delete(m.id);
        m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); }
      else if (m.method && this.handlers.has(m.method)) this.handlers.get(m.method)(m.params); }; }
  send(method, params = {}) { const id = ++this.id;
    return new Promise((res, rej) => { this.pending.set(id, { res, rej }); this.ws.send(JSON.stringify({ id, method, params })); }); }
  on(method, fn) { this.handlers.set(method, fn); }
}

/* `args` appends extra Chrome flags. Added 2026-09-02 to test the Spanish language redirect,
   which is decided by `navigator.language` and therefore cannot be exercised at all without a
   browser that reports a different one. A stubbed navigator would be testing the stub. */
export async function withPage(fn, { width = 1440, height = 900, dsf = 2, args = [] } = {}) {
  const profile = mkdtempSync(join(tmpdir(), 'os-measure-'));
  // 🔒 KILL THE GROUP, NOT THE PARENT. Chrome forks renderer, GPU and zygote children, and
  // killing only the process we spawned leaves them alive holding their profile directory.
  // Measured at the end of this session: 7 headless Chromes still running from harness calls
  // that had all returned cleanly. `detached: true` puts them in their own process group so
  // `process.kill(-pid)` reaches every one of them.
  const chrome = spawn(CHROME, [
    '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--disable-extensions',
    '--hide-scrollbars', '--force-color-profile=srgb', '--disable-lcd-text',
    `--window-size=${width},${height}`, ...args, 'about:blank',
  ], { stdio: 'ignore', detached: true });

  let target = null, port = null;
  for (let i = 0; i < 60 && !target; i++) {
    port = port ?? activePort(profile);
    if (port) {
      try { const list = await httpJSON(port, '/json/list'); target = list.find(t => t.type === 'page'); } catch {}
    }
    if (!target) await sleep(250);
  }
  if (!target) {
    // Reap the GROUP here too: the old path called chrome.kill(), which leaves the renderer
    // and GPU children alive holding the profile, the exact leak the finally below exists for.
    try { process.kill(-chrome.pid, 'SIGKILL'); } catch { try { chrome.kill('SIGKILL'); } catch {} }
    throw new Error(port ? `Chrome came up on ${port} but served no page target`
                         : 'Chrome never wrote DevToolsActivePort, so it never came up');
  }

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  const cdp = new CDP(ws);
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width, height, deviceScaleFactor: dsf, mobile: width < 700,
  });

  const api = {
    async goto(url) {
      const loaded = new Promise(res => cdp.on('Page.loadEventFired', res));
      await cdp.send('Page.navigate', { url });
      await loaded; await sleep(700);
    },
    async evaluate(expr) {
      const r = await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
      return r.result.value;
    },
    async shot(path, { full = false } = {}) {
      /* 🔒 NEVER RESIZE THE VIEWPORT TO CAPTURE A FULL PAGE. Growing the viewport to the
         document height also grows 100svh, so `.hero{min-height:calc(100svh - 5rem)}`
         expanded to ten thousand pixels and the capture showed a page that does not
         exist: 3,500 px of blank space and the fixed bar stranded mid-document. Clip
         instead, so the layout being photographed is the layout a visitor gets. */
      let params = { format: 'png' };
      if (full) {
        const m = await cdp.send('Page.getLayoutMetrics');
        params.captureBeyondViewport = true;
        params.clip = { x: 0, y: 0, width: Math.ceil(m.cssContentSize.width),
                        height: Math.min(Math.ceil(m.cssContentSize.height), 30000), scale: 1 };
      }
      const { data } = await cdp.send('Page.captureScreenshot', params);
      mkdirSync(join(path, '..'), { recursive: true });
      writeFileSync(path, Buffer.from(data, 'base64'));
      return path;
    },
    async scrollTo(y) { await api.evaluate(`window.scrollTo(0,${y});"ok"`); await sleep(400); },
  };

  try { return await fn(api); }
  finally {
    ws.close();
    try { process.kill(-chrome.pid, 'SIGKILL'); } catch { try { chrome.kill('SIGKILL'); } catch {} }
    await sleep(200);
    try { rmSync(profile, { recursive: true, force: true }); } catch {}
  }
}
