
function sendMessage(e) {
  chrome.runtime.sendMessage({
      enemy_hp: document.getElementById('enemy-hp0').textContent,
      hp1 : document.getElementsByClassName("txt-hp-value")[0].textContent,
      hp2 : document.getElementsByClassName("txt-hp-value")[1].textContent,
      hp3 : document.getElementsByClassName("txt-hp-value")[2].textContent,
      hp4 : document.getElementsByClassName("txt-hp-value")[3].textContent
  });

}
//passive event listner にして稼働を早くする
document.addEventListener('touchstart', function() {}, {passive: true});

//参加者人数は取得したいが、秒速から計ることにする。データを取得して統計的に分析


//ボタン、クリック検知

var classElement = document.getElementsByClassName("btn-sub-category btn-sub-beginnercomic")[0];
classElement.addEventListener("mouseover", sendMessage);
window.addEventListener("click", sendMessage);
