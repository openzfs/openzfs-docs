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

    var count = document.createElement("span");
    count.className = "zfs-param-count";

    host.appendChild(caption);
    host.appendChild(select);
    host.appendChild(count);

    function apply(value) {
      var shown = 0;
      params.forEach(function (node) {
        var visible = value === ALL || node.classList.contains(value);
        node.classList.toggle("zfs-param-hidden", !visible);
        if (visible) {
          shown += 1;
        }
      });
      // parameter sections are counted twice: once in the tag index, once
      // in the parameter list itself
      var total = document.querySelectorAll("section.zfs-param").length;
      var visibleSections = document.querySelectorAll(
        "section.zfs-param:not(.zfs-param-hidden)"
      ).length;
      count.textContent =
        value === ALL
          ? total + " parameters"
          : visibleSections + " of " + total + " parameters";
      try {
        window.localStorage.setItem(STORAGE_KEY, value);
      } catch (err) {
        /* private mode, nothing to do */
      }
    }

    select.addEventListener("change", function () {
      apply(select.value);
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
    apply(stored);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
