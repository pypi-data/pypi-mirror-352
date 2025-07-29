"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8733"],{67936:function(e,t,r){r.d(t,{v:()=>n});r(39710);var a=r(64930),o=r(76151);function n(e,t){const r=(0,o.M)(e.entity_id),n=void 0!==t?t:null==e?void 0:e.state;if(["button","event","input_button","scene"].includes(r))return n!==a.nZ;if((0,a.rk)(n))return!1;if(n===a.PX&&"alert"!==r)return!1;switch(r){case"alarm_control_panel":return"disarmed"!==n;case"alert":return"idle"!==n;case"cover":case"valve":return"closed"!==n;case"device_tracker":case"person":return"not_home"!==n;case"lawn_mower":return["mowing","error"].includes(n);case"lock":return"locked"!==n;case"media_player":return"standby"!==n;case"vacuum":return!["idle","docked","paused"].includes(n);case"plant":return"problem"===n;case"group":return["on","home","open","locked","problem"].includes(n);case"timer":return"active"===n;case"camera":return"streaming"===n}return!0}},91337:function(e,t,r){r(26847),r(81738),r(22960),r(6989),r(87799),r(1455),r(27530);var a=r(73742),o=r(59048),n=r(7616),i=r(69342),s=r(29740);r(22543),r(32986);let c,l,d,u,p,h,m,b,_,g=e=>e;const v={boolean:()=>r.e("4852").then(r.bind(r,60751)),constant:()=>r.e("177").then(r.bind(r,85184)),float:()=>r.e("2369").then(r.bind(r,94980)),grid:()=>r.e("9219").then(r.bind(r,79998)),expandable:()=>r.e("4020").then(r.bind(r,71781)),integer:()=>r.e("3703").then(r.bind(r,12960)),multi_select:()=>Promise.all([r.e("4458"),r.e("514")]).then(r.bind(r,79298)),positive_time_period_dict:()=>r.e("2010").then(r.bind(r,49058)),select:()=>r.e("3162").then(r.bind(r,64324)),string:()=>r.e("2529").then(r.bind(r,72609)),optional_actions:()=>r.e("1601").then(r.bind(r,67552))},f=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class y extends o.oi{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof o.fl&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{var t;"selector"in e||null===(t=v[e.type])||void 0===t||t.call(v)}))}render(){return(0,o.dy)(c||(c=g`
      <div class="root" part="root">
        ${0}
        ${0}
      </div>
    `),this.error&&this.error.base?(0,o.dy)(l||(l=g`
              <ha-alert alert-type="error">
                ${0}
              </ha-alert>
            `),this._computeError(this.error.base,this.schema)):"",this.schema.map((e=>{var t;const r=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),a=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return(0,o.dy)(d||(d=g`
            ${0}
            ${0}
          `),r?(0,o.dy)(u||(u=g`
                  <ha-alert own-margin alert-type="error">
                    ${0}
                  </ha-alert>
                `),this._computeError(r,e)):a?(0,o.dy)(p||(p=g`
                    <ha-alert own-margin alert-type="warning">
                      ${0}
                    </ha-alert>
                  `),this._computeWarning(a,e)):"","selector"in e?(0,o.dy)(h||(h=g`<ha-selector
                  .schema=${0}
                  .hass=${0}
                  .narrow=${0}
                  .name=${0}
                  .selector=${0}
                  .value=${0}
                  .label=${0}
                  .disabled=${0}
                  .placeholder=${0}
                  .helper=${0}
                  .localizeValue=${0}
                  .required=${0}
                  .context=${0}
                ></ha-selector>`),e,this.hass,this.narrow,e.name,e.selector,f(this.data,e),this._computeLabel(e,this.data),e.disabled||this.disabled||!1,e.required?"":e.default,this._computeHelper(e),this.localizeValue,e.required||!1,this._generateContext(e)):(0,i.h)(this.fieldElementName(e.type),Object.assign({schema:e,data:f(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:null===(t=this.hass)||void 0===t?void 0:t.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e)},this.getFormProperties())))})))}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[r,a]of Object.entries(e.context))t[r]=this.data[a];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const r=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data=Object.assign(Object.assign({},this.data),r),(0,s.B)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?(0,o.dy)(m||(m=g`<ul>
        ${0}
      </ul>`),e.map((e=>(0,o.dy)(b||(b=g`<li>
              ${0}
            </li>`),this.computeError?this.computeError(e,t):e)))):this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}y.styles=(0,o.iv)(_||(_=g`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `)),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"hass",void 0),(0,a.__decorate)([(0,n.Cb)({type:Boolean})],y.prototype,"narrow",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"data",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"schema",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"error",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"warning",void 0),(0,a.__decorate)([(0,n.Cb)({type:Boolean})],y.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"computeError",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"computeWarning",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"computeLabel",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"computeHelper",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"localizeValue",void 0),y=(0,a.__decorate)([(0,n.Mo)("ha-form")],y)},39929:function(e,t,r){r.d(t,{iI:()=>o,oT:()=>a});r(39710),r(81738),r(6989),r(21700),r(87799),r(1455),r(26086),r(56389);const a=e=>e.map((e=>{if("string"!==e.type)return e;switch(e.name){case"username":return Object.assign(Object.assign({},e),{},{autocomplete:"username",autofocus:!0});case"password":return Object.assign(Object.assign({},e),{},{autocomplete:"current-password"});case"code":return Object.assign(Object.assign({},e),{},{autocomplete:"one-time-code",autofocus:!0});default:return e}})),o=(e,t)=>e.callWS({type:"auth/sign_path",path:t})},64930:function(e,t,r){r.d(t,{ON:()=>i,PX:()=>s,V_:()=>c,lz:()=>n,nZ:()=>o,rk:()=>d});var a=r(13228);const o="unavailable",n="unknown",i="on",s="off",c=[o,n],l=[o,n,s],d=(0,a.z)(c);(0,a.z)(l)},37198:function(e,t,r){r.d(t,{X1:()=>a,u4:()=>o,zC:()=>n});r(44261);const a=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,o=e=>e.split("/")[4],n=e=>e.startsWith("https://brands.home-assistant.io/")}}]);
//# sourceMappingURL=8733.3c802eb87f58120c.js.map