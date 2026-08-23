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
