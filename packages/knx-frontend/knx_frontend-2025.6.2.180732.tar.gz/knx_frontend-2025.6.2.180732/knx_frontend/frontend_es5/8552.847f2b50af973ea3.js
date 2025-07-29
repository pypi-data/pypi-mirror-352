"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8552"],{81758:function(t,e,i){i.a(t,(async function(t,e){try{i(39710),i(26847),i(81738),i(94814),i(6989),i(56389),i(27530);var o=i(73742),a=i(59048),s=i(7616),r=i(73549),d=i(54693),l=t([d,r]);[d,r]=l.then?(await l)():l;let h,u=t=>t;class n extends a.oi{shouldUpdate(t){return!(!t.has("_opened")&&this._opened)}updated(t){if(t.has("_opened")&&this._opened){const t=this.entityId?this.hass.states[this.entityId]:void 0;this._comboBox.items=t?Object.keys(t.attributes).filter((t=>{var e;return!(null!==(e=this.hideAttributes)&&void 0!==e&&e.includes(t))})).map((e=>({value:e,label:(0,r.S)(this.hass.localize,t,this.hass.entities,e)}))):[]}}render(){var t;if(!this.hass)return a.Ld;const e=this.hass.states[this.entityId];return(0,a.dy)(h||(h=u`
      <ha-combo-box
        .hass=${0}
        .value=${0}
        .autofocus=${0}
        .label=${0}
        .disabled=${0}
        .required=${0}
        .helper=${0}
        .allowCustomValue=${0}
        item-value-path="value"
        item-label-path="label"
        @opened-changed=${0}
        @value-changed=${0}
      >
      </ha-combo-box>
    `),this.hass,this.value?e?(0,r.S)(this.hass.localize,e,this.hass.entities,this.value):this.value:"",this.autofocus,null!==(t=this.label)&&void 0!==t?t:this.hass.localize("ui.components.entity.entity-attribute-picker.attribute"),this.disabled||!this.entityId,this.required,this.helper,this.allowCustomValue,this._openedChanged,this._valueChanged)}_openedChanged(t){this._opened=t.detail.value}_valueChanged(t){this.value=t.detail.value}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this._opened=!1}}(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"entityId",void 0),(0,o.__decorate)([(0,s.Cb)({type:Array,attribute:"hide-attributes"})],n.prototype,"hideAttributes",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],n.prototype,"autofocus",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],n.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],n.prototype,"required",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,attribute:"allow-custom-value"})],n.prototype,"allowCustomValue",void 0),(0,o.__decorate)([(0,s.Cb)()],n.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)()],n.prototype,"value",void 0),(0,o.__decorate)([(0,s.Cb)()],n.prototype,"helper",void 0),(0,o.__decorate)([(0,s.SB)()],n.prototype,"_opened",void 0),(0,o.__decorate)([(0,s.IO)("ha-combo-box",!0)],n.prototype,"_comboBox",void 0),n=(0,o.__decorate)([(0,s.Mo)("ha-entity-attribute-picker")],n),e()}catch(h){e(h)}}))},58558:function(t,e,i){i.a(t,(async function(t,o){try{i.r(e),i.d(e,{HaSelectorAttribute:()=>c});i(26847),i(27530);var a=i(73742),s=i(59048),r=i(7616),d=i(29740),l=i(81758),h=t([l]);l=(h.then?(await h)():h)[0];let u,n=t=>t;class c extends s.oi{render(){var t,e,i;return(0,s.dy)(u||(u=n`
      <ha-entity-attribute-picker
        .hass=${0}
        .entityId=${0}
        .hideAttributes=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        allow-custom-value
      ></ha-entity-attribute-picker>
    `),this.hass,(null===(t=this.selector.attribute)||void 0===t?void 0:t.entity_id)||(null===(e=this.context)||void 0===e?void 0:e.filter_entity),null===(i=this.selector.attribute)||void 0===i?void 0:i.hide_attributes,this.value,this.label,this.helper,this.disabled,this.required)}updated(t){var e;if(super.updated(t),!this.value||null!==(e=this.selector.attribute)&&void 0!==e&&e.entity_id||!t.has("context"))return;const i=t.get("context");if(!this.context||!i||i.filter_entity===this.context.filter_entity)return;let o=!1;if(this.context.filter_entity){const t=this.hass.states[this.context.filter_entity];t&&this.value in t.attributes||(o=!0)}else o=void 0!==this.value;o&&(0,d.B)(this,"value-changed",{value:void 0})}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,a.__decorate)([(0,r.Cb)({attribute:!1})],c.prototype,"hass",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],c.prototype,"selector",void 0),(0,a.__decorate)([(0,r.Cb)()],c.prototype,"value",void 0),(0,a.__decorate)([(0,r.Cb)()],c.prototype,"label",void 0),(0,a.__decorate)([(0,r.Cb)()],c.prototype,"helper",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],c.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],c.prototype,"required",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],c.prototype,"context",void 0),c=(0,a.__decorate)([(0,r.Mo)("ha-selector-attribute")],c),o()}catch(u){o(u)}}))}}]);
//# sourceMappingURL=8552.847f2b50af973ea3.js.map