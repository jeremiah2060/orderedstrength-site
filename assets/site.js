/* Shared chrome. Deliberately small.
   It does NOT reveal content: every block on every page is visible without this file.
   The only thing here that touches layout is the scroll-progress hairline. */
(function(){
'use strict';
var bar = document.querySelector('.bar');
if (!bar) return;
var prog = bar.querySelector('.prog');
function chrome(){
  bar.classList.toggle('stuck', window.scrollY > 8);
  if (prog){
    var h = document.documentElement.scrollHeight - window.innerHeight;
    prog.style.width = (h > 0 ? Math.min(1, window.scrollY / h) * 100 : 0) + '%';
  }
}
window.addEventListener('scroll', chrome, {passive:true});
window.addEventListener('resize', chrome, {passive:true});
chrome();
})();
