document.addEventListener("DOMContentLoaded", function() {
	document.getElementById("ChromePlugin-doScrape").addEventListener("click", function(){

		chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {},
            function(msg) {
              document.getElementById("ChromePlugin-result-disp").innerHTML = msg;
            });
        });

	});
});
