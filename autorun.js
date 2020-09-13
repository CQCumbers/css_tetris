const flip = document.getElementById('fl');
let counter = 0;
const step = () => {
  if (counter++ >= 100) { return; }
  const btns = Array.from(document.querySelectorAll('label')).filter(s =>
     window.getComputedStyle(s).getPropertyValue('display') != 'none' && s != flip
  );
  btns.forEach(btn => btn.click());
  flip.click();
  window.requestAnimationFrame(step);
}
step();
