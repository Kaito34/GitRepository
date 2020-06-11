chrome.runtime.onMessage.addListener(function(msg, sender, sendResponse) {
	var result = "<ul>";
	var el_titles = document.querySelectorAll("#ires .g .r a");

	for(var i = 0; i < el_titles.length; i++){
		result += "<li>" + el_titles[i].innerHTML + "</li>";
	}

	result += "</ul>";
	sendResponse(result);
});