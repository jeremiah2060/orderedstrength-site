#!/usr/bin/env node
/* Measure the rendered page with real geometry, over the Chrome DevTools Protocol.
   Zero dependencies: node's global WebSocket + the local Chrome binary.
   A screenshot shows you that something is wrong; this tells you by how many pixels. */
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function httpJSON(path) {
  const r = await fetch(`http://127.0.0.1:${PORT}${path}`);
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

export async function withPage(fn, { width = 1440, height = 900, dsf = 2 } = {}) {
  const profile = mkdtempSync(join(tmpdir(), 'os-measure-'));
  const chrome = spawn(CHROME, [
    '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--disable-extensions',
    '--hide-scrollbars', '--force-color-profile=srgb', '--disable-lcd-text',
    `--window-size=${width},${height}`, 'about:blank',
  ], { stdio: 'ignore' });

  let target = null;
  for (let i = 0; i < 60 && !target; i++) {
    try { const list = await httpJSON('/json/list'); target = list.find(t => t.type === 'page'); } catch {}
    if (!target) await sleep(250);
  }
  if (!target) { chrome.kill(); throw new Error('Chrome never came up'); }

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
  finally { ws.close(); chrome.kill('SIGKILL'); await sleep(200); try { rmSync(profile, { recursive: true, force: true }); } catch {} }
}
