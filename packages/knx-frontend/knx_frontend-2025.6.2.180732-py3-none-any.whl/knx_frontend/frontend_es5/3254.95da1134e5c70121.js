/*! For license information please see 3254.95da1134e5c70121.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3254"],{37339:function(t,e,i){i.a(t,(async function(t,s){try{i.r(e),i.d(e,{HaIconSelector:()=>b});i(26847),i(27530);var o=i(73742),a=i(59048),n=i(7616),r=i(28177),c=i(29740),h=i(54974),d=i(27882),l=t([d,h]);[d,h]=l.then?(await l)():l;let u,v,_=t=>t;class b extends a.oi{render(){var t,e,i,s;const o=null===(t=this.context)||void 0===t?void 0:t.icon_entity,n=o?this.hass.states[o]:void 0,c=(null===(e=this.selector.icon)||void 0===e?void 0:e.placeholder)||(null==n?void 0:n.attributes.icon)||n&&(0,r.C)((0,h.gD)(this.hass,n));return(0,a.dy)(u||(u=_`
      <ha-icon-picker
        .hass=${0}
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .helper=${0}
        .placeholder=${0}
        @value-changed=${0}
      >
        ${0}
      </ha-icon-picker>
    `),this.hass,this.label,this.value,this.required,this.disabled,this.helper,null!==(i=null===(s=this.selector.icon)||void 0===s?void 0:s.placeholder)&&void 0!==i?i:c,this._valueChanged,!c&&n?(0,a.dy)(v||(v=_`
              <ha-state-icon
                slot="fallback"
                .hass=${0}
                .stateObj=${0}
              ></ha-state-icon>
            `),this.hass,n):a.Ld)}_valueChanged(t){(0,c.B)(this,"value-changed",{value:t.detail.value})}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,o.__decorate)([(0,n.Cb)({attribute:!1})],b.prototype,"hass",void 0),(0,o.__decorate)([(0,n.Cb)({attribute:!1})],b.prototype,"selector",void 0),(0,o.__decorate)([(0,n.Cb)()],b.prototype,"value",void 0),(0,o.__decorate)([(0,n.Cb)()],b.prototype,"label",void 0),(0,o.__decorate)([(0,n.Cb)()],b.prototype,"helper",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean,reflect:!0})],b.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean})],b.prototype,"required",void 0),(0,o.__decorate)([(0,n.Cb)({attribute:!1})],b.prototype,"context",void 0),b=(0,o.__decorate)([(0,n.Mo)("ha-selector-icon")],b),s()}catch(u){s(u)}}))},27882:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(73742),o=i(59048),a=i(7616),n=i(28177),r=i(18088),c=i(54974),h=(i(40830),t([c]));c=(h.then?(await h)():h)[0];let d,l,u,v,_=t=>t;class b extends o.oi{render(){var t,e;const i=this.icon||this.stateObj&&(null===(t=this.hass)||void 0===t||null===(t=t.entities[this.stateObj.entity_id])||void 0===t?void 0:t.icon)||(null===(e=this.stateObj)||void 0===e?void 0:e.attributes.icon);if(i)return(0,o.dy)(d||(d=_`<ha-icon .icon=${0}></ha-icon>`),i);if(!this.stateObj)return o.Ld;if(!this.hass)return this._renderFallback();const s=(0,c.gD)(this.hass,this.stateObj,this.stateValue).then((t=>t?(0,o.dy)(l||(l=_`<ha-icon .icon=${0}></ha-icon>`),t):this._renderFallback()));return(0,o.dy)(u||(u=_`${0}`),(0,n.C)(s))}_renderFallback(){const t=(0,r.N)(this.stateObj);return(0,o.dy)(v||(v=_`
      <ha-svg-icon
        .path=${0}
      ></ha-svg-icon>
    `),c.Ls[t]||c.Rb)}}(0,s.__decorate)([(0,a.Cb)({attribute:!1})],b.prototype,"hass",void 0),(0,s.__decorate)([(0,a.Cb)({attribute:!1})],b.prototype,"stateObj",void 0),(0,s.__decorate)([(0,a.Cb)({attribute:!1})],b.prototype,"stateValue",void 0),(0,s.__decorate)([(0,a.Cb)()],b.prototype,"icon",void 0),b=(0,s.__decorate)([(0,a.Mo)("ha-state-icon")],b),e()}catch(d){e(d)}}))},28177:function(t,e,i){i.d(e,{C:()=>u});i(26847),i(81738),i(29981),i(1455),i(27530);var s=i(31152),o=i(5277),a=i(93847);i(84730),i(15411),i(40777);class n{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class r{get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.Z=t)))}resume(){var t;null!==(t=this.Z)&&void 0!==t&&t.call(this),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var c=i(83522);const h=t=>!(0,o.pt)(t)&&"function"==typeof t.then,d=1073741823;class l extends a.sR{render(...t){var e;return null!==(e=t.find((t=>!h(t))))&&void 0!==e?e:s.Jb}update(t,e){const i=this._$Cbt;let o=i.length;this._$Cbt=e;const a=this._$CK,n=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<e.length&&!(s>this._$Cwt);s++){const t=e[s];if(!h(t))return this._$Cwt=s,t;s<o&&t===i[s]||(this._$Cwt=d,o=0,Promise.resolve(t).then((async e=>{for(;n.get();)await n.get();const i=a.deref();if(void 0!==i){const s=i._$Cbt.indexOf(t);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(e))}})))}return s.Jb}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=d,this._$Cbt=[],this._$CK=new n(this),this._$CX=new r}}const u=(0,c.XM)(l)}}]);
//# sourceMappingURL=3254.95da1134e5c70121.js.map