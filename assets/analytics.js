/* Cloudflare Web Analytics (手動導入)。localStorage でこのブラウザのみ計測除外。 */
(function(){
  'use strict';
  const key='rapasai_analytics_opt_out';
  const params=new URLSearchParams(window.location.search);
  const command=params.get('analytics');
  try {
    if(command==='off') localStorage.setItem(key,'1');
    if(command==='on') localStorage.removeItem(key);
    if(localStorage.getItem(key)==='1') return;
  } catch(e) { /* ストレージが無効なら通常計測 */ }
  const beacon=document.createElement('script');
  beacon.type='module';
  beacon.src='https://static.cloudflareinsights.com/beacon.min.js';
  beacon.setAttribute('data-cf-beacon',JSON.stringify({token:'7bbb5ce7daba4a44895c1ac5dedeef5d'}));
  document.head.appendChild(beacon);
})();
