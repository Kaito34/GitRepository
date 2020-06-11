var textContents = '';
chrome.runtime.onMessage.addListener(
  function (request){
    textContents = request.value;
    console.log(textContents)
    return true
  }
);
