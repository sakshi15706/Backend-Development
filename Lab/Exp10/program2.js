// Program 2: Task Manager using jQuery
$(document).ready(function () {

  var tasks = [
    { id: 1, title: "Finish Experiment 10", priority: "High", done: false },
    { id: 2, title: "Revise Node.js notes", priority: "Medium", done: true },
    { id: 3, title: "Push code to GitHub", priority: "Low", done: false }
  ];
  var nextId = 4;
  var currentFilter = "all";

  // ---------- Draw the list from the tasks array ----------
  function render() {
    var search = $("#searchBox").val().toLowerCase().trim();
    var $list = $("#taskList").empty();
    var shown = 0;

    $.each(tasks, function (i, t) {
      if (currentFilter === "pending" && t.done) { return; }          // skip (continue)
      if (currentFilter === "done" && !t.done) { return; }
      if (search && t.title.toLowerCase().indexOf(search) === -1) { return; }

      var $li = $("<li></li>")
        .attr("data-id", t.id)
        .toggleClass("done", t.done);
      $li.append($("<input type='checkbox' class='check'>").prop("checked", t.done));
      $li.append($("<span class='title'></span>").text(t.title));      // .text() keeps user text safe
      $li.append($("<span class='badge'></span>").addClass(t.priority).text(t.priority));
      $li.append("<button class='del' title='Delete'>&times;</button>");
      $list.append($li);
      shown++;
    });

    $("#emptyMsg").toggle(shown === 0);
    updateStats();
  }

  function updateStats() {
    var total = tasks.length;
    var done = $.grep(tasks, function (t) { return t.done; }).length;   // $.grep filters an array
    $("#statTotal").text(total);
    $("#statDone").text(done);
    $("#statPending").text(total - done);
    $("#progressBar").animate({ width: (total ? (done / total) * 100 : 0) + "%" }, 300);
  }

  // ---------- Add a task with validation ----------
  $("#taskForm").submit(function (e) {
    e.preventDefault();                                                // stop the page from reloading
    var title = $.trim($("#taskTitle").val());
    var priority = $("#taskPriority").val();
    var error = "";

    if (title.length < 3) { error = "Title must have at least 3 characters."; }
    else if (!priority) { error = "Please choose a priority."; }
    else if ($.grep(tasks, function (t) { return t.title.toLowerCase() === title.toLowerCase(); }).length) {
      error = "This task already exists.";
    }

    if (error) {
      $("#formError").text(error).hide().fadeIn(200);
      $("#taskTitle").addClass("invalid");
      return;
    }

    $("#formError").text("");
    $("#taskTitle").removeClass("invalid").val("");
    $("#taskPriority").val("");
    tasks.push({ id: nextId++, title: title, priority: priority, done: false });
    render();
    $("#taskList li:last").hide().slideDown(300);                      // new item slides in
  });

  $("#taskTitle").on("input", function () { $(this).removeClass("invalid"); $("#formError").text(""); });

  // ---------- Events on items that are created later (event delegation) ----------
  $("#taskList").on("change", ".check", function () {
    var id = $(this).closest("li").data("id");
    $.each(tasks, function (i, t) { if (t.id === id) { t.done = !t.done; } });
    render();
  });

  $("#taskList").on("click", ".del", function () {
    var $li = $(this).closest("li");
    var id = $li.data("id");
    $li.slideUp(250, function () {                                     // remove after the animation
      tasks = $.grep(tasks, function (t) { return t.id !== id; });
      render();
    });
  });

  // ---------- Filter buttons and search ----------
  $(".filter").click(function () {
    $(".filter").removeClass("active");
    $(this).addClass("active");
    currentFilter = $(this).data("filter");
    render();
  });
  $("#searchBox").on("keyup", render);

  $("#clearDone").click(function () {
    tasks = $.grep(tasks, function (t) { return !t.done; });
    render();
  });

  // ---------- Accordion ----------
  $(".acc-body").hide();
  $(".acc-head").click(function () {
    $(this).toggleClass("open").next(".acc-body").slideToggle(250);
    $(this).siblings(".acc-head").removeClass("open").next(".acc-body").slideUp(250);  // keep one open
  });

  // ---------- Tabs ----------
  $(".tab-btn").click(function () {
    $(".tab-btn").removeClass("active");
    $(this).addClass("active");
    $(".tab-panel").hide();
    $("#" + $(this).data("tab")).fadeIn(200);
  });

  // ---------- Character counter ----------
  $("#note").on("keyup", function () {
    var text = $(this).val();
    var words = $.trim(text) === "" ? 0 : $.trim(text).split(/\s+/).length;
    $("#charCount").text(text.length).css("color", text.length >= 90 ? "#c0392b" : "");
    $("#wordCount").text(words);
  });

  render();
});
