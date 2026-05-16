(function () {
  var KEY = "hmd-theme";
  var btn = document.getElementById("theme-toggle");
  var root = document.documentElement;
  function apply(theme) {
    if (theme === "dark") root.setAttribute("data-theme", "dark");
    else root.removeAttribute("data-theme");
  }
  var saved = localStorage.getItem(KEY);
  if (saved) apply(saved);
  else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) apply("dark");
  btn && btn.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    apply(next);
    localStorage.setItem(KEY, next);
  });
})();
