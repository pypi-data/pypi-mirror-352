export const __webpack_ids__=["9656"];export const __webpack_modules__={76499:function(t,e,a){a.a(t,(async function(t,i){try{a.d(e,{WB:()=>h,p6:()=>c});var o=a(57900),r=a(28105),s=a(1066),n=a(36641),l=t([o,n]);[o,n]=l.then?(await l)():l;(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"long",month:"long",day:"numeric",timeZone:(0,n.f)(t.time_zone,e)})));const c=(t,e,a)=>d(e,a.time_zone).format(t),d=(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"long",day:"numeric",timeZone:(0,n.f)(t.time_zone,e)}))),h=((0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"short",day:"numeric",timeZone:(0,n.f)(t.time_zone,e)}))),(t,e,a)=>{const i=u(e,a.time_zone);if(e.date_format===s.t6.language||e.date_format===s.t6.system)return i.format(t);const o=i.formatToParts(t),r=o.find((t=>"literal"===t.type))?.value,n=o.find((t=>"day"===t.type))?.value,l=o.find((t=>"month"===t.type))?.value,c=o.find((t=>"year"===t.type))?.value,d=o.at(o.length-1);let h="literal"===d?.type?d?.value:"";"bg"===e.language&&e.date_format===s.t6.YMD&&(h="");return{[s.t6.DMY]:`${n}${r}${l}${r}${c}${h}`,[s.t6.MDY]:`${l}${r}${n}${r}${c}${h}`,[s.t6.YMD]:`${c}${r}${l}${r}${n}${h}`}[e.date_format]}),u=(0,r.Z)(((t,e)=>{const a=t.date_format===s.t6.system?void 0:t.language;return t.date_format===s.t6.language||(t.date_format,s.t6.system),new Intl.DateTimeFormat(a,{year:"numeric",month:"numeric",day:"numeric",timeZone:(0,n.f)(t.time_zone,e)})}));(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{day:"numeric",month:"short",timeZone:(0,n.f)(t.time_zone,e)}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{month:"long",year:"numeric",timeZone:(0,n.f)(t.time_zone,e)}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{month:"long",timeZone:(0,n.f)(t.time_zone,e)}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",timeZone:(0,n.f)(t.time_zone,e)}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"long",timeZone:(0,n.f)(t.time_zone,e)}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"short",timeZone:(0,n.f)(t.time_zone,e)})));i()}catch(c){i(c)}}))},40678:function(t,e,a){a.a(t,(async function(t,i){try{a.d(e,{o0:()=>h});var o=a(57900),r=a(28105),s=a(76499),n=a(9131),l=a(36641),c=a(13819),d=t([o,s,n,l]);[o,s,n,l]=d.then?(await d)():d;const h=(t,e,a)=>u(e,a.time_zone).format(t),u=(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.y)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.y)(t)?"h12":"h23",timeZone:(0,l.f)(t.time_zone,e)})));(0,r.Z)((()=>new Intl.DateTimeFormat(void 0,{year:"numeric",month:"long",day:"numeric",hour:"2-digit",minute:"2-digit"}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"short",day:"numeric",hour:(0,c.y)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.y)(t)?"h12":"h23",timeZone:(0,l.f)(t.time_zone,e)}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{month:"short",day:"numeric",hour:(0,c.y)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.y)(t)?"h12":"h23",timeZone:(0,l.f)(t.time_zone,e)}))),(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.y)(t)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,c.y)(t)?"h12":"h23",timeZone:(0,l.f)(t.time_zone,e)})));i()}catch(h){i(h)}}))},9131:function(t,e,a){a.a(t,(async function(t,i){try{a.d(e,{Vu:()=>h,Zs:()=>_,mr:()=>c,xO:()=>m});var o=a(57900),r=a(28105),s=a(36641),n=a(13819),l=t([o,s]);[o,s]=l.then?(await l)():l;const c=(t,e,a)=>d(e,a.time_zone).format(t),d=(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,n.y)(t)?"h12":"h23",timeZone:(0,s.f)(t.time_zone,e)}))),h=(t,e,a)=>u(e,a.time_zone).format(t),u=(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{hour:(0,n.y)(t)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,n.y)(t)?"h12":"h23",timeZone:(0,s.f)(t.time_zone,e)}))),m=(t,e,a)=>p(e,a.time_zone).format(t),p=(0,r.Z)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"long",hour:(0,n.y)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,n.y)(t)?"h12":"h23",timeZone:(0,s.f)(t.time_zone,e)}))),_=(t,e,a)=>g(e,a.time_zone).format(t),g=(0,r.Z)(((t,e)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,s.f)(t.time_zone,e)})));i()}catch(c){i(c)}}))},36641:function(t,e,a){a.a(t,(async function(t,i){try{a.d(e,{f:()=>c});var o=a(57900),r=a(1066),s=t([o]);o=(s.then?(await s)():s)[0];const n=Intl.DateTimeFormat?.().resolvedOptions?.().timeZone,l=n??"UTC",c=(t,e)=>t===r.c_.local&&n?l:e;i()}catch(n){i(n)}}))},13819:function(t,e,a){a.d(e,{y:()=>r});var i=a(28105),o=a(1066);const r=(0,i.Z)((t=>{if(t.time_format===o.zt.language||t.time_format===o.zt.system){const e=t.time_format===o.zt.language?t.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(e).includes("10")}return t.time_format===o.zt.am_pm}))},94594:function(t,e,a){a.d(e,{F:()=>i});const i=async t=>{if(!t.parentNode)throw new Error("Cannot setup Leaflet map on disconnected element");const e=(await Promise.resolve().then(a.t.bind(a,25975,23))).default;e.Icon.Default.imagePath="/static/images/leaflet/images/",await a.e("150").then(a.t.bind(a,63295,23));const i=e.map(t),r=document.createElement("link");r.setAttribute("href","/static/images/leaflet/leaflet.css"),r.setAttribute("rel","stylesheet"),t.parentNode.appendChild(r);const s=document.createElement("link");s.setAttribute("href","/static/images/leaflet/MarkerCluster.css"),s.setAttribute("rel","stylesheet"),t.parentNode.appendChild(s),i.setView([52.3731339,4.8903147],13);return[i,e,o(e).addTo(i)]},o=t=>t.tileLayer("https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}"+(t.Browser.retina?"@2x.png":".png"),{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>',subdomains:"abcd",minZoom:0,maxZoom:20})},31298:function(t,e,a){a.d(e,{C:()=>o});var i=a(93318);const o=t=>{return e=t.entity_id,void 0===(a=t.attributes).friendly_name?(0,i.p)(e).replace(/_/g," "):(a.friendly_name??"").toString();var e,a}},26966:function(t,e,a){a.d(e,{k:()=>o});var i=a(25975);class o extends i.Marker{onAdd(t){return super.onAdd(t),this.decorationLayer?.addTo(t),this}onRemove(t){return this.decorationLayer?.remove(),super.onRemove(t)}constructor(t,e,a){super(t,a),this.decorationLayer=e}}},91337:function(t,e,a){var i=a(73742),o=a(59048),r=a(7616),s=a(69342),n=a(29740);a(22543),a(32986);const l={boolean:()=>a.e("4852").then(a.bind(a,60751)),constant:()=>a.e("177").then(a.bind(a,85184)),float:()=>a.e("2369").then(a.bind(a,94980)),grid:()=>a.e("9219").then(a.bind(a,79998)),expandable:()=>a.e("4020").then(a.bind(a,71781)),integer:()=>a.e("3703").then(a.bind(a,12960)),multi_select:()=>Promise.all([a.e("4458"),a.e("514")]).then(a.bind(a,79298)),positive_time_period_dict:()=>a.e("2010").then(a.bind(a,49058)),select:()=>a.e("3162").then(a.bind(a,64324)),string:()=>a.e("2529").then(a.bind(a,72609)),optional_actions:()=>a.e("1601").then(a.bind(a,67552))},c=(t,e)=>t?!e.name||e.flatten?t:t[e.name]:null;class d extends o.oi{getFormProperties(){return{}}async focus(){await this.updateComplete;const t=this.renderRoot.querySelector(".root");if(t)for(const e of t.children)if("HA-ALERT"!==e.tagName){e instanceof o.fl&&await e.updateComplete,e.focus();break}}willUpdate(t){t.has("schema")&&this.schema&&this.schema.forEach((t=>{"selector"in t||l[t.type]?.()}))}render(){return o.dy`
      <div class="root" part="root">
        ${this.error&&this.error.base?o.dy`
              <ha-alert alert-type="error">
                ${this._computeError(this.error.base,this.schema)}
              </ha-alert>
            `:""}
        ${this.schema.map((t=>{const e=((t,e)=>t&&e.name?t[e.name]:null)(this.error,t),a=((t,e)=>t&&e.name?t[e.name]:null)(this.warning,t);return o.dy`
            ${e?o.dy`
                  <ha-alert own-margin alert-type="error">
                    ${this._computeError(e,t)}
                  </ha-alert>
                `:a?o.dy`
                    <ha-alert own-margin alert-type="warning">
                      ${this._computeWarning(a,t)}
                    </ha-alert>
                  `:""}
            ${"selector"in t?o.dy`<ha-selector
                  .schema=${t}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .name=${t.name}
                  .selector=${t.selector}
                  .value=${c(this.data,t)}
                  .label=${this._computeLabel(t,this.data)}
                  .disabled=${t.disabled||this.disabled||!1}
                  .placeholder=${t.required?"":t.default}
                  .helper=${this._computeHelper(t)}
                  .localizeValue=${this.localizeValue}
                  .required=${t.required||!1}
                  .context=${this._generateContext(t)}
                ></ha-selector>`:(0,s.h)(this.fieldElementName(t.type),{schema:t,data:c(this.data,t),label:this._computeLabel(t,this.data),helper:this._computeHelper(t),disabled:this.disabled||t.disabled||!1,hass:this.hass,localize:this.hass?.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(t),...this.getFormProperties()})}
          `}))}
      </div>
    `}fieldElementName(t){return`ha-form-${t}`}_generateContext(t){if(!t.context)return;const e={};for(const[a,i]of Object.entries(t.context))e[a]=this.data[i];return e}createRenderRoot(){const t=super.createRenderRoot();return this.addValueChangedListener(t),t}addValueChangedListener(t){t.addEventListener("value-changed",(t=>{t.stopPropagation();const e=t.target.schema;if(t.target===this)return;const a=!e.name||"flatten"in e&&e.flatten?t.detail.value:{[e.name]:t.detail.value};this.data={...this.data,...a},(0,n.B)(this,"value-changed",{value:this.data})}))}_computeLabel(t,e){return this.computeLabel?this.computeLabel(t,e):t?t.name:""}_computeHelper(t){return this.computeHelper?this.computeHelper(t):""}_computeError(t,e){return Array.isArray(t)?o.dy`<ul>
        ${t.map((t=>o.dy`<li>
              ${this.computeError?this.computeError(t,e):t}
            </li>`))}
      </ul>`:this.computeError?this.computeError(t,e):t}_computeWarning(t,e){return this.computeWarning?this.computeWarning(t,e):t}constructor(...t){super(...t),this.narrow=!1,this.disabled=!1}}d.styles=o.iv`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `,(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.Cb)({type:Boolean})],d.prototype,"narrow",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"data",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"schema",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"error",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"warning",void 0),(0,i.__decorate)([(0,r.Cb)({type:Boolean})],d.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"computeError",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"computeWarning",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"computeLabel",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"computeHelper",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"localizeValue",void 0),d=(0,i.__decorate)([(0,r.Mo)("ha-form")],d)},4830:function(t,e,a){a.a(t,(async function(t,i){try{a.r(e),a.d(e,{HaLocationSelector:()=>h});var o=a(73742),r=a(59048),s=a(7616),n=a(28105),l=a(29740),c=a(39107),d=(a(91337),t([c]));c=(d.then?(await d)():d)[0];class h extends r.oi{willUpdate(){this.value||(this.value={latitude:this.hass.config.latitude,longitude:this.hass.config.longitude,radius:this.selector.location?.radius?1e3:void 0})}render(){return r.dy`
      <p>${this.label?this.label:""}</p>
      <ha-locations-editor
        class="flex"
        .hass=${this.hass}
        .helper=${this.helper}
        .locations=${this._location(this.selector,this.value)}
        @location-updated=${this._locationChanged}
        @radius-updated=${this._radiusChanged}
        pin-on-click
      ></ha-locations-editor>
      <ha-form
        .hass=${this.hass}
        .schema=${this._schema(this.hass.localize,this.selector.location?.radius,this.selector.location?.radius_readonly)}
        .data=${this.value}
        .computeLabel=${this._computeLabel}
        .disabled=${this.disabled}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}_locationChanged(t){const[e,a]=t.detail.location;(0,l.B)(this,"value-changed",{value:{...this.value,latitude:e,longitude:a}})}_radiusChanged(t){const e=Math.round(t.detail.radius);(0,l.B)(this,"value-changed",{value:{...this.value,radius:e}})}_valueChanged(t){t.stopPropagation();const e=t.detail.value,a=Math.round(t.detail.value.radius);(0,l.B)(this,"value-changed",{value:{latitude:e.latitude,longitude:e.longitude,...this.selector.location?.radius&&!this.selector.location?.radius_readonly?{radius:a}:{}}})}constructor(...t){super(...t),this.disabled=!1,this._schema=(0,n.Z)(((t,e,a)=>[{name:"",type:"grid",schema:[{name:"latitude",required:!0,selector:{number:{step:"any",unit_of_measurement:"°"}}},{name:"longitude",required:!0,selector:{number:{step:"any",unit_of_measurement:"°"}}}]},...e?[{name:"radius",required:!0,default:1e3,disabled:!!a,selector:{number:{min:0,step:1,mode:"box",unit_of_measurement:t("ui.components.selectors.location.radius_meters")}}}]:[]])),this._location=(0,n.Z)(((t,e)=>{const a=getComputedStyle(this),i=t.location?.radius?a.getPropertyValue("--zone-radius-color")||a.getPropertyValue("--accent-color"):void 0;return[{id:"location",latitude:!e||isNaN(e.latitude)?this.hass.config.latitude:e.latitude,longitude:!e||isNaN(e.longitude)?this.hass.config.longitude:e.longitude,radius:t.location?.radius?e?.radius||1e3:void 0,radius_color:i,icon:t.location?.icon||t.location?.radius?"mdi:map-marker-radius":"mdi:map-marker",location_editable:!0,radius_editable:!!t.location?.radius&&!t.location?.radius_readonly}]})),this._computeLabel=t=>t.name?this.hass.localize(`ui.components.selectors.location.${t.name}`):""}}h.styles=r.iv`
    ha-locations-editor {
      display: block;
      height: 400px;
      margin-bottom: 16px;
    }
    p {
      margin-top: 0;
    }
  `,(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"selector",void 0),(0,o.__decorate)([(0,s.Cb)({type:Object})],h.prototype,"value",void 0),(0,o.__decorate)([(0,s.Cb)()],h.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)()],h.prototype,"helper",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,reflect:!0})],h.prototype,"disabled",void 0),h=(0,o.__decorate)([(0,s.Mo)("ha-selector-location")],h),i()}catch(h){i(h)}}))},27882:function(t,e,a){a.a(t,(async function(t,e){try{var i=a(73742),o=a(59048),r=a(7616),s=a(12790),n=a(18088),l=a(54974),c=(a(40830),t([l]));l=(c.then?(await c)():c)[0];class d extends o.oi{render(){const t=this.icon||this.stateObj&&this.hass?.entities[this.stateObj.entity_id]?.icon||this.stateObj?.attributes.icon;if(t)return o.dy`<ha-icon .icon=${t}></ha-icon>`;if(!this.stateObj)return o.Ld;if(!this.hass)return this._renderFallback();const e=(0,l.gD)(this.hass,this.stateObj,this.stateValue).then((t=>t?o.dy`<ha-icon .icon=${t}></ha-icon>`:this._renderFallback()));return o.dy`${(0,s.C)(e)}`}_renderFallback(){const t=(0,n.N)(this.stateObj);return o.dy`
      <ha-svg-icon
        .path=${l.Ls[t]||l.Rb}
      ></ha-svg-icon>
    `}}(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"stateObj",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"stateValue",void 0),(0,i.__decorate)([(0,r.Cb)()],d.prototype,"icon",void 0),d=(0,i.__decorate)([(0,r.Mo)("ha-state-icon")],d),e()}catch(d){e(d)}}))},77395:function(t,e,a){a.a(t,(async function(t,e){try{var i=a(73742),o=a(59048),r=a(7616),s=a(20480),n=a(29740),l=a(27882),c=t([l]);l=(c.then?(await c)():c)[0];class d extends o.oi{render(){return o.dy`
      <div
        class="marker ${this.entityPicture?"picture":""}"
        style=${(0,s.V)({"border-color":this.entityColor})}
        @click=${this._badgeTap}
      >
        ${this.entityPicture?o.dy`<div
              class="entity-picture"
              style=${(0,s.V)({"background-image":`url(${this.entityPicture})`})}
            ></div>`:this.showIcon&&this.entityId?o.dy`<ha-state-icon
                .hass=${this.hass}
                .stateObj=${this.hass?.states[this.entityId]}
              ></ha-state-icon>`:this.entityName}
      </div>
    `}_badgeTap(t){t.stopPropagation(),this.entityId&&(0,n.B)(this,"hass-more-info",{entityId:this.entityId})}constructor(...t){super(...t),this.showIcon=!1}}d.styles=o.iv`
    .marker {
      display: flex;
      justify-content: center;
      text-align: center;
      align-items: center;
      box-sizing: border-box;
      width: 48px;
      height: 48px;
      font-size: var(--ha-marker-font-size, var(--ha-font-size-xl));
      border-radius: var(--ha-marker-border-radius, 50%);
      border: 1px solid var(--ha-marker-color, var(--primary-color));
      color: var(--primary-text-color);
      background-color: var(--card-background-color);
    }
    .marker.picture {
      overflow: hidden;
    }
    .entity-picture {
      background-size: cover;
      height: 100%;
      width: 100%;
    }
  `,(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:"entity-id",reflect:!0})],d.prototype,"entityId",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:"entity-name"})],d.prototype,"entityName",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:"entity-picture"})],d.prototype,"entityPicture",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:"entity-color"})],d.prototype,"entityColor",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:"show-icon",type:Boolean})],d.prototype,"showIcon",void 0),customElements.define("ha-entity-marker",d),e()}catch(d){e(d)}}))},39107:function(t,e,a){a.a(t,(async function(t,e){try{var i=a(73742),o=a(59048),r=a(7616),s=a(28105),n=a(29740),l=(a(42592),a(67146)),c=t([l]);l=(c.then?(await c)():c)[0];class d extends o.oi{fitMap(t){this.map.fitMap(t)}fitBounds(t,e){this.map.fitBounds(t,e)}async fitMarker(t,e){if(this.Leaflet||await this._loadPromise,!this.map.leafletMap||!this._locationMarkers)return;const a=this._locationMarkers[t];if(a)if("getBounds"in a)this.map.leafletMap.fitBounds(a.getBounds()),a.bringToFront();else{const i=this._circles[t];i?this.map.leafletMap.fitBounds(i.getBounds()):this.map.leafletMap.setView(a.getLatLng(),e?.zoom||this.zoom)}}render(){return o.dy`
      <ha-map
        .hass=${this.hass}
        .layers=${this._getLayers(this._circles,this._locationMarkers)}
        .zoom=${this.zoom}
        .autoFit=${this.autoFit}
        .themeMode=${this.themeMode}
        .clickable=${this.pinOnClick}
        @map-clicked=${this._mapClicked}
      ></ha-map>
      ${this.helper?o.dy`<ha-input-helper-text>${this.helper}</ha-input-helper-text>`:""}
    `}willUpdate(t){super.willUpdate(t),this.Leaflet&&t.has("locations")&&this._updateMarkers()}updated(t){if(this.Leaflet&&t.has("locations")){const e=t.get("locations"),a=this.locations?.filter(((t,a)=>!e[a]||(t.latitude!==e[a].latitude||t.longitude!==e[a].longitude)&&this.map.leafletMap?.getBounds().contains({lat:e[a].latitude,lng:e[a].longitude})&&!this.map.leafletMap?.getBounds().contains({lat:t.latitude,lng:t.longitude})));1===a?.length&&this.map.leafletMap?.panTo({lat:a[0].latitude,lng:a[0].longitude})}}_normalizeLongitude(t){return Math.abs(t)>180?(t%360+540)%360-180:t}_updateLocation(t){const e=t.target,a=e.getLatLng(),i=[a.lat,this._normalizeLongitude(a.lng)];(0,n.B)(this,"location-updated",{id:e.id,location:i},{bubbles:!1})}_updateRadius(t){const e=t.target,a=this._locationMarkers[e.id];(0,n.B)(this,"radius-updated",{id:e.id,radius:a.getRadius()},{bubbles:!1})}_markerClicked(t){const e=t.target;(0,n.B)(this,"marker-clicked",{id:e.id},{bubbles:!1})}_mapClicked(t){if(this.pinOnClick&&this._locationMarkers){const e=Object.keys(this._locationMarkers)[0],a=[t.detail.location[0],this._normalizeLongitude(t.detail.location[1])];(0,n.B)(this,"location-updated",{id:e,location:a},{bubbles:!1}),a[1]!==t.detail.location[1]&&this.map.leafletMap?.panTo({lat:a[0],lng:a[1]})}}_updateMarkers(){if(!this.locations||!this.locations.length)return this._circles={},void(this._locationMarkers=void 0);const t={},e={},a=getComputedStyle(this).getPropertyValue("--accent-color");this.locations.forEach((i=>{let o;if(i.icon||i.iconPath){const t=document.createElement("div");let e;t.className="named-icon",void 0!==i.name&&(t.innerText=i.name),i.icon?(e=document.createElement("ha-icon"),e.setAttribute("icon",i.icon)):(e=document.createElement("ha-svg-icon"),e.setAttribute("path",i.iconPath)),t.prepend(e),o=this.Leaflet.divIcon({html:t.outerHTML,iconSize:[24,24],className:"light"})}if(i.radius){const r=this.Leaflet.circle([i.latitude,i.longitude],{color:i.radius_color||a,radius:i.radius});i.radius_editable||i.location_editable?(r.editing.enable(),r.addEventListener("add",(()=>{const t=r.editing._moveMarker,e=r.editing._resizeMarkers[0];o&&t.setIcon(o),e.id=t.id=i.id,t.addEventListener("dragend",(t=>this._updateLocation(t))).addEventListener("click",(t=>this._markerClicked(t))),i.radius_editable?e.addEventListener("dragend",(t=>this._updateRadius(t))):e.remove()})),t[i.id]=r):e[i.id]=r}if(!i.radius||!i.radius_editable&&!i.location_editable){const e={title:i.name,draggable:i.location_editable};o&&(e.icon=o);const a=this.Leaflet.marker([i.latitude,i.longitude],e).addEventListener("dragend",(t=>this._updateLocation(t))).addEventListener("click",(t=>this._markerClicked(t)));a.id=i.id,t[i.id]=a}})),this._circles=e,this._locationMarkers=t,(0,n.B)(this,"markers-updated")}constructor(){super(),this.autoFit=!1,this.zoom=16,this.themeMode="auto",this.pinOnClick=!1,this._circles={},this._getLayers=(0,s.Z)(((t,e)=>{const a=[];return Array.prototype.push.apply(a,Object.values(t)),e&&Array.prototype.push.apply(a,Object.values(e)),a})),this._loadPromise=Promise.resolve().then(a.t.bind(a,25975,23)).then((t=>a.e("9701").then(a.t.bind(a,99857,23)).then((()=>(this.Leaflet=t.default,this._updateMarkers(),this.updateComplete.then((()=>this.fitMap())))))))}}d.styles=o.iv`
    ha-map {
      display: block;
      height: 100%;
    }
  `,(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],d.prototype,"locations",void 0),(0,i.__decorate)([(0,r.Cb)()],d.prototype,"helper",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:"auto-fit",type:Boolean})],d.prototype,"autoFit",void 0),(0,i.__decorate)([(0,r.Cb)({type:Number})],d.prototype,"zoom",void 0),(0,i.__decorate)([(0,r.Cb)({attribute:"theme-mode",type:String})],d.prototype,"themeMode",void 0),(0,i.__decorate)([(0,r.Cb)({type:Boolean,attribute:"pin-on-click"})],d.prototype,"pinOnClick",void 0),(0,i.__decorate)([(0,r.SB)()],d.prototype,"_locationMarkers",void 0),(0,i.__decorate)([(0,r.SB)()],d.prototype,"_circles",void 0),(0,i.__decorate)([(0,r.IO)("ha-map",!0)],d.prototype,"map",void 0),d=(0,i.__decorate)([(0,r.Mo)("ha-locations-editor")],d),e()}catch(d){e(d)}}))},67146:function(t,e,a){a.a(t,(async function(t,e){try{var i=a(73742),o=a(5870),r=a(59048),s=a(7616),n=a(29740),l=a(40678),c=a(9131),d=a(94594),h=a(18088),u=a(31298),m=a(78001),p=(a(78645),a(77395)),_=a(26966),g=t([p,l,c]);[p,l,c]=g.then?(await g)():g;const y=t=>"string"==typeof t?t:t.entity_id;class f extends r.fl{connectedCallback(){super.connectedCallback(),this._loadMap(),this._attachObserver()}disconnectedCallback(){super.disconnectedCallback(),this.leafletMap&&(this.leafletMap.remove(),this.leafletMap=void 0,this.Leaflet=void 0),this._loaded=!1,this._resizeObserver&&this._resizeObserver.unobserve(this)}update(t){if(super.update(t),!this._loaded)return;let e=!1;const a=t.get("hass");if(t.has("_loaded")||t.has("entities"))this._drawEntities(),e=!0;else if(this._loaded&&a&&this.entities)for(const i of this.entities)if(a.states[y(i)]!==this.hass.states[y(i)]){this._drawEntities(),e=!0;break}t.has("clusterMarkers")&&this._drawEntities(),(t.has("_loaded")||t.has("paths"))&&this._drawPaths(),(t.has("_loaded")||t.has("layers"))&&(this._drawLayers(t.get("layers")),e=!0),(t.has("_loaded")||this.autoFit&&e)&&this.fitMap(),t.has("zoom")&&this.leafletMap.setZoom(this.zoom),(t.has("themeMode")||t.has("hass")&&(!a||a.themes?.darkMode!==this.hass.themes?.darkMode))&&this._updateMapStyle()}get _darkMode(){return"dark"===this.themeMode||"auto"===this.themeMode&&Boolean(this.hass.themes.darkMode)}_updateMapStyle(){const t=this.renderRoot.querySelector("#map");t.classList.toggle("clickable",this.clickable),t.classList.toggle("dark",this._darkMode),t.classList.toggle("forced-dark","dark"===this.themeMode),t.classList.toggle("forced-light","light"===this.themeMode)}async _loadMap(){if(this._loading)return;let t=this.shadowRoot.getElementById("map");t||(t=document.createElement("div"),t.id="map",this.shadowRoot.append(t)),this._loading=!0;try{[this.leafletMap,this.Leaflet]=await(0,d.F)(t),this._updateMapStyle(),this.leafletMap.on("click",(t=>{0===this._clickCount&&setTimeout((()=>{1===this._clickCount&&(0,n.B)(this,"map-clicked",{location:[t.latlng.lat,t.latlng.lng]}),this._clickCount=0}),250),this._clickCount++})),this._loaded=!0}finally{this._loading=!1}}fitMap(t){if(!this.leafletMap||!this.Leaflet||!this.hass)return;if(!this._mapFocusItems.length&&!this._mapFocusZones.length&&!this.layers?.length)return void this.leafletMap.setView(new this.Leaflet.LatLng(this.hass.config.latitude,this.hass.config.longitude),t?.zoom||this.zoom);let e=this.Leaflet.latLngBounds(this._mapFocusItems?this._mapFocusItems.map((t=>t.getLatLng())):[]);this._mapFocusZones?.forEach((t=>{e.extend("getBounds"in t?t.getBounds():t.getLatLng())})),this.layers?.forEach((t=>{e.extend("getBounds"in t?t.getBounds():t.getLatLng())})),e=e.pad(t?.pad??.5),this.leafletMap.fitBounds(e,{maxZoom:t?.zoom||this.zoom})}fitBounds(t,e){if(!this.leafletMap||!this.Leaflet||!this.hass)return;const a=this.Leaflet.latLngBounds(t).pad(e?.pad??.5);this.leafletMap.fitBounds(a,{maxZoom:e?.zoom||this.zoom})}_drawLayers(t){if(t&&t.forEach((t=>t.remove())),!this.layers)return;const e=this.leafletMap;this.layers.forEach((t=>{e.addLayer(t)}))}_computePathTooltip(t,e){let a;return a=t.fullDatetime?(0,l.o0)(e.timestamp,this.hass.locale,this.hass.config):(0,o.z)(e.timestamp)?(0,c.Vu)(e.timestamp,this.hass.locale,this.hass.config):(0,c.xO)(e.timestamp,this.hass.locale,this.hass.config),`${t.name}<br>${a}`}_drawPaths(){const t=this.hass,e=this.leafletMap,a=this.Leaflet;if(!t||!e||!a)return;if(this._mapPaths.length&&(this._mapPaths.forEach((t=>t.remove())),this._mapPaths=[]),!this.paths)return;const i=getComputedStyle(this).getPropertyValue("--dark-primary-color");this.paths.forEach((t=>{let o,r;t.gradualOpacity&&(o=t.gradualOpacity/(t.points.length-2),r=1-t.gradualOpacity);for(let e=0;e<t.points.length-1;e++){const s=t.gradualOpacity?r+e*o:void 0;this._mapPaths.push(a.circleMarker(t.points[e].point,{radius:m.T?8:3,color:t.color||i,opacity:s,fillOpacity:s,interactive:!0}).bindTooltip(this._computePathTooltip(t,t.points[e]),{direction:"top"})),this._mapPaths.push(a.polyline([t.points[e].point,t.points[e+1].point],{color:t.color||i,opacity:s,interactive:!1}))}const s=t.points.length-1;if(s>=0){const e=t.gradualOpacity?r+s*o:void 0;this._mapPaths.push(a.circleMarker(t.points[s].point,{radius:m.T?8:3,color:t.color||i,opacity:e,fillOpacity:e,interactive:!0}).bindTooltip(this._computePathTooltip(t,t.points[s]),{direction:"top"}))}this._mapPaths.forEach((t=>e.addLayer(t)))}))}_drawEntities(){const t=this.hass,e=this.leafletMap,a=this.Leaflet;if(!t||!e||!a)return;if(this._mapItems.length&&(this._mapItems.forEach((t=>t.remove())),this._mapItems=[],this._mapFocusItems=[]),this._mapZones.length&&(this._mapZones.forEach((t=>t.remove())),this._mapZones=[],this._mapFocusZones=[]),this._mapCluster&&(this._mapCluster.remove(),this._mapCluster=void 0),!this.entities)return;const i=getComputedStyle(this),o=i.getPropertyValue("--accent-color"),r=i.getPropertyValue("--secondary-text-color"),s=i.getPropertyValue("--dark-primary-color"),n=this._darkMode?"dark":"light";for(const l of this.entities){const e=t.states[y(l)];if(!e)continue;const i="string"!=typeof l?l.name:void 0,c=i??(0,u.C)(e),{latitude:d,longitude:m,passive:p,icon:g,radius:f,entity_picture:b,gps_accuracy:v}=e.attributes;if(!d||!m)continue;if("zone"===(0,h.N)(e)){if(p&&!this.renderPassive)continue;let t="";if(g){const e=document.createElement("ha-icon");e.setAttribute("icon",g),t=e.outerHTML}else{const e=document.createElement("span");e.innerHTML=c,t=e.outerHTML}const e=a.circle([d,m],{interactive:!1,color:p?r:o,radius:f}),i=new _.k([d,m],e,{icon:a.divIcon({html:t,iconSize:[24,24],className:n}),interactive:this.interactiveZones,title:c});this._mapZones.push(i),!this.fitZones||"string"!=typeof l&&!1===l.focus||this._mapFocusZones.push(e);continue}const k="string"!=typeof l&&"state"===l.label_mode?this.hass.formatEntityState(e):"string"!=typeof l&&"attribute"===l.label_mode&&void 0!==l.attribute?this.hass.formatEntityAttributeValue(e,l.attribute):i??c.split(" ").map((t=>t[0])).join("").substr(0,3),C=document.createElement("ha-entity-marker");C.hass=this.hass,C.showIcon="string"!=typeof l&&"icon"===l.label_mode,C.entityId=y(l),C.entityName=k,C.entityPicture=!b||"string"!=typeof l&&l.label_mode?"":this.hass.hassUrl(b),"string"!=typeof l&&(C.entityColor=l.color);const w=new _.k([d,m],void 0,{icon:a.divIcon({html:C,iconSize:[48,48],className:""}),title:c});"string"!=typeof l&&!1===l.focus||this._mapFocusItems.push(w),v&&(w.decorationLayer=a.circle([d,m],{interactive:!1,color:s,radius:v})),this._mapItems.push(w)}this.clusterMarkers?(this._mapCluster=a.markerClusterGroup({showCoverageOnHover:!1,removeOutsideVisibleBounds:!1,maxClusterRadius:40}),this._mapCluster.addLayers(this._mapItems),e.addLayer(this._mapCluster)):this._mapItems.forEach((t=>e.addLayer(t))),this._mapZones.forEach((t=>e.addLayer(t)))}async _attachObserver(){this._resizeObserver||(this._resizeObserver=new ResizeObserver((()=>{this.leafletMap?.invalidateSize({debounceMoveend:!0})}))),this._resizeObserver.observe(this)}constructor(...t){super(...t),this.clickable=!1,this.autoFit=!1,this.renderPassive=!1,this.interactiveZones=!1,this.fitZones=!1,this.themeMode="auto",this.zoom=14,this.clusterMarkers=!0,this._loaded=!1,this._mapItems=[],this._mapFocusItems=[],this._mapZones=[],this._mapFocusZones=[],this._mapPaths=[],this._clickCount=0,this._loading=!1}}f.styles=r.iv`
    :host {
      display: block;
      height: 300px;
    }
    #map {
      height: 100%;
    }
    #map.clickable {
      cursor: pointer;
    }
    #map.dark {
      background: #090909;
    }
    #map.forced-dark {
      color: #ffffff;
      --map-filter: invert(0.9) hue-rotate(170deg) brightness(1.5) contrast(1.2)
        saturate(0.3);
    }
    #map.forced-light {
      background: #ffffff;
      color: #000000;
      --map-filter: invert(0);
    }
    #map.clickable:active,
    #map:active {
      cursor: grabbing;
      cursor: -moz-grabbing;
      cursor: -webkit-grabbing;
    }
    .leaflet-tile-pane {
      filter: var(--map-filter);
    }
    .dark .leaflet-bar a {
      background-color: #1c1c1c;
      color: #ffffff;
    }
    .dark .leaflet-bar a:hover {
      background-color: #313131;
    }
    .leaflet-marker-draggable {
      cursor: move !important;
    }
    .leaflet-edit-resize {
      border-radius: 50%;
      cursor: nesw-resize !important;
    }
    .named-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      text-align: center;
      color: var(--primary-text-color);
    }
    .leaflet-pane {
      z-index: 0 !important;
    }
    .leaflet-control,
    .leaflet-top,
    .leaflet-bottom {
      z-index: 1 !important;
    }
    .leaflet-tooltip {
      padding: 8px;
      font-size: var(--ha-font-size-s);
      background: rgba(80, 80, 80, 0.9) !important;
      color: white !important;
      border-radius: 4px;
      box-shadow: none !important;
      text-align: center;
    }

    .marker-cluster div {
      background-clip: padding-box;
      background-color: var(--primary-color);
      border: 3px solid rgba(var(--rgb-primary-color), 0.2);
      width: 32px;
      height: 32px;
      border-radius: 20px;
      text-align: center;
      color: var(--text-primary-color);
      font-size: var(--ha-font-size-m);
    }

    .marker-cluster span {
      line-height: var(--ha-line-height-expanded);
    }
  `,(0,i.__decorate)([(0,s.Cb)({attribute:!1})],f.prototype,"hass",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:!1})],f.prototype,"entities",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:!1})],f.prototype,"paths",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:!1})],f.prototype,"layers",void 0),(0,i.__decorate)([(0,s.Cb)({type:Boolean})],f.prototype,"clickable",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:"auto-fit",type:Boolean})],f.prototype,"autoFit",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:"render-passive",type:Boolean})],f.prototype,"renderPassive",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:"interactive-zones",type:Boolean})],f.prototype,"interactiveZones",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:"fit-zones",type:Boolean})],f.prototype,"fitZones",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:"theme-mode",type:String})],f.prototype,"themeMode",void 0),(0,i.__decorate)([(0,s.Cb)({type:Number})],f.prototype,"zoom",void 0),(0,i.__decorate)([(0,s.Cb)({attribute:"cluster-markers",type:Boolean})],f.prototype,"clusterMarkers",void 0),(0,i.__decorate)([(0,s.SB)()],f.prototype,"_loaded",void 0),f=(0,i.__decorate)([(0,s.Mo)("ha-map")],f),e()}catch(y){e(y)}}))},78001:function(t,e,a){a.d(e,{T:()=>i});const i="ontouchstart"in window||navigator.maxTouchPoints>0||navigator.msMaxTouchPoints>0}};
//# sourceMappingURL=9656.3dee3f6b0c64a13f.js.map