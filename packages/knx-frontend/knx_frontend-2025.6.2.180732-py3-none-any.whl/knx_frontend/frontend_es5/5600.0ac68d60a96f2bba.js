"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5600"],{45917:function(e,t,r){r.a(e,(async function(e,a){try{r.r(t),r.d(t,{HaLabelSelector:()=>v});r(26847),r(27530);var i=r(73742),s=r(59048),o=r(7616),l=r(74608),n=r(29740),d=r(19442),c=e([d]);d=(c.then?(await c)():c)[0];let u,h,b,p=e=>e;class v extends s.oi{render(){var e;return this.selector.label.multiple?(0,s.dy)(u||(u=p`
        <ha-labels-picker
          no-add
          .hass=${0}
          .value=${0}
          .required=${0}
          .disabled=${0}
          .label=${0}
          @value-changed=${0}
        >
        </ha-labels-picker>
      `),this.hass,(0,l.r)(null!==(e=this.value)&&void 0!==e?e:[]),this.required,this.disabled,this.label,this._handleChange):(0,s.dy)(h||(h=p`
      <ha-label-picker
        no-add
        .hass=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .label=${0}
        @value-changed=${0}
      >
      </ha-label-picker>
    `),this.hass,this.value,this.required,this.disabled,this.label,this._handleChange)}_handleChange(e){let t=e.detail.value;this.value!==t&&((""===t||Array.isArray(t)&&0===t.length)&&!this.required&&(t=void 0),(0,n.B)(this,"value-changed",{value:t}))}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}v.styles=(0,s.iv)(b||(b=p`
    ha-labels-picker {
      display: block;
      width: 100%;
    }
  `)),(0,i.__decorate)([(0,o.Cb)({attribute:!1})],v.prototype,"hass",void 0),(0,i.__decorate)([(0,o.Cb)()],v.prototype,"value",void 0),(0,i.__decorate)([(0,o.Cb)()],v.prototype,"name",void 0),(0,i.__decorate)([(0,o.Cb)()],v.prototype,"label",void 0),(0,i.__decorate)([(0,o.Cb)()],v.prototype,"placeholder",void 0),(0,i.__decorate)([(0,o.Cb)()],v.prototype,"helper",void 0),(0,i.__decorate)([(0,o.Cb)({attribute:!1})],v.prototype,"selector",void 0),(0,i.__decorate)([(0,o.Cb)({type:Boolean})],v.prototype,"disabled",void 0),(0,i.__decorate)([(0,o.Cb)({type:Boolean})],v.prototype,"required",void 0),v=(0,i.__decorate)([(0,o.Mo)("ha-selector-label")],v),a()}catch(u){a(u)}}))},88865:function(e,t,r){r.d(t,{B:()=>s});r(40777),r(2394),r(87799),r(1455);const a=e=>{let t=[];function r(r,a){e=a?r:Object.assign(Object.assign({},e),r);let i=t;for(let t=0;t<i.length;t++)i[t](e)}return{get state(){return e},action(t){function a(e){r(e,!1)}return function(){let r=[e];for(let e=0;e<arguments.length;e++)r.push(arguments[e]);let i=t.apply(this,r);if(null!=i)return i instanceof Promise?i.then(a):a(i)}},setState:r,clearState(){e=void 0},subscribe(e){return t.push(e),()=>{!function(e){let r=[];for(let a=0;a<t.length;a++)t[a]===e?e=null:r.push(t[a]);t=r}(e)}}}},i=(e,t,r,i,s={unsubGrace:!0})=>{if(e[t])return e[t];let o,l,n=0,d=a();const c=()=>{if(!r)throw new Error("Collection does not support refresh");return r(e).then((e=>d.setState(e,!0)))},u=()=>c().catch((t=>{if(e.connected)throw t})),h=()=>{l=void 0,o&&o.then((e=>{e()})),d.clearState(),e.removeEventListener("ready",c),e.removeEventListener("disconnected",b)},b=()=>{l&&(clearTimeout(l),h())};return e[t]={get state(){return d.state},refresh:c,subscribe(t){n++,1===n&&(()=>{if(void 0!==l)return clearTimeout(l),void(l=void 0);i&&(o=i(e,d)),r&&(e.addEventListener("ready",u),u()),e.addEventListener("disconnected",b)})();const a=d.subscribe(t);return void 0!==d.state&&setTimeout((()=>t(d.state)),0),()=>{a(),n--,n||(s.unsubGrace?l=setTimeout(h,5e3):h())}}},e[t]},s=(e,t,r,a,s)=>i(a,e,t,r).subscribe(s)}}]);
//# sourceMappingURL=5600.0ac68d60a96f2bba.js.map