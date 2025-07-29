/*! For license information please see 3254.32167b4b872607eb.js.LICENSE.txt */
export const __webpack_ids__=["3254"];export const __webpack_modules__={37339:function(t,e,s){s.a(t,(async function(t,i){try{s.r(e),s.d(e,{HaIconSelector:()=>l});var o=s(73742),a=s(59048),r=s(7616),n=s(12790),c=s(29740),h=s(54974),d=s(27882),_=t([d,h]);[d,h]=_.then?(await _)():_;class l extends a.oi{render(){const t=this.context?.icon_entity,e=t?this.hass.states[t]:void 0,s=this.selector.icon?.placeholder||e?.attributes.icon||e&&(0,n.C)((0,h.gD)(this.hass,e));return a.dy`
      <ha-icon-picker
        .hass=${this.hass}
        .label=${this.label}
        .value=${this.value}
        .required=${this.required}
        .disabled=${this.disabled}
        .helper=${this.helper}
        .placeholder=${this.selector.icon?.placeholder??s}
        @value-changed=${this._valueChanged}
      >
        ${!s&&e?a.dy`
              <ha-state-icon
                slot="fallback"
                .hass=${this.hass}
                .stateObj=${e}
              ></ha-state-icon>
            `:a.Ld}
      </ha-icon-picker>
    `}_valueChanged(t){(0,c.B)(this,"value-changed",{value:t.detail.value})}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,o.__decorate)([(0,r.Cb)({attribute:!1})],l.prototype,"hass",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],l.prototype,"selector",void 0),(0,o.__decorate)([(0,r.Cb)()],l.prototype,"value",void 0),(0,o.__decorate)([(0,r.Cb)()],l.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)()],l.prototype,"helper",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,reflect:!0})],l.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],l.prototype,"required",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],l.prototype,"context",void 0),l=(0,o.__decorate)([(0,r.Mo)("ha-selector-icon")],l),i()}catch(l){i(l)}}))},27882:function(t,e,s){s.a(t,(async function(t,e){try{var i=s(73742),o=s(59048),a=s(7616),r=s(12790),n=s(18088),c=s(54974),h=(s(40830),t([c]));c=(h.then?(await h)():h)[0];class d extends o.oi{render(){const t=this.icon||this.stateObj&&this.hass?.entities[this.stateObj.entity_id]?.icon||this.stateObj?.attributes.icon;if(t)return o.dy`<ha-icon .icon=${t}></ha-icon>`;if(!this.stateObj)return o.Ld;if(!this.hass)return this._renderFallback();const e=(0,c.gD)(this.hass,this.stateObj,this.stateValue).then((t=>t?o.dy`<ha-icon .icon=${t}></ha-icon>`:this._renderFallback()));return o.dy`${(0,r.C)(e)}`}_renderFallback(){const t=(0,n.N)(this.stateObj);return o.dy`
      <ha-svg-icon
        .path=${c.Ls[t]||c.Rb}
      ></ha-svg-icon>
    `}}(0,i.__decorate)([(0,a.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,a.Cb)({attribute:!1})],d.prototype,"stateObj",void 0),(0,i.__decorate)([(0,a.Cb)({attribute:!1})],d.prototype,"stateValue",void 0),(0,i.__decorate)([(0,a.Cb)()],d.prototype,"icon",void 0),d=(0,i.__decorate)([(0,a.Mo)("ha-state-icon")],d),e()}catch(d){e(d)}}))},12790:function(t,e,s){s.d(e,{C:()=>l});var i=s(35340),o=s(5277),a=s(93847);class r{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class n{get(){return this.Y}pause(){this.Y??=new Promise((t=>this.Z=t))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var c=s(83522);const h=t=>!(0,o.pt)(t)&&"function"==typeof t.then,d=1073741823;class _ extends a.sR{render(...t){return t.find((t=>!h(t)))??i.Jb}update(t,e){const s=this._$Cbt;let o=s.length;this._$Cbt=e;const a=this._$CK,r=this._$CX;this.isConnected||this.disconnected();for(let i=0;i<e.length&&!(i>this._$Cwt);i++){const t=e[i];if(!h(t))return this._$Cwt=i,t;i<o&&t===s[i]||(this._$Cwt=d,o=0,Promise.resolve(t).then((async e=>{for(;r.get();)await r.get();const s=a.deref();if(void 0!==s){const i=s._$Cbt.indexOf(t);i>-1&&i<s._$Cwt&&(s._$Cwt=i,s.setValue(e))}})))}return i.Jb}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=d,this._$Cbt=[],this._$CK=new r(this),this._$CX=new n}}const l=(0,c.XM)(_)}};
//# sourceMappingURL=3254.32167b4b872607eb.js.map