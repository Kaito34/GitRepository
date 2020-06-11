
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
{
  console.clear()
  console.log(`${request.enemy_hp}  ${request.hp1}  ${request.hp2}  ${request.hp3}  ${request.hp4}`);
  //return が非同期の場合は欲しい
  return true;
});
