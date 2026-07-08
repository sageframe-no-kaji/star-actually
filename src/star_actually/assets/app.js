/* *, Actually — The Motion
 *
 * The one JS file. No framework, no build step. It owns:
 *   - the journey: every node visited, at what depth (sessionStorage)
 *   - the branch stack: lateral departures and one-keypress return
 *   - the keyboard map, shown live in the action bar
 *   - the rail: where you've been, where you are, how to get back
 *
 * If this file fails to load, the site degrades to its HTML floor:
 * every link is real, every fragment is a page. Nothing breaks.
 */

(function () {
  "use strict";

  var STORE = "star-actually-journey";

  /* ── journey state ─────────────────────────────────────────────── */

  function load() {
    try {
      var raw = sessionStorage.getItem(STORE);
      var state = raw ? JSON.parse(raw) : null;
      if (state && Array.isArray(state.path) && Array.isArray(state.branches)) return state;
    } catch (e) { /* corrupted or unavailable storage: start fresh */ }
    return { path: [], branches: [] };
  }

  function save(state) {
    try { sessionStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* private mode */ }
  }

  var journey = load();

  function current() {
    return journey.path[journey.path.length - 1] || null;
  }

  /* Record a visit. Dialing depth on the same node edits the visit;
     arriving somewhere new appends one. */
  function record(id, depth, title) {
    var here = current();
    if (here && here.id === id) {
      here.depth = depth;
    } else {
      journey.path.push({ id: id, depth: depth, title: title });
    }
    save(journey);
    renderRail();
  }

  /* ── reading the screen ────────────────────────────────────────── */

  function content() {
    return document.getElementById("content");
  }

  function nodeState() {
    var el = content();
    if (!el || !el.dataset.nodeId) return null;
    return {
      id: el.dataset.nodeId,
      depth: parseInt(el.dataset.depth, 10),
      max: parseInt(el.dataset.maxDepth, 10),
      title: el.dataset.title
    };
  }

  function firstLink(selector) {
    var el = content() || document;
    return el.querySelector(selector);
  }

  function navLinks() {
    var el = content();
    if (!el) return [];
    return Array.prototype.slice.call(el.querySelectorAll(".nav-forward, .nav-lateral"));
  }

  /* ── moving ────────────────────────────────────────────────────── */

  /* Counter, not boolean: rapid back-presses can have several suppressed
     swaps in flight at once, and each afterSwap must consume exactly one. */
  var suppressCount = 0;

  function swapTo(id, depth) {
    if (!window.htmx) { window.location.href = "/n/" + id + "/"; return; }
    htmx.ajax("GET", "/n/" + id + "/d" + depth + ".html", {
      target: "#content",
      swap: "outerHTML"
    }).then(function () {
      history.replaceState(null, "", "/n/" + id + "/");
    });
  }

  /* Go back along the journey, restoring the depth you left.
     Only a live node page may mutate the journey — on any other page
     (entry, help) the browser's own history is the right "back". */
  function goBack() {
    if (!nodeState()) { history.back(); return; }
    if (journey.path.length < 2) return;
    journey.path.pop();
    /* leaving a node also collapses any branch departures recorded past here */
    journey.branches = journey.branches.filter(function (b) {
      return b < journey.path.length - 1;
    });
    var target = current();
    save(journey);
    suppressCount++;
    swapTo(target.id, target.depth);
  }

  /* Follow the first onward link (or the root link on the entry screen). */
  function goOnward() {
    var link = firstLink(".nav-forward") || document.querySelector(".nav-root");
    if (link) link.click();
  }

  /* Lateral move = branch: pin where we are, then follow. */
  function goBranch() {
    var link = firstLink(".nav-lateral");
    if (!link) return;
    journey.branches.push(journey.path.length - 1);
    save(journey);
    link.click();
  }

  /* One-keypress return: pop the branch stack, truncate the detour,
     land on the departure node at the departure depth. */
  function goReturn() {
    if (!nodeState()) return; /* journeys only mutate on node pages */
    if (!journey.branches.length) return;
    var idx = journey.branches.pop();
    journey.path = journey.path.slice(0, idx + 1);
    var target = current();
    save(journey);
    if (!target) return;
    suppressCount++;
    swapTo(target.id, target.depth);
  }

  /* Rail click: recenter on a past node — truncate everything after it. */
  function goRailIndex(idx) {
    if (!nodeState()) return;
    if (idx < 0 || idx >= journey.path.length - 1) return;
    journey.path = journey.path.slice(0, idx + 1);
    journey.branches = journey.branches.filter(function (b) { return b < idx; });
    var target = current();
    save(journey);
    suppressCount++;
    swapTo(target.id, target.depth);
  }

  function dial(step) {
    var link = firstLink(step > 0 ? ".depth-deeper" : ".depth-shallower");
    if (link) link.click();
  }

  /* ── the rail ──────────────────────────────────────────────────── */

  var RAIL_SHOWN = 5;

  function renderRail() {
    var rail = document.getElementById("rail");
    if (!rail) return;
    rail.textContent = "";

    var path = journey.path;
    if (!path.length) return;

    var start = Math.max(0, path.length - RAIL_SHOWN);
    if (start > 0) {
      rail.appendChild(span("rail-node", "…"));
      rail.appendChild(span("rail-sep", "›"));
    }

    path.forEach(function (visit, i) {
      if (i < start) return;
      if (i > start) rail.appendChild(span("rail-sep", "›"));
      if (i === path.length - 1) {
        rail.appendChild(span("rail-here", "▶ " + visit.title + " @" + visit.depth));
      } else {
        var a = document.createElement("a");
        a.className = "rail-node";
        a.href = "/n/" + visit.id + "/";
        a.textContent = visit.title + " @" + visit.depth;
        a.addEventListener("click", function (ev) {
          ev.preventDefault();
          goRailIndex(i);
        });
        rail.appendChild(a);
      }
    });

    if (journey.branches.length) {
      var b = journey.branches[journey.branches.length - 1];
      var origin = path[b];
      if (origin) {
        var chip = span("rail-return", "↩ return to " + origin.title + " @" + origin.depth);
        rail.appendChild(chip);
      }
    } else if (path.length === 1) {
      /* First arrival: give the reader something to stand on. */
      rail.appendChild(span("rail-note", "  — the start of your path; it grows as you move"));
    }
  }

  function span(cls, text) {
    var el = document.createElement("span");
    el.className = cls;
    el.textContent = text;
    return el;
  }

  /* ── keyboard ──────────────────────────────────────────────────── */

  function inTextField(target) {
    return target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" ||
      target.isContentEditable);
  }

  document.addEventListener("keydown", function (ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;

    if (inTextField(ev.target)) {
      if (ev.key === "Escape") ev.target.blur();
      return; /* Enter submits, characters type; the keyboard layer stays out */
    }

    /* Enter on a focused link is a click — let the browser have it. */
    if (ev.key === "Enter" && document.activeElement &&
        document.activeElement.tagName === "A") return;

    switch (ev.key) {
      /* Depth is water: − dials down (deeper), + surfaces. Seed §7. */
      case "-": case "_": dial(1); break;
      case "+": case "=": dial(-1); break;
      case "ArrowDown": case "j": goOnward(); break;
      case "ArrowUp": case "k": goBack(); break;
      case "ArrowRight": case "l": goBranch(); break;
      case "Enter": goReturn(); break;
      case "/":
        if (window.location.pathname === "/") {
          var input = document.querySelector(".prompt-input");
          if (input) input.focus();
        } else {
          window.location.href = "/";
        }
        break;
      case "?": window.location.href = "/help.html"; break;
      default: {
        var n = parseInt(ev.key, 10);
        if (n >= 1 && n <= 9) {
          var links = navLinks();
          var link = links[n - 1];
          if (link) {
            if (link.classList.contains("nav-lateral")) {
              journey.branches.push(journey.path.length - 1);
              save(journey);
            }
            link.click();
          }
        }
        return; /* unhandled: don't preventDefault */
      }
    }
    ev.preventDefault();
  });

  /* ── wiring ────────────────────────────────────────────────────── */

  /* After every swap: record the visit (unless a back/return suppressed it). */
  document.body.addEventListener("htmx:afterSwap", function (ev) {
    if (ev.detail && ev.detail.target && ev.detail.target.id !== "content" &&
        !(ev.detail.target.closest && ev.detail.target.closest("#content"))) {
      /* a swap somewhere else (future features); the journey doesn't care */
    }
    var state = nodeState();
    if (!state) return;
    if (suppressCount > 0) {
      suppressCount--;
      renderRail();
      return;
    }
    record(state.id, state.depth, state.title);
  });

  /* Browser Back/Forward: htmx restores old DOM from its history cache;
     re-align the journey with whatever node is actually on screen. */
  function resyncToScreen() {
    var state = nodeState();
    if (!state) { renderRail(); return; }
    var here = current();
    if (here && here.id === state.id) {
      here.depth = state.depth;
    } else {
      var last = -1;
      for (var i = journey.path.length - 1; i >= 0; i--) {
        if (journey.path[i].id === state.id) { last = i; break; }
      }
      if (last >= 0) {
        journey.path = journey.path.slice(0, last + 1);
        journey.branches = journey.branches.filter(function (b) { return b < last; });
        journey.path[last].depth = state.depth;
      } else {
        journey.path.push({ id: state.id, depth: state.depth, title: state.title });
      }
    }
    save(journey);
    renderRail();
  }

  document.body.addEventListener("htmx:historyRestore", resyncToScreen);
  window.addEventListener("popstate", function () {
    /* htmx handles its own restores; this covers full-page history moves */
    setTimeout(resyncToScreen, 0);
  });

  /* Lateral link *clicks* (mouse) also branch. Keyboard paths push the
     branch marker themselves; this covers pointers. */
  document.body.addEventListener("htmx:beforeRequest", function (ev) {
    var src = ev.detail && ev.detail.elt;
    if (src && src.classList && src.classList.contains("nav-lateral")) {
      var last = journey.branches[journey.branches.length - 1];
      if (last !== journey.path.length - 1) {
        journey.branches.push(journey.path.length - 1);
        save(journey);
      }
    }
  });

  /* ── the question box (ho-06) ──────────────────────────────────── */

  function tokens(text) {
    return text.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
  }

  /* Catalog scoring: a title hit is a concept answer; entry phrases were
     written for exactly this; summaries are the long tail. */
  function scoreNode(node, qTokens) {
    var title = tokens(node.title);
    var entries = tokens(node.entry_points.join(" "));
    var summary = tokens(node.summary);
    var score = 0;
    qTokens.forEach(function (t) {
      if (title.indexOf(t) !== -1) score += 3;
      if (entries.indexOf(t) !== -1) score += 2;
      if (summary.indexOf(t) !== -1) score += 1;
    });
    return score;
  }

  function resultLink(href, title, note) {
    var a = document.createElement("a");
    a.href = href;
    a.textContent = title;
    if (note) {
      var s = span("result-summary", "  " + note);
      a.appendChild(s);
    }
    return a;
  }

  var searchSeq = 0; /* stale async results must never land in a newer query */

  function fullText(query, container, seq) {
    import("/pagefind/pagefind.js").then(function (pf) {
      return pf.search(query);
    }).then(function (res) {
      return Promise.all(res.results.slice(0, 5).map(function (r) { return r.data(); }));
    }).then(function (hits) {
      if (seq !== searchSeq) return; /* the reader has typed on */
      hits.forEach(function (d) {
        container.appendChild(resultLink(
          d.url.replace(/full\.html$/, ""), d.meta.title, "· full-text"));
      });
    }).catch(function () { /* no index built: catalog matching stands alone */ });
  }

  function initEntry() {
    var input = document.querySelector(".prompt-input");
    var results = document.getElementById("results");
    var form = document.getElementById("ask-form");
    if (!input || !results || !form) return;

    var catalog = [];
    fetch("/catalog.json").then(function (r) { return r.json(); })
      .then(function (data) { catalog = data.nodes; })
      .catch(function () { /* the ↓-to-begin path still works */ });

    input.addEventListener("input", function () {
      var qTokens = tokens(input.value);
      searchSeq++;
      results.textContent = "";
      if (!qTokens.length) return;
      var scored = catalog.map(function (n) { return { n: n, s: scoreNode(n, qTokens) }; })
        .filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, 5);
      scored.forEach(function (x) {
        results.appendChild(resultLink("/n/" + x.n.id + "/", x.n.title, x.n.summary));
      });
      if (scored.length < 3 && input.value.length > 3) {
        fullText(input.value, results, searchSeq);
      }
    });

    /* Enter: try the Receptionist first (same-origin /ask, short timeout);
       fall back to the top search result if it's absent, slow, or wrong. */
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var asking = span("result-summary", "asking the receptionist…");
      results.insertBefore(asking, results.firstChild);
      var fallback = function () {
        if (asking.parentNode) asking.parentNode.removeChild(asking);
        var first = results.querySelector("a");
        if (first) window.location.href = first.getAttribute("href");
      };
      var controller = new AbortController();
      var timer = setTimeout(function () { controller.abort(); }, 1500);
      fetch("/ask", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question: input.value }),
        signal: controller.signal
      }).then(function (r) {
        clearTimeout(timer);
        if (!r.ok) throw new Error("no receptionist");
        return r.json();
      }).then(function (a) {
        window.location.href = "/n/" + a.node_id + "/?d=" + a.depth;
      }).catch(fallback);
    });
  }

  /* Initial load of a node page: record the visit; honor ?d=N deep links. */
  document.addEventListener("DOMContentLoaded", function () {
    var state = nodeState();
    if (state) {
      var params = new URLSearchParams(window.location.search);
      var wanted = parseInt(params.get("d"), 10);
      record(state.id, state.depth, state.title);
      if (wanted && wanted !== state.depth && wanted >= 1 && wanted <= state.max) {
        swapTo(state.id, wanted);
      }
    }
    renderRail();
    initEntry();
  });
})();
