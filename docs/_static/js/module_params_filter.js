/*
 * Version filter for the generated "Module Parameters" page.
 *
 * Every parameter section carries the classes "zfs-param v-2-3 v-master ..."
 * listing the OpenZFS versions it exists in. Picking a version hides the
 * parameters that version does not have; "All versions" shows everything,
 * which is what you want when searching the page with Ctrl+F.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "zfs-param-version";
  var ALL = "all";

  function versionsOf(node) {
    var found = [];
    node.classList.forEach(function (name) {
      if (name.indexOf("v-") === 0) {
        found.push(name);
      }
    });
    return found;
  }

  function normalize(text) {
    return text.trim().toLowerCase().replace(/-/g, "_");
  }

  function nameOf(node) {
    if (node.dataset.zfsName === undefined) {
      // sections carry the name as their id, tag index entries as their text
      node.dataset.zfsName = normalize(
        node.tagName === "SECTION" ? node.id : node.textContent
      );
    }
    return node.dataset.zfsName;
  }

  function label(cls) {
    var name = cls.slice(2).replace(/-/g, ".");
    return name === "master" ? "master" : "OpenZFS " + name;
  }

  function sortKey(cls) {
    if (cls === "v-master") {
      return [Infinity];
    }
    return cls.slice(2).split("-").map(Number);
  }

  function compare(a, b) {
    var x = sortKey(a);
    var y = sortKey(b);
    for (var i = 0; i < Math.max(x.length, y.length); i++) {
      var diff = (x[i] || 0) - (y[i] || 0);
      if (diff) {
        return diff;
      }
    }
    return 0;
  }

  function build() {
    var host = document.getElementById("zfs-param-filter");
    var params = document.querySelectorAll(".zfs-param");
    if (!host || !params.length) {
      return;
    }

    var seen = {};
    params.forEach(function (node) {
      versionsOf(node).forEach(function (cls) {
        seen[cls] = true;
      });
    });
    var versions = Object.keys(seen).sort(compare).reverse();

    var select = document.createElement("select");
    select.id = "zfs-param-version";
    var options = [[ALL, "All versions"]].concat(
      versions.map(function (cls) {
        return [cls, label(cls)];
      })
    );
    options.forEach(function (pair) {
      var option = document.createElement("option");
      option.value = pair[0];
      option.textContent = pair[1];
      select.appendChild(option);
    });

    var caption = document.createElement("label");
    caption.htmlFor = select.id;
    caption.textContent = "Show parameters of ";

    var search = document.createElement("input");
    search.id = "zfs-param-search";
    search.type = "search";
    search.placeholder = "arc_max";
    search.autocomplete = "off";
    search.spellcheck = false;

    var searchCaption = document.createElement("label");
    searchCaption.htmlFor = search.id;
    searchCaption.textContent = " whose name contains ";

    var count = document.createElement("span");
    count.className = "zfs-param-count";

    host.appendChild(caption);
    host.appendChild(select);
    host.appendChild(searchCaption);
    host.appendChild(search);
    host.appendChild(count);

    var total = document.querySelectorAll("section.zfs-param").length;
    var tags = document.querySelectorAll("section.zfs-tag");

    function apply() {
      var value = select.value;
      // "-" and "_" are interchangeable: the names use "_", the anchors "-"
      var query = normalize(search.value);
      var shown = 0;

      params.forEach(function (node) {
        var visible =
          (value === ALL || node.classList.contains(value)) &&
          (!query || nameOf(node).indexOf(query) !== -1);
        node.classList.toggle("zfs-param-hidden", !visible);
        if (visible && node.tagName === "SECTION") {
          shown += 1;
        }
      });

      // a tag with nothing left under it is just a stray heading
      tags.forEach(function (node) {
        var empty = !node.querySelector("li.zfs-param:not(.zfs-param-hidden)");
        node.classList.toggle("zfs-param-hidden", empty);
      });

      count.textContent =
        value === ALL && !query
          ? total + " parameters"
          : shown + " of " + total + " parameters";
      try {
        window.localStorage.setItem(STORAGE_KEY, value);
      } catch (err) {
        /* private mode, nothing to do */
      }
    }

    select.addEventListener("change", apply);
    search.addEventListener("input", apply);
    search.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        search.value = "";
        apply();
      }
    });

    var stored = ALL;
    try {
      stored = window.localStorage.getItem(STORAGE_KEY) || ALL;
    } catch (err) {
      /* private mode, nothing to do */
    }
    if (stored !== ALL && !seen[stored]) {
      stored = ALL;
    }
    select.value = stored;
    apply();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
