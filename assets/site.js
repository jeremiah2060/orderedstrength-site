/* Shared chrome: sticky bar, scroll progress, the measurement rail, and reveals.
   No libraries. transform and opacity only, so everything stays on the compositor. */
(function(){
'use strict';
var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* sticky bar + progress */
var bar = document.querySelector('.bar');
var prog = bar && bar.querySelector('.prog');
function chrome(){
  if (!bar) return;
  bar.classList.toggle('stuck', window.scrollY > 8);
  if (prog){
    var h = document.documentElement.scrollHeight - window.innerHeight;
    prog.style.width = (h > 0 ? Math.min(1, window.scrollY / h) * 100 : 0) + '%';
  }
}
window.addEventListener('scroll', chrome, {passive:true});
window.addEventListener('resize', chrome, {passive:true});
chrome();

/* reveals */
var reveals = document.querySelectorAll('.r');
if (reduce || !('IntersectionObserver' in window)){
  Array.prototype.forEach.call(reveals, function(n){ n.classList.add('in'); });
} else {
  var io = new IntersectionObserver(function(en){
    en.forEach(function(e){
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      io.unobserve(e.target);
      if (e.target.dataset && e.target.dataset.onreveal && window[e.target.dataset.onreveal]){
        window[e.target.dataset.onreveal]();
      }
    });
  }, {threshold:0.18, rootMargin:'0px 0px -6% 0px'});
  Array.prototype.forEach.call(reveals, function(n){ io.observe(n); });
}

/* the measurement rail marks which section you are in, and jumps to one */
var rail = document.querySelector('.rail');
if (rail){
  var links = rail.querySelectorAll('a');
  var targets = [];
  Array.prototype.forEach.call(links, function(a){
    var t = document.querySelector(a.getAttribute('href'));
    if (t) targets.push({ link:a, el:t });
  });
  var mark = function(){
    var best = null, mid = window.innerHeight * 0.38;
    targets.forEach(function(t){
      var top = t.el.getBoundingClientRect().top;
      if (top <= mid && (!best || top > best.el.getBoundingClientRect().top)) best = t;
    });
    targets.forEach(function(t){
      if (t === best) t.link.setAttribute('aria-current','true');
      else t.link.removeAttribute('aria-current');
    });
  };
  window.addEventListener('scroll', mark, {passive:true});
  mark();
}
})();
