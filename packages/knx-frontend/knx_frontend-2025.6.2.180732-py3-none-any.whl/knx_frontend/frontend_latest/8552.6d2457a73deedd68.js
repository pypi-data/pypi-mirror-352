export const __webpack_ids__=["8552"];export const __webpack_modules__={81758:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(73742),a=i(59048),s=i(7616),r=i(73549),d=(i(90256),t([r]));r=(d.then?(await d)():d)[0];class h extends a.oi{shouldUpdate(t){return!(!t.has("_opened")&&this._opened)}updated(t){if(t.has("_opened")&&this._opened){const t=this.entityId?this.hass.states[this.entityId]:void 0;this._comboBox.items=t?Object.keys(t.attributes).filter((t=>!this.hideAttributes?.includes(t))).map((e=>({value:e,label:(0,r.S)(this.hass.localize,t,this.hass.entities,e)}))):[]}}render(){if(!this.hass)return a.Ld;const t=this.hass.states[this.entityId];return a.dy`
      <ha-combo-box
        .hass=${this.hass}
        .value=${this.value?t?(0,r.S)(this.hass.localize,t,this.hass.entities,this.value):this.value:""}
        .autofocus=${this.autofocus}
        .label=${this.label??this.hass.localize("ui.components.entity.entity-attribute-picker.attribute")}
        .disabled=${this.disabled||!this.entityId}
        .required=${this.required}
        .helper=${this.helper}
        .allowCustomValue=${this.allowCustomValue}
        item-value-path="value"
        item-label-path="label"
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
      >
      </ha-combo-box>
    `}_openedChanged(t){this._opened=t.detail.value}_valueChanged(t){this.value=t.detail.value}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this._opened=!1}}(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"entityId",void 0),(0,o.__decorate)([(0,s.Cb)({type:Array,attribute:"hide-attributes"})],h.prototype,"hideAttributes",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],h.prototype,"autofocus",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],h.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],h.prototype,"required",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,attribute:"allow-custom-value"})],h.prototype,"allowCustomValue",void 0),(0,o.__decorate)([(0,s.Cb)()],h.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)()],h.prototype,"value",void 0),(0,o.__decorate)([(0,s.Cb)()],h.prototype,"helper",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_opened",void 0),(0,o.__decorate)([(0,s.IO)("ha-combo-box",!0)],h.prototype,"_comboBox",void 0),h=(0,o.__decorate)([(0,s.Mo)("ha-entity-attribute-picker")],h),e()}catch(h){e(h)}}))},58558:function(t,e,i){i.a(t,(async function(t,o){try{i.r(e),i.d(e,{HaSelectorAttribute:()=>u});var a=i(73742),s=i(59048),r=i(7616),d=i(29740),h=i(81758),l=t([h]);h=(l.then?(await l)():l)[0];class u extends s.oi{render(){return s.dy`
      <ha-entity-attribute-picker
        .hass=${this.hass}
        .entityId=${this.selector.attribute?.entity_id||this.context?.filter_entity}
        .hideAttributes=${this.selector.attribute?.hide_attributes}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        allow-custom-value
      ></ha-entity-attribute-picker>
    `}updated(t){if(super.updated(t),!this.value||this.selector.attribute?.entity_id||!t.has("context"))return;const e=t.get("context");if(!this.context||!e||e.filter_entity===this.context.filter_entity)return;let i=!1;if(this.context.filter_entity){const t=this.hass.states[this.context.filter_entity];t&&this.value in t.attributes||(i=!0)}else i=void 0!==this.value;i&&(0,d.B)(this,"value-changed",{value:void 0})}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,a.__decorate)([(0,r.Cb)({attribute:!1})],u.prototype,"hass",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],u.prototype,"selector",void 0),(0,a.__decorate)([(0,r.Cb)()],u.prototype,"value",void 0),(0,a.__decorate)([(0,r.Cb)()],u.prototype,"label",void 0),(0,a.__decorate)([(0,r.Cb)()],u.prototype,"helper",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],u.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],u.prototype,"required",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],u.prototype,"context",void 0),u=(0,a.__decorate)([(0,r.Mo)("ha-selector-attribute")],u),o()}catch(u){o(u)}}))}};
//# sourceMappingURL=8552.6d2457a73deedd68.js.map