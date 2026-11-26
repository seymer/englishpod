/* Circular 中/英 button: cycle Chinese display clear -> mosaic -> English-only.
 * Sits at the top-right inside the body's A4-like border.
 * Choice is remembered locally. No other behaviour is changed.
 */
(function () {
  "use strict";

  var KEY = "ep2_zh_mode";
  var STATES = ["show", "blur", "en"];
  var stored = null;
  try { stored = localStorage.getItem(KEY); } catch (e) {}
  var state = STATES.indexOf(stored) < 0 ? "show" : stored;

  var style = document.createElement("style");
  style.textContent =
    ".zh-blur .zh,.zh-blur .zh-name,.zh-blur .zh-def,.zh-blur .zh-title{" +
    "filter:blur(4px);opacity:.55;cursor:help}" +
    ".zh-blur .zh:hover,.zh-blur .zh-name:hover,.zh-blur .zh-def:hover,.zh-blur .zh-title:hover{" +
    "filter:none;opacity:1}" +
    ".zh-hide .zh,.zh-hide .zh-name,.zh-hide .zh-def,.zh-hide .zh-title{visibility:hidden}" +
    "body{position:relative}" +
    ".zh-toggle-btn{position:absolute;top:8px;right:8px;display:inline-flex;" +
    "align-items:center;justify-content:center;width:24px;height:24px;padding:0;" +
    "border:1px solid #990000;border-radius:50%;background:#fff;color:#990000;" +
    "font-family:inherit;font-size:14px;line-height:1;cursor:pointer;opacity:.85}" +
    ".zh-toggle-btn:hover{opacity:1}" +
    ".zh-glyph{display:block}" +
    ".zh-toggle-btn.blurred{background:#990000;color:#fff}" +
    ".zh-toggle-btn.blurred .zh-glyph{filter:blur(.5px)}";
  document.head.appendChild(style);

  var button = document.createElement("button");
  button.type = "button";
  button.className = "zh-toggle-btn";
  var glyph = document.createElement("span");
  glyph.className = "zh-glyph";
  button.appendChild(glyph);

  function apply() {
    document.body.classList.remove("zh-blur", "zh-hide");
    button.classList.remove("blurred", "english");
    if (state === "blur") {
      document.body.classList.add("zh-blur");
      button.classList.add("blurred");
    } else if (state === "en") {
      document.body.classList.add("zh-hide");
      button.classList.add("english");
    }
    glyph.textContent = state === "en" ? "英" : "中";
    try { localStorage.setItem(KEY, state); } catch (e) {}
  }

  button.addEventListener("click", function () {
    state = STATES[(STATES.indexOf(state) + 1) % STATES.length];
    apply();
  });

  document.body.appendChild(button);
  apply();
})();
