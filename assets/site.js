/* Shared chrome. Small on purpose.
   🔒 IT MUST NEVER BE ABLE TO HIDE CONTENT. The hiding class is added by THIS script,
   so a failed script means no hiding at all, and a 1.6s failsafe reveals everything
   regardless of whether the observer ever fired. */
(function(){
'use strict';
var root = document.documentElement;

/* ── sticky bar + progress ── */
var bar = document.querySelector('.bar');
if (bar){
  var prog = bar.querySelector('.prog');
  var chrome = function(){
    bar.classList.toggle('stuck', window.scrollY > 8);
    if (prog){
      var h = document.documentElement.scrollHeight - window.innerHeight;
      prog.style.width = (h > 0 ? Math.min(1, window.scrollY / h) * 100 : 0) + '%';
    }
  };
  window.addEventListener('scroll', chrome, {passive:true});
  window.addEventListener('resize', chrome, {passive:true});
  chrome();
}

/* ── THE SCALE ──
   A linear gauge in the left margin. Built from the page's own section labels, so there is
   no second list to keep in sync. Section offsets are measured ONCE and on resize, never
   on scroll: reading layout inside a scroll handler is the classic way to make a smooth
   page stutter. Everything per-frame is a style write, inside one rAF. */
(function(){
  var scenes = [].slice.call(document.querySelectorAll('main > .scene'));
  if (scenes.length < 3 || !document.body) return;

  /* the number beside the needle must be the SAME number the stylesheet prints at the end
     of the specification rule, and the stylesheet counts eyebrows, not sections. Count the
     same thing the same way rather than assuming they agree. */
  var brows = [].slice.call(document.querySelectorAll('.eyebrow'));
  var items = scenes.map(function(sec){
    var b = sec.querySelector('.eyebrow');
    return { el: sec,
             n: b ? brows.indexOf(b) + 1 : 0,
             label: b ? (b.textContent || '').trim() : '' };
  });

  var rail = document.createElement('nav');
  rail.className = 'rail'; rail.setAttribute('aria-hidden', 'true');
  var line = document.createElement('span'); line.className = 'rail__line'; rail.appendChild(line);
  var ticks = items.map(function(){
    var t = document.createElement('span'); t.className = 'rail__tick'; rail.appendChild(t); return t;
  });
  /* THE SAME INSTRUMENT, LAID ON ITS SIDE, for every width the margin cannot reach. Built
     from `items` above, so there is still exactly one list of sections on this page. The
     stylesheet shows it only below 95rem AND only once `has-rail` says it was built. */
  var head = document.querySelector('.bar');
  var strip = null, sNum = null, sLab = null, sTicks = [], sNeedle = null;
  if (head){
    strip = document.createElement('div');
    strip.className = 'barscale'; strip.setAttribute('aria-hidden', 'true');
    sNum = document.createElement('b'); sNum.className = 'barscale__n';
    sLab = document.createElement('em'); sLab.className = 'barscale__lab';
    var sTrack = document.createElement('span'); sTrack.className = 'barscale__track';
    sTicks = items.map(function(){
      var t = document.createElement('i'); t.className = 'barscale__tick';
      sTrack.appendChild(t); return t;
    });
    sNeedle = document.createElement('span'); sNeedle.className = 'barscale__needle';
    sTrack.appendChild(sNeedle);
    strip.appendChild(sNum); strip.appendChild(sLab); strip.appendChild(sTrack);
    head.appendChild(strip);
  }

  var needle = document.createElement('span'); needle.className = 'rail__needle';
  var bar = document.createElement('i'), num = document.createElement('b'), lab = document.createElement('em');
  needle.appendChild(bar); needle.appendChild(num); needle.appendChild(lab);
  rail.appendChild(needle);
  document.body.appendChild(rail);
  document.documentElement.classList.add('has-rail');

  var FOCUS = 0.34;                       /* the line a section is "at" when you read it */
  var tops = [], marks = [], span = 1, railTop = 0, railH = 0, queued = false;
  var labH = 0, labMode = null;

  function measure(){
    var docH = document.documentElement.scrollHeight;
    span = Math.max(1, docH - window.innerHeight);
    /* offsetTop, not getBoundingClientRect: the ticks and the needle are positioned
       against .rail's own box, and the rect is viewport-relative, so mixing the two put
       every mark exactly one navigation-bar lower than the scale it belongs to. */
    railTop = line.offsetTop; railH = line.offsetHeight;
    /* 🔒 ONE COORDINATE SPACE, OR THE GAUGE LIES. The needle rides SCROLL PROGRESS and the
       label named the section under a focus line one third down the viewport. Both were
       true and they described different things, so the needle sat beside tick 04 while its
       own label read 05. A tick is therefore placed at the scroll progress AT WHICH ITS
       SECTION BECOMES ACTIVE, not at its proportional position in the document. Now
       "needle is level with this tick" and "this section is the one you are reading" are
       the same statement, and cannot drift apart. */
    tops = items.map(function(it){
      return it.el.getBoundingClientRect().top + window.scrollY;
    });
    marks = tops.map(function(top){
      return Math.min(1, Math.max(0, (top - window.innerHeight * FOCUS) / span));
    });
    items.forEach(function(it, i){
      ticks[i].style.top = (railTop + marks[i] * railH) + 'px';
      /* the SAME mark, so the two scales cannot disagree about where a section starts */
      if (sTicks[i]) sTicks[i].style.left = (marks[i] * 100) + '%';
    });
    paint();
  }

  function paint(){
    queued = false;
    var y = window.scrollY;
    var prog = Math.min(1, Math.max(0, y / span));
    var ny = railTop + prog * railH;
    needle.style.top = ny + 'px';

    var active = 0;
    for (var i = 0; i < marks.length; i++) if (marks[i] <= prog + 1e-4) active = i;
    var it = items[active];
    num.textContent = it.n ? (it.n < 10 ? '0' + it.n : String(it.n)) : '';
    if (lab.textContent !== it.label){ lab.textContent = it.label; labH = lab.offsetHeight; }

    /* A vertical label centred on the needle runs off the top of the scale as soon as the
       needle is near the top of it, which is where every visitor starts. So it hangs from
       the needle at the top of the travel, stands on it at the bottom, and is centred in
       between. The label height is read only when the LABEL CHANGES, never per frame: a
       layout read inside a scroll handler is how a smooth page starts to stutter. */
    var half = labH / 2;
    var mode = (ny - railTop) < half ? 'top' : (railTop + railH - ny) < half ? 'bottom' : '';
    if (mode !== labMode){
      labMode = mode;
      lab.style.top = mode === 'bottom' ? 'auto' : '0';
      lab.style.bottom = mode === 'bottom' ? '0' : 'auto';
      lab.style.transform = mode ? 'rotate(180deg)' : 'translateY(-50%) rotate(180deg)';
    }

    if (strip){
      sNum.textContent = num.textContent;
      if (sLab.textContent !== it.label) sLab.textContent = it.label;
      sNeedle.style.left = (prog * 100) + '%';
      for (var s = 0; s < sTicks.length; s++){
        sTicks[s].className = 'barscale__tick' + (s === active ? ' on' : '');
      }
    }

    for (var k = 0; k < ticks.length; k++){
      var d = Math.abs(parseFloat(ticks[k].style.top) - ny);
      var near = Math.max(0, 1 - d / 220);
      ticks[k].style.opacity = String(0.45 + near * 0.55);
      ticks[k].style.width = (0.5625 + near * 0.25) + 'rem';
      ticks[k].style.backgroundColor = k === active ? 'var(--teal)' : 'var(--line)';
    }
  }

  function onScroll(){ if (!queued){ queued = true; requestAnimationFrame(paint); } }
  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('resize', measure, {passive:true});
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
  measure();
  setTimeout(measure, 400);
})();

/* ── the language choice, recorded from either direction ──
   The head script on the English pages sends a Spanish phone to /es/ exactly once, and only
   while nothing is stored. This is what stores it: using either language link is a decision, and
   after it the reader stays where they put themselves. Without this the English link on /es/
   would work once and then be undone by the next visit to the root.
   🔒 AND SINCE 2026-09-03 IT IS THE ONLY WRITER OF os-lang. The head script used to record its
   own automatic redirect here too, which made a guess about a browser indistinguishable from a
   person's decision. A click is a decision. A language list is not. */
document.addEventListener('click', function (e) {
  var a = e.target && e.target.closest ? e.target.closest('a[hreflang]') : null;
  if (!a) return;
  var want = a.getAttribute('hreflang');
  if (want !== 'en' && want !== 'es') return;
  try { localStorage.setItem('os-lang', want); } catch (err) { /* not storable: harmless */ }
}, true);

/* ── WHEN A BROWSER TRANSLATES THE SPANISH PAGE, SAY SO ──────────────────────────────────
   FOUND BY THE CEO, 2026-09-03, and every instrument on this site was green while he looked at
   it: "if you switch to spanish it only appears for a split second then goes back to english
   again, but all the screenshots are in spanish, only the content is bouncing". That last clause
   is the whole diagnosis. Text changing while the images do not is not a navigation, and it is
   not this site: it is Chrome's own translator, from the "always translate Spanish" he switched
   on for /es/ on 2026-08-31, replaying on every visit since.

   🔒 A PAGE THAT IS ALREADY A REAL TRANSLATION HAS NOTHING TO GAIN FROM A MACHINE ONE AND
   EVERYTHING TO LOSE. translate-gate.py guards the ELEMENTS a translator must not rewrite, and
   it is right about all of them, but no one had ever said that this page should not be
   translated at all. The Spanish pages now declare notranslate, which stops Chrome. Safari's
   translator does not read that declaration, so the page also has to be able to notice.

   🔒 AND IT NOTICES BY WATCHING ITS OWN WORDS, NOT BY ASKING THE BROWSER. Chrome stamps
   translated-ltr on <html> and Safari stamps nothing, so a check written against the class name
   would be a check that can only see one of the two browsers this has to work in. The headline
   is read once here, before any translator has run, and a change to it that this site did not
   make is the evidence. That test has no browser in it.

   WHAT IT RESTS ON, SAID PLAINLY RATHER THAN LEFT TO BE DISCOVERED: that this script reads the
   headline before a translator rewrites it. It is a defer script, so it runs after parsing and
   before DOMContentLoaded, and a translator detects the page language and swaps text after load.
   That ordering holds in both engines today and is not a thing either one promises. The class
   check is the second path for Chrome if it ever stops holding; for Safari the honest statement
   is that a translation applied before this line would be invisible to it, and the header's
   language link, which needs none of this, is why that is a degradation and not a failure. */
(function () {
  if (!/^es/i.test(root.getAttribute('lang') || '')) return;   /* English prose stays translatable on purpose */
  var h1 = document.querySelector('h1');
  var twin = document.querySelector('a[hreflang="en"]');
  if (!h1 || !twin) return;
  var ours = (h1.textContent || '').replace(/\s+/g, ' ').trim();
  if (!ours) return;
  var shown = false;

  function rewritten() {
    return /(^|\s)translated-/.test(root.className) ||
           (h1.textContent || '').replace(/\s+/g, ' ').trim() !== ours;
  }

  function tell() {
    if (shown || !rewritten()) return;
    shown = true;
    var bar = document.createElement('p');
    bar.className = 'mtnote';
    /* 🔒 translate="no" ON THE WHOLE LINE. This is the one sentence on the page that must
       survive the thing it is reporting. A notice about a translation that is itself translated
       tells the reader nothing they can act on. */
    bar.setAttribute('translate', 'no');
    bar.setAttribute('lang', 'es');
    bar.setAttribute('role', 'status');
    bar.appendChild(document.createTextNode(
      'Tu navegador tradujo esta p\u00e1gina. Las frases que citamos de la app y las huellas del sello ya no son las nuestras. '));
    var a = document.createElement('a');
    /* the twin's href, never a second copy of the mapping: one place decides where English is */
    a.href = twin.getAttribute('href');
    a.setAttribute('hreflang', 'en');
    a.setAttribute('lang', 'en');
    a.setAttribute('translate', 'no');
    a.className = 'lang';
    a.textContent = 'English';
    bar.appendChild(a);
    var host = document.getElementById('main') || document.body;
    host.insertBefore(bar, host.firstChild);
  }

  tell();
  /* a translator runs after load, and on its own schedule, so watch rather than sample once */
  if (window.MutationObserver) {
    var mo = new MutationObserver(function () { tell(); if (shown) mo.disconnect(); });
    mo.observe(h1, { childList: true, characterData: true, subtree: true });
    mo.observe(root, { attributes: true, attributeFilter: ['class'] });
    setTimeout(function () { tell(); }, 4000);
  } else {
    setTimeout(tell, 1200); setTimeout(tell, 4000);
  }
})();

/* ── reveal ── */
var targets = [].slice.call(document.querySelectorAll('.reveal'));
if (!targets.length) return;
var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var showAll = function(){ targets.forEach(function(n){ n.classList.add('in'); }); };

if (reduce || !('IntersectionObserver' in window)) { showAll(); return; }

root.classList.add('anim');              // only NOW is anything hidden
var io = new IntersectionObserver(function(en){
  en.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
}, {threshold:0.08, rootMargin:'0px 0px -4% 0px'});
targets.forEach(function(n){ io.observe(n); });

/* anything already on screen appears immediately, not on a scroll */
requestAnimationFrame(function(){
  targets.forEach(function(n){
    if (n.getBoundingClientRect().top < window.innerHeight) n.classList.add('in');
  });
});
/* and the failsafe: whatever happened above, nothing stays hidden */
setTimeout(showAll, 1600);
})();
