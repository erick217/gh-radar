(function () {
  "use strict";

  var THEME_KEY = "radar-theme";
  var THEMES = ["system", "light", "dark"];
  var THEME_LABELS = {
    system: "💻 跟随系统",
    light: "☀️ 浅色",
    dark: "🌙 深色",
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
    var actions = document.querySelector(".radar-nav-actions");
    if (!actions) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "radar-theme-btn";
    var updateLabel = function () {
      var cur = getTheme();
      btn.textContent = THEME_LABELS[cur];
      btn.title = "点击切换界面主题（跟随系统 / 浅色 / 深色）";
    };
    updateLabel();
    btn.addEventListener("click", function () {
      var cur = getTheme();
      var next = THEMES[(THEMES.indexOf(cur) + 1) % THEMES.length];
      applyTheme(next);
      updateLabel();
    });
    actions.prepend(btn);
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

    if (header === "⭐" || header === "调用次数" || header === "输入" || header === "输入 Tokens" ||
        header === "缓存命中" || header === "缓存未命中" || header === "总 Tokens" ||
        header === "输出 Tokens（思维链）" || header === "输出（思维链）") {
      td.classList.add("radar-num");
    } else if (header === "7日") {
      td.classList.add("radar-num");
      td.textContent = "";
      td.appendChild(makePill(text, "is-gain"));
    } else if (header === "花费 (¥)") {
      td.classList.add("radar-num");
      td.textContent = "";
      td.appendChild(makePill(text, "is-cost"));
    } else if (header === "命中率") {
      td.classList.add("radar-num");
      td.textContent = "";
      td.appendChild(makePill(text, "is-score-mid"));
    } else if (header === "分数") {
      td.classList.add("radar-num");
      var val = parseFloat(text);
      var cls = val >= 85 ? "is-score-high" : val >= 70 ? "is-score-mid" : "is-score-low";
      td.textContent = "";
      td.appendChild(makePill(text, cls));
    } else if (header === "形态" || header === "语言" || header === "模型") {
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

    // Enable click-to-sort on multi-row tables
    if (rows.length > 1) {
      var ths = thead.querySelectorAll("th");
      var sortState = { idx: -1, dir: -1 };
      ths.forEach(function (th, idx) {
        var headerText = headers[idx] || "";
        if (headerText === "简介" || headerText === "状态" || headerText === "说明") return;
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

    // Add search/filter toolbar for larger tables
    var langIdx = headers.indexOf("语言");
    var isRepoTable = headers.indexOf("项目") !== -1 && headers.indexOf("简介") !== -1;
    var isLargeTable = rows.length >= 4;
    if (!isLargeTable) return;

    var toolbar = document.createElement("div");
    toolbar.className = "radar-toolbar";

    var left = document.createElement("div");
    left.className = "radar-toolbar-left";

    var search = document.createElement("input");
    search.type = "search";
    search.className = "radar-search";
    search.placeholder = isRepoTable ? "🔍 搜索项目名、简介、分类或形态..." : "🔍 搜索项目、日期或模型...";
    left.appendChild(search);

    var langSelect = null;
    if (isRepoTable && langIdx !== -1) {
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
    countEl.className = "radar-count";
    countEl.textContent = "共 " + rows.length + " 条";

    toolbar.appendChild(left);
    toolbar.appendChild(countEl);
    wrap.parentNode.insertBefore(toolbar, wrap);

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
      countEl.textContent = visible === rows.length ? "共 " + rows.length + " 条" : "显示 " + visible + " / " + rows.length + " 条";
    };

    search.addEventListener("input", applyFilter);
    if (langSelect) {
      langSelect.addEventListener("change", applyFilter);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initThemeToggle();
    var tables = document.querySelectorAll(".markdown-body table");
    tables.forEach(enhanceTable);
  });
})();
