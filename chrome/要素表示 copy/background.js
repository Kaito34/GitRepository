
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
{
  console.log(`敵HP: ${request.enemy_hp}`);
  console.log(`キャラ1HP: ${request.hp1}`);
  console.log(`キャラ2HP: ${request.hp2}`);
  console.log(`キャラ3HP: ${request.hp3}`);
  console.log(`キャラ4HP: ${request.hp4}`);
  //retrun が非同期の場合は欲しい
  $(function(){
    $.ajax({
        url: 'recieve.py',
        type: 'post',
        data: '送信メッセージ'
    }).done(function(data){
        console.log(data);
        });
    }).fail(function(){
        console.log('failed');
    });

  return true;
});
