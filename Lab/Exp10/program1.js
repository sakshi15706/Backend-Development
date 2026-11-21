// Program 1: jQuery basics
// $(document).ready() runs the code after the page (DOM) is loaded.
$(document).ready(function () {

  // ---------- 1. SELECTORS ----------
  function mark(selection, label) {
    $("#fruitList li").removeClass("picked");
    selection.addClass("picked");                       // highlight the selected elements
    $("#selOut").text(label + "  ->  " + selection.length + " element(s) selected: [" +
      selection.map(function () { return $(this).text(); }).get().join(", ") + "]");
  }
  $("#selTag").click(function () { mark($("li.fruit"), 'tag selector $("li")'); });
  $("#selClass").click(function () { mark($(".special"), 'class selector $(".special")'); });
  $("#selFirst").click(function () { mark($("#fruitList li:first"), "$('li:first')"); });
  $("#selOdd").click(function () { mark($("#fruitList li:odd"), "$('li:odd')  (index 1, 3...)"); });
  $("#selChild").click(function () { mark($("#fruitList li:last-child"), "$('li:last-child')"); });
  $("#selReset").click(function () {
    $("#fruitList li").removeClass("picked");
    $("#selOut").text("Click a button");
  });

  // ---------- 2. EFFECTS ----------
  $("#eHide").click(function () { $("#effectBox").hide(500); });
  $("#eShow").click(function () { $("#effectBox").show(500); });
  $("#eToggle").click(function () { $("#effectBox").toggle(500); });
  $("#eFadeOut").click(function () { $("#effectBox").fadeOut(800); });
  $("#eFadeIn").click(function () { $("#effectBox").fadeIn(800); });
  $("#eFadeTo").click(function () { $("#effectBox").fadeTo(800, 0.3); });
  $("#eSlideUp").click(function () { $("#effectBox").slideUp(600); });
  $("#eSlideDown").click(function () { $("#effectBox").slideDown(600); });
  $("#eSlideToggle").click(function () { $("#effectBox").slideToggle(600); });

  // ---------- 3. ANIMATE ----------
  $("#aMove").click(function () { $("#ball").animate({ left: "250px" }, 1000); });
  $("#aGrow").click(function () { $("#ball").animate({ width: "80px", height: "80px", opacity: 0.6 }, 800); });
  $("#aBack").click(function () {
    $("#ball").animate({ left: "0px", width: "40px", height: "40px", opacity: 1 }, 800);
  });
  $("#aChain").click(function () {
    $("#ball")
      .animate({ left: "250px" }, 700)           // animations in a chain run one after another
      .animate({ top: "30px" }, 400)
      .animate({ left: "0px" }, 700)
      .animate({ top: "0px" }, 400);
  });
  $("#aStop").click(function () { $("#ball").stop(true); });

  // ---------- 4. CONTENT, CSS, ATTRIBUTES ----------
  $("#cText").click(function () { $("#contentOut").text("text(): " + $("#demoPara").text()); });
  $("#cHtml").click(function () { $("#contentOut").text("html(): " + $("#demoPara").html()); });
  $("#cVal").click(function () { $("#contentOut").text("val(): " + $("#demoInput").val()); });
  $("#cSetText").click(function () { $("#demoPara").text("New <b>plain</b> text set with text()"); });
  $("#cSetHtml").click(function () { $("#demoPara").html("New <b>bold</b> text set with html()"); });
  $("#cCss").click(function () {
    $("#demoPara").css({ color: "#c0392b", "font-size": "20px" });
    $("#contentOut").text("css('color'): " + $("#demoPara").css("color"));
  });
  $("#cClass").click(function () { $("#demoPara").toggleClass("highlight"); });
  $("#cAttr").click(function () {
    $("#demoInput").attr("title", "Set by jQuery").attr("placeholder", "attr() changed me");
    $("#contentOut").text("attr('title'): " + $("#demoInput").attr("title"));
  });

  // ---------- 5. ADD AND REMOVE ELEMENTS ----------
  var count = 3;
  $("#dAppend").click(function () { $("#itemList").append("<li>Appended item " + count++ + "</li>"); });
  $("#dPrepend").click(function () { $("#itemList").prepend("<li>Prepended item " + count++ + "</li>"); });
  $("#dAfter").click(function () { $("#itemList li:first").after("<li>Inserted after first</li>"); });
  $("#dRemoveLast").click(function () { $("#itemList li:last").remove(); });
  $("#dEmpty").click(function () { $("#itemList").empty(); });
  $("#dClone").click(function () { $("#itemList li:first").clone().appendTo("#itemList"); });

  // ---------- 6. EVENTS ----------
  function log(text) { $("#eventOut").text(text); }
  $("#eventBox")
    .click(function () { log("click"); })
    .dblclick(function () { $(this).toggleClass("highlight"); log("dblclick (toggled colour)"); })
    .mouseenter(function () { $(this).css("background", "#cfe8ff"); log("mouseenter"); })
    .mouseleave(function () { $(this).css("background", ""); log("mouseleave"); })
    .mousemove(function (e) { log("mousemove  x=" + e.offsetX + "  y=" + e.offsetY); });

  $("#keyInput").keyup(function () { log("keyup  value = '" + $(this).val() + "'  (" + $(this).val().length + " characters)"); });
  $("#colorSelect").change(function () {
    $("body").css("background", $(this).val() || "");
    log("change  value = " + ($(this).val() || "none"));
  });

  // on() can attach several events, and works for elements added later when delegated
  $("#itemList").on("click", "li", function () {
    $(this).toggleClass("picked");
  });

  // ---------- 7. TRAVERSING ----------
  function showTrav(selection, label) {
    $("#parentList li, #family, #parentList").removeClass("picked");
    selection.addClass("picked");
    $("#travOut").text(label + "  ->  " + selection.length + " element(s)");
  }
  $("#tParent").click(function () { showTrav($("#middle").parent(), "$('#middle').parent()  (the <ul>)"); });
  $("#tChildren").click(function () { showTrav($("#parentList").children(), "$('#parentList').children()"); });
  $("#tSiblings").click(function () { showTrav($("#middle").siblings(), "$('#middle').siblings()"); });
  $("#tNext").click(function () { showTrav($("#middle").next(), "$('#middle').next()"); });
  $("#tPrev").click(function () { showTrav($("#middle").prev(), "$('#middle').prev()"); });
  $("#tNextAll").click(function () { showTrav($("#middle").nextAll(), "$('#middle').nextAll()"); });
  $("#tFilter").click(function () { showTrav($("#parentList li").eq(0), "$('li').eq(0)  (first item)"); });
  $("#tEach").click(function () {
    var names = [];
    $("#parentList li").each(function (index, element) {
      names.push(index + ": " + $(element).text());
    });
    $("#travOut").text("each():\n" + names.join("\n"));
  });

  // ---------- 8. CHAINING ----------
  $("#chainBtn").click(function () {
    $("#chainBox").css("background", "#ffe08a").slideUp(500).slideDown(500).text("Chain finished!");
  });

});
