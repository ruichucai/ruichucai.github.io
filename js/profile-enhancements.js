/* Progressive enhancements for the academic profile. No framework or external dependency. */
(function () {
  "use strict";
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }
  ready(function () {
    var isZh = document.documentElement.lang.toLowerCase().indexOf("zh") === 0 ||
      location.pathname.indexOf("/zh-cn") === 0;
    var labels = isZh
      ? {search:"搜索论文（标题、作者、期刊或会议）", year:"全部年份", category:"全部研究方向", count:"篇论文", empty:"没有找到匹配的论文。", clear:"清除筛选", more:"展开全部新闻", less:"收起较早新闻"}
      : {search:"Search publications by title, author, venue…", year:"All years", category:"All research areas", count:"publications", empty:"No publications match your filters.", clear:"Clear filters", more:"Show all news", less:"Show fewer news"};
    var publicationRoot = document.querySelector(".publication-list");
    if (publicationRoot) {
      var entries = [];
      var activeCategory = isZh ? "其他" : "Other";
      Array.prototype.forEach.call(publicationRoot.children, function (node) {
        if (node.tagName === "FONT") {
          var heading = node.textContent.trim();
          if (heading) activeCategory = heading;
        } else if (node.tagName === "UL") {
          Array.prototype.forEach.call(node.querySelectorAll(":scope > li"), function (li) {
            var text = li.textContent.replace(/\s+/g, " ").trim();
            var years = text.match(/20\d{2}/g) || [];
            var year = years.length ? years[years.length - 1] : "";
            li.dataset.publicationCategory = activeCategory;
            li.dataset.publicationYear = year;
            entries.push({node:li, text:text.toLowerCase(), category:activeCategory, year:year});
          });
        }
      });
      if (entries.length) {
        var toolbar = document.createElement("div");
        toolbar.className = "publication-toolbar";
        toolbar.setAttribute("role", "search");
        var search = document.createElement("input");
        search.type = "search";
        search.className = "publication-search";
        search.placeholder = labels.search;
        search.setAttribute("aria-label", labels.search);
        var year = document.createElement("select");
        year.className = "publication-filter";
        year.setAttribute("aria-label", labels.year);
        var yearDefault = document.createElement("option");
        yearDefault.value = ""; yearDefault.textContent = labels.year; year.appendChild(yearDefault);
        Array.from(new Set(entries.map(function (e) { return e.year; }).filter(Boolean))).sort().reverse().forEach(function (value) {
          var option = document.createElement("option"); option.value = value; option.textContent = value; year.appendChild(option);
        });
        var category = document.createElement("select");
        category.className = "publication-filter";
        category.setAttribute("aria-label", labels.category);
        var categoryDefault = document.createElement("option");
        categoryDefault.value = ""; categoryDefault.textContent = labels.category; category.appendChild(categoryDefault);
        Array.from(new Set(entries.map(function (e) { return e.category; }))).forEach(function (value) {
          var option = document.createElement("option"); option.value = value; option.textContent = value; category.appendChild(option);
        });
        var status = document.createElement("p");
        status.className = "publication-count";
        status.setAttribute("aria-live", "polite");
        var clear = document.createElement("button");
        clear.type = "button"; clear.className = "publication-clear"; clear.textContent = labels.clear;
        toolbar.append(search, year, category, clear, status);
        publicationRoot.insertBefore(toolbar, publicationRoot.firstChild);
        function applyFilters() {
          var query = search.value.trim().toLowerCase(), selectedYear = year.value, selectedCategory = category.value, shown = 0;
          entries.forEach(function (entry) {
            var visible = (!query || entry.text.indexOf(query) !== -1) &&
              (!selectedYear || entry.year === selectedYear) &&
              (!selectedCategory || entry.category === selectedCategory);
            entry.node.hidden = !visible;
            if (visible) shown++;
          });
          status.textContent = shown + " / " + entries.length + " " + labels.count;
          var oldEmpty = publicationRoot.querySelector(".publication-empty");
          if (!shown && !oldEmpty) {
            oldEmpty = document.createElement("p"); oldEmpty.className = "publication-empty"; oldEmpty.textContent = labels.empty; publicationRoot.appendChild(oldEmpty);
          } else if (shown && oldEmpty) oldEmpty.remove();
          Array.prototype.forEach.call(publicationRoot.children, function (node) {
            if (node.tagName === "UL") {
              var hasVisible = !!node.querySelector("li:not([hidden])");
              node.hidden = !hasVisible;
              var heading = node.previousElementSibling;
              if (heading && heading.tagName === "FONT") heading.hidden = !hasVisible;
            }
          });
        }
        search.addEventListener("input", applyFilters);
        year.addEventListener("change", applyFilters);
        category.addEventListener("change", applyFilters);
        clear.addEventListener("click", function () { search.value = ""; year.value = ""; category.value = ""; applyFilters(); search.focus(); });
        applyFilters();
      }
    }

    var newsHeading = document.getElementById("news");
    var newsList = newsHeading && newsHeading.nextElementSibling;
    if (newsList && newsList.tagName === "UL" && newsList.children.length > 8) {
      newsList.classList.add("news-list");
      var newsItems = Array.prototype.slice.call(newsList.children);
      var newsButton = document.createElement("button");
      newsButton.type = "button"; newsButton.className = "news-toggle";
      var expanded = false;
      function updateNews() {
        newsItems.forEach(function (item, index) { item.hidden = !expanded && index >= 8; });
        newsButton.textContent = expanded ? labels.less : labels.more + " (" + newsItems.length + ")";
        newsButton.setAttribute("aria-expanded", String(expanded));
      }
      newsButton.addEventListener("click", function () { expanded = !expanded; updateNews(); });
      newsList.insertAdjacentElement("afterend", newsButton);
      updateNews();
    }

    ["selected-projects", "open-source-projects"].forEach(function (id) {
      var heading = document.getElementById(id);
      var list = heading && heading.nextElementSibling;
      if (list && list.tagName === "UL") {
        list.classList.add(id === "open-source-projects" ? "project-grid" : "project-list");
        Array.prototype.forEach.call(list.children, function (item) { item.classList.add("project-item"); });
      }
    });
  });
})();
