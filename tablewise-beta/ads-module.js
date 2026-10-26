'use strict';
let adFilter='All';
function adFeed(){return window.TABLEWISE_ADS||{updated:'',sources:[],deals:[]}}
function activeDeals(){const today=new Date().toISOString().slice(0,10);return (adFeed().deals||[]).filter(d=>d.validThrough>=today&&d.seenAt<=today&&S.stores.includes(d.store)&&(!d.zip||d.zip===S.zip)&&(!d.region||d.region==='Michigan'))}
// Ad prices are provisional and only substitute *exact matching* ingredient/unit
// prices, for the beta ZIP, after checking dates. User-edited prices win.
function adPriceOffer(key,store){
 if(store!=='ALDI'||S.zip!=='48864'||typeof S.prices[key]?.ALDI==='number')return null;
 const unit=def(key)[2];
 return activeDeals().find(d=>d.store===store&&d.mapping===key&&d.unit===unit&&Number.isFinite(d.price)&&d.price>0)||null;
}
// ZIP-to-state hints only. Each ZIP must still be checked on Kroger.com
// because many markets have separate subregion/store editions.
function krogerZipState(zip){
 const n=Number(String(zip||'').slice(0,3));
 if(!Number.isInteger(n)||String(zip||'').length!==5)return '';
 if(n>=480&&n<=499)return 'MI';
 if(n>=430&&n<=459)return 'OH';
 if(n>=460&&n<=479)return 'IN';
 if(n>=370&&n<=385)return 'TN';
 if(n>=300&&n<=319)return 'GA';
 if((n>=750&&n<=799)||(n>=733&&n<=749)||(n>=885&&n<=885))return 'TX';
 return '';
}
function krogerRegionalUi(store){
 const today=new Date().toISOString().slice(0,10);
 const flyers=(store.flyers||[]).filter(f=>f.validFrom<=today&&f.validThrough>=today&&f.region);
 const regions=[...new Set(flyers.map(f=>f.region))].sort();
 const suggestion=krogerZipState(S.zip);
 const chosen=S.krogerRegion&&S.krogerRegion!=='auto'?S.krogerRegion:suggestion;
 const displayed=flyers.filter(f=>!chosen||f.region===chosen);
 const selected=displayed.length?displayed:flyers;
 return `<div class="kroger-region-tools"><label>Kroger weekly ad region <select id="kroger-region-select" aria-label="Kroger regional weekly ads"><option value="auto" ${S.krogerRegion==='auto'?'selected':''}>Auto from ZIP (${esc(suggestion||'all available')})</option><option value="ALL" ${S.krogerRegion==='ALL'?'selected':''}>All available editions</option>${regions.map(st=>`<option value="${st}" ${S.krogerRegion===st?'selected':''}>${st}</option>`).join('')}</select></label><p class="ad-meta">ZIP ${esc(S.zip)} ${suggestion?'suggests '+esc(suggestion):'has no matching edition in our supported list'}. Regional editions are NOT verified prices for your exact store; use WeeklyAds2 ZIP lookup or Kroger checkout to confirm.</p>${selected.length?`<div class="kroger-flyer-grid">${selected.map((f,index)=>`<a class="kroger-flyer-link ${suggestion===f.region?'match':''}" href="${esc(f.url)}" target="_blank" rel="noopener noreferrer"><b>${esc(f.region)} ${f.zipHint?'· example ZIP '+esc(f.zipHint):'· statewide edition'}${index>0?' · '+(index+1):''}</b><span>${esc(f.validFrom)} – ${esc(f.validThrough)}</span><small>View current Kroger flyer ↗</small></a>`).join('')}</div>`:`<p class="ad-note">No confirmed current-week flyer editions available. Use the publisher's regional ZIP selector to locate the current ad.</p>`}<p class="ad-meta"><a href="${esc(store.url)}" target="_blank" rel="noopener noreferrer">See every selectable region / enter ZIP on WeeklyAds2 ↗</a></p></div>`;
}
function adsView(){const feed=adFeed(),list=activeDeals().filter(d=>adFilter==='All'||adFilter===d.store);const local=S.zip==='48864';const note=local?'Store locations are configured for ZIP 48864.':'The configured store addresses are for Okemos, MI (48864), not your ZIP. Select your own store at the retailer. ALDI ad prices are never assumed locally verified.';
return `${pageHead('YOUR LOCAL WEEKLY SPECIALS','This week’s grocery ads','Browse current flyers, track advertised offers and bring sale finds into your shopping plan.',`<button data-act="settings" class="btn btn-soft">⌖ &nbsp; ZIP ${esc(S.zip)}</button>`)}
<div class="ad-intro"><div><strong>Deals from the stores you actually shop.</strong><p>${note} Ads may contain digital-coupon restrictions or minimum package sizes. ALDI prices come from an independent site, not ALDI. Store-level prices may differ. The Meijer and Kroger regional flyers are discovery sources, not ZIP-specific price feeds. Scheduled metadata checks run only when the source permits access.</p></div><span class="ad-status">Feed checked: ${esc(feed.updated||'Not yet')}</span></div>
<div class="ad-store-grid">${(feed.sources||[]).filter(x=>S.stores.includes(x.store)).map(st=>`<div class="ad-store-card"><div class="ad-deal-top"><h3>${esc(st.store)}</h3><span class="ad-status">${st.status==='third-party-priced-offers'?'Independent prices':st.status==='no-current-dated-ad'?'No current ad':'Flyer available'}</span></div><small>${esc(local?st.address:st.name)}</small><p class="ad-note">${esc(st.detail)}</p><a class="btn btn-soft" href="${esc(st.url)}" target="_blank" rel="noopener noreferrer">Open ${esc(st.store)} weekly ad ↗</a>${st.officialUrl?`<p><a class="ad-inline-link" href="${esc(st.officialUrl)}" target="_blank" rel="noopener noreferrer">Check local ${esc(st.store)} prices ↗</a></p>`:''}${st.store==='Kroger'?krogerRegionalUi(st):(st.flyers||[]).filter(f=>f.validFrom<=new Date().toISOString().slice(0,10)&&f.validThrough>=new Date().toISOString().slice(0,10)).map(f=>`<p class="ad-meta"><a class="ad-inline-link" href="${esc(f.url)}" target="_blank" rel="noopener noreferrer">${esc(f.title)} ↗</a> · ends ${esc(f.validThrough)} · regional, not ZIP-verified</p>`).join('')}</div>`).join('')}</div>
<div class="section-heading"><div><span class="kicker">AD-SOURCED OFFER BOARD</span><h2>Items spotted in weekly ads</h2><p>Listings are time-limited and require confirmation for your exact store. Exact matched ALDI ingredient prices provisionally replace samples while the ad is current; unverified for local stores. Any price you edit always takes priority.</p></div></div>
<div class="ad-filter">${['All',...S.stores].map(st=>`<button class="${adFilter===st?'active':''}" data-act="ad-filter" data-id="${st}">${esc(st)}</button>`).join('')}</div>
${list.length?`<div class="ad-deals">${list.map(d=>`<div class="ad-deal"><div class="ad-deal-top"><span class="ad-status">${esc(d.store)}</span><span class="ad-meta">Through ${esc(d.validThrough)}</span></div><strong>${esc(d.name)}</strong><div><span class="ad-deal-price">${money(d.price)}</span><span class="ad-meta"> / ${esc(d.unit)}</span></div><p class="ad-meta">${esc(d.scope)} ${d.packageNote?`· ${esc(d.packageNote)}`:''}</p><a class="ad-inline-link" href="${esc(d.source)}" target="_blank" rel="noopener noreferrer">View source ↗</a><button data-act="ad-add" data-id="${esc(d.id)}">Add to shopping list +</button></div>`).join('')}</div>`:`<div class="ad-empty">No non-expired priced deals for this filter yet. The original weekly-ad links above still work. We will not carry last week’s expired deals into a new shopping plan.</div>`}
<div class="bottom-banner"><div class="bottom-emoji">💡</div><div><strong>Found a sale that our parser missed?</strong><p>Add that offer to your shopping list from the ad, then update its price. Your cart comparison will immediately recalculate.</p></div><button class="btn btn-outline" data-act="add-item">Add grocery item +</button></div>
<p class="disclaimer">Availability and pricing can change by store. A link to a weekly flyer is not proof that a particular item has an extractable local price. Never assume coupons are automatically applied.</p>`}
