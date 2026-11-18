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

  function resolveEffectiveTone(mode) {
    if (mode === "light" || mode === "dark") return mode;
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
      return "light";
    }
    return "dark";
  }

  function applyTheme(mode) {
    var html = document.documentElement;
    if (mode === "light" || mode === "dark") {
      html.setAttribute("data-theme", mode);
    } else {
      html.removeAttribute("data-theme");
    }
    html.dataset.tone = resolveEffectiveTone(mode);
    try {
      if (mode === "system") {
        localStorage.removeItem(THEME_KEY);
      } else {
        localStorage.setItem(THEME_KEY, mode);
      }
    } catch (e) {}
    if (window.tasteBackgrounds && typeof window.tasteBackgrounds.detect === "function") {
      window.tasteBackgrounds.detect();
    }
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

    if (window.matchMedia) {
      window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", function () {
        if (getTheme() === "system") {
          applyTheme("system");
        }
      });
    }
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
    span.className = "radar-pill " + cls;
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
    if (table.dataset.radarEnhanced === "1") return;
    table.dataset.radarEnhanced = "1";

    var wrap = table.closest(".radar-table-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.className = "radar-table-wrap";
      table.parentNode.insertBefore(wrap, table);
      wrap.appendChild(table);
    }

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

    var catIdx = headers.indexOf("分类");
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

    var catSelect = null;
    if (catIdx !== -1) {
      var cats = {};
      rows.forEach(function (r) {
        var val = r.children[catIdx] ? r.children[catIdx].textContent.trim() : "";
        var topCat = val.split("/")[0].trim();
        if (topCat) cats[topCat] = (cats[topCat] || 0) + 1;
      });
      var catKeys = Object.keys(cats).sort(function (a, b) {
        return cats[b] - cats[a] || a.localeCompare(b, "zh-Hans-CN");
      });
      if (catKeys.length > 1) {
        catSelect = document.createElement("select");
        catSelect.className = "radar-select";
        catSelect.setAttribute("aria-label", "按分类筛选");
        var allCatOpt = document.createElement("option");
        allCatOpt.value = "";
        allCatOpt.textContent = "全部分类 (" + rows.length + ")";
        catSelect.appendChild(allCatOpt);
        catKeys.forEach(function (c) {
          var opt = document.createElement("option");
          opt.value = c;
          opt.textContent = c + " (" + cats[c] + ")";
          catSelect.appendChild(opt);
        });
        left.appendChild(catSelect);
      }
    }

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
    countEl.className = "radar-count mono-num";
    countEl.textContent = "共 " + rows.length + " 项";

    toolbar.appendChild(left);
    toolbar.appendChild(countEl);
    wrap.parentNode.insertBefore(toolbar, wrap);

    var emptyState = document.createElement("div");
    emptyState.className = "radar-empty-state";
    emptyState.innerHTML =
      '<p class="t-card">未找到匹配的项目</p>' +
      '<p class="t-body">没有符合当前搜索词、分类或语言条件的开源项目，可以清空筛选重新查看。</p>' +
      '<button type="button" class="btn btn--secondary btn--sm">重置筛选条件</button>';
    wrap.parentNode.insertBefore(emptyState, wrap.nextSibling);

    var resetBtn = emptyState.querySelector("button");
    resetBtn.addEventListener("click", function () {
      search.value = "";
      if (catSelect) catSelect.value = "";
      if (langSelect) langSelect.value = "";
      applyFilter();
      search.focus();
    });

    var applyFilter = function () {
      var q = search.value.trim().toLowerCase();
      var cat = catSelect ? catSelect.value : "";
      var lang = langSelect ? langSelect.value : "";
      var visible = 0;
      rows.forEach(function (r) {
        var textMatch = !q || r.textContent.toLowerCase().indexOf(q) !== -1;
        var cellCat = catIdx !== -1 && r.children[catIdx] ? r.children[catIdx].textContent.trim().split("/")[0].trim() : "";
        var catMatch = !cat || cellCat === cat;
        var cellLang = langIdx !== -1 && r.children[langIdx] ? r.children[langIdx].textContent.trim() : "";
        var langMatch = !lang || cellLang === lang;
        var show = textMatch && catMatch && langMatch;
        r.style.display = show ? "" : "none";
        if (show) visible += 1;
      });
      countEl.textContent = visible === rows.length ? "共 " + rows.length + " 项" : "显示 " + visible + " / " + rows.length + " 项";
      wrap.style.display = visible === 0 ? "none" : "";
      emptyState.classList.toggle("is-visible", visible === 0);
    };

    search.addEventListener("input", applyFilter);
    if (catSelect) {
      catSelect.addEventListener("change", applyFilter);
    }
    if (langSelect) {
      langSelect.addEventListener("change", applyFilter);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initThemeToggle();
    document.querySelectorAll("main table").forEach(enhanceTable);
  });
})();
