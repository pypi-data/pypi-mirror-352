
function loadES5() {
  var el = document.createElement('script');
  el.src = '/knx_static/frontend_es5/entrypoint.f7b6a0e8adf6dc42.js';
  document.body.appendChild(el);
}
if (/.*Version\/(?:11|12)(?:\.\d+)*.*Safari\//.test(navigator.userAgent)) {
    loadES5();
} else {
  try {
    new Function("import('/knx_static/frontend_latest/entrypoint.a61ab678a88ad29b.js')")();
  } catch (err) {
    loadES5();
  }
}
  