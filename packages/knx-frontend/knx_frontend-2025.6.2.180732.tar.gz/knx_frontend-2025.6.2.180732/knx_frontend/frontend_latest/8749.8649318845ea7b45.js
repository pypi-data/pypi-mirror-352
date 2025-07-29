/*! For license information please see 8749.8649318845ea7b45.js.LICENSE.txt */
export const __webpack_ids__=["8749"];export const __webpack_modules__={52245:function(e,t,i){i.a(e,(async function(e,t){try{var s=i(73742),r=i(59048),n=i(7616),a=i(28105),o=i(29740),c=i(27087),l=i(39711),d=e([l]);l=(d.then?(await d)():d)[0];class h extends r.oi{render(){if(!this.hass)return r.Ld;const e=this._currentEntities;return r.dy`
      ${this.label?r.dy`<label>${this.label}</label>`:r.Ld}
      ${e.map((e=>r.dy`
          <div>
            <ha-entity-picker
              allow-custom-entity
              .curValue=${e}
              .hass=${this.hass}
              .includeDomains=${this.includeDomains}
              .excludeDomains=${this.excludeDomains}
              .includeEntities=${this.includeEntities}
              .excludeEntities=${this.excludeEntities}
              .includeDeviceClasses=${this.includeDeviceClasses}
              .includeUnitOfMeasurement=${this.includeUnitOfMeasurement}
              .entityFilter=${this.entityFilter}
              .value=${e}
              .disabled=${this.disabled}
              .createDomains=${this.createDomains}
              @value-changed=${this._entityChanged}
            ></ha-entity-picker>
          </div>
        `))}
      <div>
        <ha-entity-picker
          allow-custom-entity
          .hass=${this.hass}
          .includeDomains=${this.includeDomains}
          .excludeDomains=${this.excludeDomains}
          .includeEntities=${this.includeEntities}
          .excludeEntities=${this._excludeEntities(this.value,this.excludeEntities)}
          .includeDeviceClasses=${this.includeDeviceClasses}
          .includeUnitOfMeasurement=${this.includeUnitOfMeasurement}
          .entityFilter=${this.entityFilter}
          .placeholder=${this.placeholder}
          .helper=${this.helper}
          .disabled=${this.disabled}
          .createDomains=${this.createDomains}
          .required=${this.required&&!e.length}
          @value-changed=${this._addEntity}
        ></ha-entity-picker>
      </div>
    `}get _currentEntities(){return this.value||[]}async _updateEntities(e){this.value=e,(0,o.B)(this,"value-changed",{value:e})}_entityChanged(e){e.stopPropagation();const t=e.currentTarget.curValue,i=e.detail.value;if(i===t||void 0!==i&&!(0,c.T)(i))return;const s=this._currentEntities;i&&!s.includes(i)?this._updateEntities(s.map((e=>e===t?i:e))):this._updateEntities(s.filter((e=>e!==t)))}async _addEntity(e){e.stopPropagation();const t=e.detail.value;if(!t)return;if(e.currentTarget.value="",!t)return;const i=this._currentEntities;i.includes(t)||this._updateEntities([...i,t])}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._excludeEntities=(0,a.Z)(((e,t)=>void 0===e?t:[...t||[],...e]))}}h.styles=r.iv`
    div {
      margin-top: 8px;
    }
    label {
      display: block;
      margin: 0 0 8px;
    }
  `,(0,s.__decorate)([(0,n.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array})],h.prototype,"value",void 0),(0,s.__decorate)([(0,n.Cb)({type:Boolean})],h.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.Cb)({type:Boolean})],h.prototype,"required",void 0),(0,s.__decorate)([(0,n.Cb)()],h.prototype,"label",void 0),(0,s.__decorate)([(0,n.Cb)()],h.prototype,"placeholder",void 0),(0,s.__decorate)([(0,n.Cb)()],h.prototype,"helper",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-domains"})],h.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"exclude-domains"})],h.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-device-classes"})],h.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-unit-of-measurement"})],h.prototype,"includeUnitOfMeasurement",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-entities"})],h.prototype,"includeEntities",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"exclude-entities"})],h.prototype,"excludeEntities",void 0),(0,s.__decorate)([(0,n.Cb)({attribute:!1})],h.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,n.Cb)({attribute:!1,type:Array})],h.prototype,"createDomains",void 0),h=(0,s.__decorate)([(0,n.Mo)("ha-entities-picker")],h),t()}catch(h){t(h)}}))},87393:function(e,t,i){i.a(e,(async function(e,s){try{i.r(t),i.d(t,{HaEntitySelector:()=>_});var r=i(73742),n=i(59048),a=i(7616),o=i(74608),c=i(29740),l=i(71170),d=i(45103),h=i(52245),u=i(39711),p=e([h,u]);[h,u]=p.then?(await p)():p;class _ extends n.oi{_hasIntegration(e){return e.entity?.filter&&(0,o.r)(e.entity.filter).some((e=>e.integration))}willUpdate(e){e.has("selector")&&void 0!==this.value&&(this.selector.entity?.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,c.B)(this,"value-changed",{value:this.value})):!this.selector.entity?.multiple&&Array.isArray(this.value)&&(this.value=this.value[0],(0,c.B)(this,"value-changed",{value:this.value})))}render(){return this._hasIntegration(this.selector)&&!this._entitySources?n.Ld:this.selector.entity?.multiple?n.dy`
      <ha-entities-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .includeEntities=${this.selector.entity.include_entities}
        .excludeEntities=${this.selector.entity.exclude_entities}
        .entityFilter=${this._filterEntities}
        .createDomains=${this._createDomains}
        .disabled=${this.disabled}
        .required=${this.required}
      ></ha-entities-picker>
    `:n.dy`<ha-entity-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .includeEntities=${this.selector.entity?.include_entities}
        .excludeEntities=${this.selector.entity?.exclude_entities}
        .entityFilter=${this._filterEntities}
        .createDomains=${this._createDomains}
        .disabled=${this.disabled}
        .required=${this.required}
        allow-custom-entity
      ></ha-entity-picker>`}updated(e){super.updated(e),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,l.m)(this.hass).then((e=>{this._entitySources=e})),e.has("selector")&&(this._createDomains=(0,d.bq)(this.selector))}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._filterEntities=e=>!this.selector?.entity?.filter||(0,o.r)(this.selector.entity.filter).some((t=>(0,d.lV)(t,e,this._entitySources)))}}(0,r.__decorate)([(0,a.Cb)({attribute:!1})],_.prototype,"hass",void 0),(0,r.__decorate)([(0,a.Cb)({attribute:!1})],_.prototype,"selector",void 0),(0,r.__decorate)([(0,a.SB)()],_.prototype,"_entitySources",void 0),(0,r.__decorate)([(0,a.Cb)()],_.prototype,"value",void 0),(0,r.__decorate)([(0,a.Cb)()],_.prototype,"label",void 0),(0,r.__decorate)([(0,a.Cb)()],_.prototype,"helper",void 0),(0,r.__decorate)([(0,a.Cb)({type:Boolean})],_.prototype,"disabled",void 0),(0,r.__decorate)([(0,a.Cb)({type:Boolean})],_.prototype,"required",void 0),(0,r.__decorate)([(0,a.SB)()],_.prototype,"_createDomains",void 0),_=(0,r.__decorate)([(0,a.Mo)("ha-selector-entity")],_),s()}catch(_){s(_)}}))},71170:function(e,t,i){i.d(t,{m:()=>n});const s=async(e,t,i,r,n,...a)=>{const o=n,c=o[e],l=c=>r&&r(n,c.result)!==c.cacheKey?(o[e]=void 0,s(e,t,i,r,n,...a)):c.result;if(c)return c instanceof Promise?c.then(l):l(c);const d=i(n,...a);return o[e]=d,d.then((i=>{o[e]={result:i,cacheKey:r?.(n,i)},setTimeout((()=>{o[e]=void 0}),t)}),(()=>{o[e]=void 0})),d},r=e=>e.callWS({type:"entity/source"}),n=e=>s("_entitySources",3e4,r,(e=>Object.keys(e.states).length),e)},12790:function(e,t,i){i.d(t,{C:()=>u});var s=i(35340),r=i(5277),n=i(93847);class a{disconnect(){this.G=void 0}reconnect(e){this.G=e}deref(){return this.G}constructor(e){this.G=e}}class o{get(){return this.Y}pause(){this.Y??=new Promise((e=>this.Z=e))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var c=i(83522);const l=e=>!(0,r.pt)(e)&&"function"==typeof e.then,d=1073741823;class h extends n.sR{render(...e){return e.find((e=>!l(e)))??s.Jb}update(e,t){const i=this._$Cbt;let r=i.length;this._$Cbt=t;const n=this._$CK,a=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<t.length&&!(s>this._$Cwt);s++){const e=t[s];if(!l(e))return this._$Cwt=s,e;s<r&&e===i[s]||(this._$Cwt=d,r=0,Promise.resolve(e).then((async t=>{for(;a.get();)await a.get();const i=n.deref();if(void 0!==i){const s=i._$Cbt.indexOf(e);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(t))}})))}return s.Jb}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=d,this._$Cbt=[],this._$CK=new a(this),this._$CX=new o}}const u=(0,c.XM)(h)}};
//# sourceMappingURL=8749.8649318845ea7b45.js.map