$(function() {
    var text = '';
    $("h3").each(function() {
      text +=  $(this).text() +　"<br>";
    });
    //alert(text);
    chrome.runtime.sendMessage({
      value: document.getElementsByClassName('prt-targeting-area main-tap-area')[0].textContent
    });
});
