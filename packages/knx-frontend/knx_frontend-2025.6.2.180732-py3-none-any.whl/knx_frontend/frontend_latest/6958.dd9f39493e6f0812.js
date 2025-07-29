export const __webpack_ids__=["6958"];export const __webpack_modules__={67936:function(e,t,r){r.d(t,{v:()=>n});var a=r(64930),o=r(76151);function n(e,t){const r=(0,o.M)(e.entity_id),n=void 0!==t?t:e?.state;if(["button","event","input_button","scene"].includes(r))return n!==a.nZ;if((0,a.rk)(n))return!1;if(n===a.PX&&"alert"!==r)return!1;switch(r){case"alarm_control_panel":return"disarmed"!==n;case"alert":return"idle"!==n;case"cover":case"valve":return"closed"!==n;case"device_tracker":case"person":return"not_home"!==n;case"lawn_mower":return["mowing","error"].includes(n);case"lock":return"locked"!==n;case"media_player":return"standby"!==n;case"vacuum":return!["idle","docked","paused"].includes(n);case"plant":return"problem"===n;case"group":return["on","home","open","locked","problem"].includes(n);case"timer":return"active"===n;case"camera":return"streaming"===n}return!0}},91337:function(e,t,r){var a=r(73742),o=r(59048),n=r(7616),i=r(69342),s=r(29740);r(22543),r(32986);const l={boolean:()=>r.e("4852").then(r.bind(r,60751)),constant:()=>r.e("177").then(r.bind(r,85184)),float:()=>r.e("2369").then(r.bind(r,94980)),grid:()=>r.e("9219").then(r.bind(r,79998)),expandable:()=>r.e("4020").then(r.bind(r,71781)),integer:()=>r.e("3703").then(r.bind(r,12960)),multi_select:()=>Promise.all([r.e("4458"),r.e("514")]).then(r.bind(r,79298)),positive_time_period_dict:()=>r.e("2010").then(r.bind(r,49058)),select:()=>r.e("3162").then(r.bind(r,64324)),string:()=>r.e("2529").then(r.bind(r,72609)),optional_actions:()=>r.e("1601").then(r.bind(r,67552))},c=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class d extends o.oi{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof o.fl&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{"selector"in e||l[e.type]?.()}))}render(){return o.dy`
      <div class="root" part="root">
        ${this.error&&this.error.base?o.dy`
              <ha-alert alert-type="error">
                ${this._computeError(this.error.base,this.schema)}
              </ha-alert>
            `:""}
        ${this.schema.map((e=>{const t=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),r=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return o.dy`
            ${t?o.dy`
                  <ha-alert own-margin alert-type="error">
                    ${this._computeError(t,e)}
                  </ha-alert>
                `:r?o.dy`
                    <ha-alert own-margin alert-type="warning">
                      ${this._computeWarning(r,e)}
                    </ha-alert>
                  `:""}
            ${"selector"in e?o.dy`<ha-selector
                  .schema=${e}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .name=${e.name}
                  .selector=${e.selector}
                  .value=${c(this.data,e)}
                  .label=${this._computeLabel(e,this.data)}
                  .disabled=${e.disabled||this.disabled||!1}
                  .placeholder=${e.required?"":e.default}
                  .helper=${this._computeHelper(e)}
                  .localizeValue=${this.localizeValue}
                  .required=${e.required||!1}
                  .context=${this._generateContext(e)}
                ></ha-selector>`:(0,i.h)(this.fieldElementName(e.type),{schema:e,data:c(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:this.hass?.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e),...this.getFormProperties()})}
          `}))}
      </div>
    `}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[r,a]of Object.entries(e.context))t[r]=this.data[a];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const r=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data={...this.data,...r},(0,s.B)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?o.dy`<ul>
        ${e.map((e=>o.dy`<li>
              ${this.computeError?this.computeError(e,t):e}
            </li>`))}
      </ul>`:this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}d.styles=o.iv`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `,(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,n.Cb)({type:Boolean})],d.prototype,"narrow",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"data",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"schema",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"error",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"warning",void 0),(0,a.__decorate)([(0,n.Cb)({type:Boolean})],d.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"computeError",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"computeWarning",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"computeLabel",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"computeHelper",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"localizeValue",void 0),d=(0,a.__decorate)([(0,n.Mo)("ha-form")],d)},64930:function(e,t,r){r.d(t,{ON:()=>i,PX:()=>s,V_:()=>l,lz:()=>n,nZ:()=>o,rk:()=>d});var a=r(13228);const o="unavailable",n="unknown",i="on",s="off",l=[o,n],c=[o,n,s],d=(0,a.z)(l);(0,a.z)(c)},37198:function(e,t,r){r.d(t,{X1:()=>a,u4:()=>o,zC:()=>n});const a=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,o=e=>e.split("/")[4],n=e=>e.startsWith("https://brands.home-assistant.io/")}};
//# sourceMappingURL=6958.dd9f39493e6f0812.js.map