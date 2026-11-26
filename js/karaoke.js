/* Word-level karaoke highlight for the static lesson pages.
 * Reads window.EP2_WORDS (word start/end times) injected into the page and
 * highlights the matching <span class="kw" data-wi="N"> as the page's own
 * <audio> plays. Nothing else: no controls, no progress, no UI changes.
 */
(function () {
  "use strict";

  var words = window.EP2_WORDS || [];
  var spans = document.querySelectorAll(".kw[data-wi]");
  if (!words.length || !spans.length) return;
  var audio = document.querySelector("audio");
  if (!audio) return;

  var style = document.createElement("style");
  style.textContent = ".kw.on{background:#ffe08a;color:#201400;border-radius:2px}";
  document.head.appendChild(style);

  var byIndex = {};
  for (var i = 0; i < spans.length; i++) {
    byIndex[spans[i].getAttribute("data-wi")] = spans[i];
  }

  var active = -1;

  function update() {
    var t = audio.currentTime;
    var idx = -1;

    if (!(t < words[0][0] - 0.3)) {
      var lo = 0, hi = words.length - 1;
      while (lo <= hi) {
        var mid = (lo + hi) >> 1;
        if (words[mid][0] <= t) { idx = mid; lo = mid + 1; } else { hi = mid - 1; }
      }
      if (idx >= 0 && words[idx][1] <= words[idx][0]) idx = -1;
    }

    if (idx === active) return;
    if (active >= 0 && byIndex[active]) byIndex[active].classList.remove("on");
    active = idx;
    if (idx >= 0 && byIndex[idx]) byIndex[idx].classList.add("on");
  }

  (function loop() {
    update();
    requestAnimationFrame(loop);
  })();
})();
