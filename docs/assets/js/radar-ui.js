(function () {
  "use strict";

  var THEME_KEY = "radar-theme";
  var THEMES = ["system", "light", "dark"];
  var THEME_META = {
    system: {
      label: "跟随系统",
      svg: '<circle cx="128" cy="128" r="56" stroke="currentColor" stroke-width="18"/><path d="M128 24V44M128 212V232M24 128H44M212 128H232M54.5 54.5L68.6 68.6M187.4 187.4L201.5 201.5M201.5 54.5L187.4 68.6M68.6 187.4L54.5 201.5" stroke="currentColor" stroke-width="18" stroke-linecap="round"/>',
    },
    light: {
      label: "浅色模式",
      svg: '<circle cx="128" cy="128" r="60" stroke="currentColor" stroke-width="18"/><path d="M128 24V44M128 212V232M24 128H44M212 128H232" stroke="currentColor" stroke-width="18" stroke-linecap="round"/>',
    },
    dark: {
      label: "深色模式",
      svg: '<path d="M210.7 148.5A88 88 0 0 1 107.5 45.3 88 88 0 1 0 210.7 148.5Z" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>',
    },
  };

  function getTheme() {
    try {
      var val = localStorage.getItem(THEME_KEY);
      return val === "light" || val === "dark" ? val : "system";
    } catch (e) {
      return "system";
    }
  }

  function applyTheme(mode) {
    if (mode === "light" || mode === "dark") {
      document.documentElement.setAttribute("data-theme", mode);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    try {
      if (mode === "system") {
        localStorage.removeItem(THEME_KEY);
      } else {
        localStorage.setItem(THEME_KEY, mode);
      }
    } catch (e) {}
  }

  function initThemeToggle() {
    var btn = document.getElementById("radar-theme-toggle");
    if (!btn) return;
    var icon = btn.querySelector("svg");
    var label = btn.querySelector(".radar-theme-label");

    var renderBtn = function () {
      var cur = getTheme();
      var meta = THEME_META[cur];
      if (icon) icon.innerHTML = meta.svg;
      if (label) label.textContent = meta.label;
      btn.title = "切换主题（跟随系统、浅色、深色）";
    };

    renderBtn();
    btn.addEventListener("click", function () {
      var cur = getTheme();
      var next = THEMES[(THEMES.indexOf(cur) + 1) % THEMES.length];
      applyTheme(next);
      renderBtn();
    });
  }

  function initMobileMenu() {
    var toggle = document.getElementById("radar-menu-toggle");
    var drawer = document.getElementById("radar-mobile-drawer");
    if (!toggle || !drawer) return;

    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      drawer.setAttribute("aria-hidden", open ? "false" : "true");
      drawer.classList.toggle("is-open", open);
      document.body.style.overflow = open ? "hidden" : "";
    };

    toggle.addEventListener("click", function () {
      var isOpen = toggle.getAttribute("aria-expanded") === "true";
      setOpen(!isOpen);
    });

    drawer.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setOpen(false);
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  function initScrollReveals() {
    var els = document.querySelectorAll(".radar-reveal");
    if (!els.length) return;
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || typeof IntersectionObserver === "undefined") {
      els.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -32px 0px" });

    els.forEach(function (el) { observer.observe(el); });
  }

  function initTaglineReveal() {
    var words = Array.prototype.slice.call(document.querySelectorAll(".radar-reveal-word"));
    if (!words.length) return;
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      words.forEach(function (w) { w.classList.add("is-lit"); });
      return;
    }

    var rafPending = false;
    var updateWords = function () {
      rafPending = false;
      var triggerY = window.innerHeight * 0.78;
      var allLit = true;
      for (var i = 0; i < words.length; i += 1) {
        var word = words[i];
        if (word.classList.contains("is-lit")) continue;
        var rect = word.getBoundingClientRect();
        var progressLine = rect.top + Math.min(rect.left * 0.12, 120);
        if (progressLine <= triggerY) {
          word.classList.add("is-lit");
        } else {
          allLit = false;
        }
      }
      if (allLit) {
        window.removeEventListener("scroll", onScroll);
        window.removeEventListener("resize", onScroll);
      }
    };

    var onScroll = function () {
      if (!rafPending) {
        rafPending = true;
        window.requestAnimationFrame(updateWords);
      }
    };

    updateWords();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
  }

  function parseNumericValue(raw) {
    var text = (raw || "").trim();
    if (!text || text === "—" || text === "-") return null;
    if (/^\d{4}-\d{2}-\d{2}$/.test(text)) {
      return Date.parse(text);
    }
    var m = text.match(/^[+¥]?\s*([\d,]+(?:\.\d+)?)\s*(k|m)?(?:\s*%|\s*（|$)/i);
    if (!m) return null;
    var n = parseFloat(m[1].replace(/,/g, ""));
    if (isNaN(n)) return null;
    var unit = (m[2] || "").toLowerCase();
    if (unit === "k") n *= 1000;
    if (unit === "m") n *= 1000000;
    return n;
  }

  function makePill(text, cls) {
    var span = document.createElement("span");
    span.className = "radar-pill caption-3 " + cls;
    span.textContent = text;
    return span;
  }

  function decorateCell(td, header) {
    var text = td.textContent.trim();
    if (!text) return;

    if (header === "⭐" || header === "总 Tokens") {
      td.classList.add("radar-num");
    } else if (header === "7日") {
      td.classList.add("radar-num");
      td.textContent = "";
      td.appendChild(makePill(text, "is-gain"));
    } else if (header === "花费 (¥)") {
      td.classList.add("radar-num");
      td.textContent = "";
      td.appendChild(makePill(text, "is-cost"));
    } else if (header === "分数") {
      td.classList.add("radar-num");
      var val = parseFloat(text);
      var cls = val >= 85 ? "is-score-high" : "is-score-mid";
      td.textContent = "";
      td.appendChild(makePill(text, cls));
    } else if (header === "形态" || header === "语言") {
      td.textContent = "";
      td.appendChild(makePill(text, "is-tag"));
    }
  }

  function enhanceTable(table) {
    if (table.closest(".radar-table-wrap")) return;

    var wrap = document.createElement("div");
    wrap.className = "radar-table-wrap";
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);

    var thead = table.querySelector("thead");
    var tbody = table.querySelector("tbody");
    if (!thead || !tbody) return;

    var headers = Array.prototype.map.call(thead.querySelectorAll("th"), function (th) {
      return th.textContent.trim();
    });
    var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));

    rows.forEach(function (tr) {
      var cells = tr.querySelectorAll("td");
      cells.forEach(function (td, idx) {
        var raw = td.textContent.trim();
        var numVal = parseNumericValue(raw);
        if (numVal !== null) {
          td.setAttribute("data-sort", String(numVal));
        } else {
          td.setAttribute("data-sort", raw.toLowerCase());
        }
        decorateCell(td, headers[idx] || "");
      });
    });

    if (rows.length > 1) {
      var ths = thead.querySelectorAll("th");
      var sortState = { idx: -1, dir: -1 };
      ths.forEach(function (th, idx) {
        var headerText = headers[idx] || "";
        if (headerText === "简介" || headerText === "状态") return;
        th.classList.add("is-sortable");
        var ind = document.createElement("span");
        ind.className = "radar-sort-ind";
        th.appendChild(ind);

        th.addEventListener("click", function () {
          var numericCol = rows.some(function (r) {
            var td = r.children[idx];
            return td && !isNaN(parseFloat(td.getAttribute("data-sort"))) &&
              /^-?\d+(\.\d+)?$/.test(td.getAttribute("data-sort"));
          });
          if (sortState.idx === idx) {
            sortState.dir *= -1;
          } else {
            sortState.idx = idx;
            sortState.dir = numericCol ? -1 : 1;
          }
          ths.forEach(function (h) {
            h.classList.remove("is-sorted");
            var s = h.querySelector(".radar-sort-ind");
            if (s) s.textContent = "";
          });
          th.classList.add("is-sorted");
          ind.textContent = sortState.dir === -1 ? "▼" : "▲";

          var sorted = rows.slice().sort(function (a, b) {
            var va = a.children[idx] ? a.children[idx].getAttribute("data-sort") : "";
            var vb = b.children[idx] ? b.children[idx].getAttribute("data-sort") : "";
            if (numericCol) {
              var na = parseFloat(va);
              var nb = parseFloat(vb);
              if (!isNaN(na) && !isNaN(nb)) return (na - nb) * sortState.dir;
            }
            return va.localeCompare(vb, "zh-Hans-CN") * sortState.dir;
          });
          sorted.forEach(function (r) { tbody.appendChild(r); });
        });
      });
    }

    var langIdx = headers.indexOf("语言");
    var isRepoTable = headers.indexOf("项目") !== -1 && headers.indexOf("简介") !== -1;
    if (!isRepoTable || rows.length < 4) return;

    var toolbar = document.createElement("div");
    toolbar.className = "radar-toolbar";

    var left = document.createElement("div");
    left.className = "radar-toolbar-left";

    var search = document.createElement("input");
    search.type = "search";
    search.className = "radar-search";
    search.placeholder = "搜索项目名、简介、分类或形态";
    search.setAttribute("aria-label", "搜索项目列表");
    left.appendChild(search);

    var langSelect = null;
    if (langIdx !== -1) {
      var langs = {};
      rows.forEach(function (r) {
        var val = r.children[langIdx] ? r.children[langIdx].textContent.trim() : "";
        if (val) langs[val] = (langs[val] || 0) + 1;
      });
      var langKeys = Object.keys(langs).sort(function (a, b) {
        return langs[b] - langs[a] || a.localeCompare(b);
      });
      if (langKeys.length > 1) {
        langSelect = document.createElement("select");
        langSelect.className = "radar-select";
        langSelect.setAttribute("aria-label", "按语言筛选");
        var allOpt = document.createElement("option");
        allOpt.value = "";
        allOpt.textContent = "全部语言 (" + rows.length + ")";
        langSelect.appendChild(allOpt);
        langKeys.forEach(function (lang) {
          var opt = document.createElement("option");
          opt.value = lang;
          opt.textContent = lang + " (" + langs[lang] + ")";
          langSelect.appendChild(opt);
        });
        left.appendChild(langSelect);
      }
    }

    var countEl = document.createElement("span");
    countEl.className = "radar-count caption-2 mono-num";
    countEl.textContent = "共 " + rows.length + " 项";

    toolbar.appendChild(left);
    toolbar.appendChild(countEl);
    wrap.parentNode.insertBefore(toolbar, wrap);

    var emptyState = document.createElement("div");
    emptyState.className = "radar-empty-state";
    emptyState.innerHTML =
      '<p class="title-3">未找到匹配的项目</p>' +
      '<p class="body-6">没有符合当前搜索词或语言条件的开源项目，你可以清空筛选重新查看。</p>' +
      '<button type="button" class="radar-btn button-sm">重置筛选条件</button>';
    wrap.parentNode.insertBefore(emptyState, wrap.nextSibling);

    var resetBtn = emptyState.querySelector("button");
    resetBtn.addEventListener("click", function () {
      search.value = "";
      if (langSelect) langSelect.value = "";
      applyFilter();
      search.focus();
    });

    var applyFilter = function () {
      var q = search.value.trim().toLowerCase();
      var lang = langSelect ? langSelect.value : "";
      var visible = 0;
      rows.forEach(function (r) {
        var textMatch = !q || r.textContent.toLowerCase().indexOf(q) !== -1;
        var cellLang = langIdx !== -1 && r.children[langIdx] ? r.children[langIdx].textContent.trim() : "";
        var langMatch = !lang || cellLang === lang;
        var show = textMatch && langMatch;
        r.style.display = show ? "" : "none";
        if (show) visible += 1;
      });
      countEl.textContent = visible === rows.length ? "共 " + rows.length + " 项" : "显示 " + visible + " / " + rows.length + " 项";
      wrap.style.display = visible === 0 ? "none" : "";
      emptyState.classList.toggle("is-visible", visible === 0);
    };

    search.addEventListener("input", applyFilter);
    if (langSelect) {
      langSelect.addEventListener("change", applyFilter);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initThemeToggle();
    initMobileMenu();
    initScrollReveals();
    initTaglineReveal();
    document.querySelectorAll(".radar-main table").forEach(enhanceTable);
  });
})();
