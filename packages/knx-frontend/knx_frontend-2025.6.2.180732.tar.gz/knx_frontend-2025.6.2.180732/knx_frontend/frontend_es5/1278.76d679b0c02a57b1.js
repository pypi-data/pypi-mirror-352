"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1278"],{94262:function(e,t,i){i(26847),i(27530);var a=i(73742),s=i(59048),o=i(7616),r=i(29740);i(24340);let l,n=e=>e;class d extends s.oi{render(){return this.aliases?(0,s.dy)(l||(l=n`
      <ha-multi-textfield
        .hass=${0}
        .value=${0}
        .disabled=${0}
        .label=${0}
        .removeLabel=${0}
        .addLabel=${0}
        item-index
        @value-changed=${0}
      >
      </ha-multi-textfield>
    `),this.hass,this.aliases,this.disabled,this.hass.localize("ui.dialogs.aliases.label"),this.hass.localize("ui.dialogs.aliases.remove"),this.hass.localize("ui.dialogs.aliases.add"),this._aliasesChanged):s.Ld}_aliasesChanged(e){(0,r.B)(this,"value-changed",{value:e})}constructor(...e){super(...e),this.disabled=!1}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array})],d.prototype,"aliases",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],d.prototype,"disabled",void 0),d=(0,a.__decorate)([(0,o.Mo)("ha-aliases-editor")],d)},86026:function(e,t,i){i.d(t,{m:()=>d});var a=i(73742),s=i(59048),o=i(7616);i(40830);let r,l,n=e=>e;const d=e=>{switch(e.level){case 0:return"M11,10H13V16H11V10M22,12H19V20H5V12H2L12,3L22,12M15,10A2,2 0 0,0 13,8H11A2,2 0 0,0 9,10V16A2,2 0 0,0 11,18H13A2,2 0 0,0 15,16V10Z";case 1:return"M12,3L2,12H5V20H19V12H22L12,3M10,8H14V18H12V10H10V8Z";case 2:return"M12,3L2,12H5V20H19V12H22L12,3M9,8H13A2,2 0 0,1 15,10V12A2,2 0 0,1 13,14H11V16H15V18H9V14A2,2 0 0,1 11,12H13V10H9V8Z";case 3:return"M12,3L22,12H19V20H5V12H2L12,3M15,11.5V10C15,8.89 14.1,8 13,8H9V10H13V12H11V14H13V16H9V18H13A2,2 0 0,0 15,16V14.5A1.5,1.5 0 0,0 13.5,13A1.5,1.5 0 0,0 15,11.5Z";case-1:return"M12,3L2,12H5V20H19V12H22L12,3M11,15H7V13H11V15M15,18H13V10H11V8H15V18Z"}return"M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"};class h extends s.oi{render(){if(this.floor.icon)return(0,s.dy)(r||(r=n`<ha-icon .icon=${0}></ha-icon>`),this.floor.icon);const e=d(this.floor);return(0,s.dy)(l||(l=n`<ha-svg-icon .path=${0}></ha-svg-icon>`),e)}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],h.prototype,"floor",void 0),(0,a.__decorate)([(0,o.Cb)()],h.prototype,"icon",void 0),h=(0,a.__decorate)([(0,o.Mo)("ha-floor-icon")],h)},79760:function(e,t,i){i.a(e,(async function(e,t){try{i(39710),i(26847),i(81738),i(33480),i(94814),i(22960),i(6989),i(72489),i(1455),i(56303),i(56389),i(44261),i(27530);var a=i(73742),s=i(59048),o=i(7616),r=i(28105),l=i(29740),n=i(76151),d=i(41099),h=i(57108),c=i(57774),_=i(98903),u=i(81665),p=i(5460),y=(i(57264),i(86026),i(33321)),m=(i(78645),i(40830),e([y]));y=(m.then?(await m)():m)[0];let v,g,f,b,$,V,H=e=>e;const C="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",x="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z",z="___ADD_NEW___";class k extends s.oi{async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.floor-picker.floor"),i=this._computeValueRenderer(this.hass.floors);return(0,s.dy)(v||(v=H`
      <ha-generic-picker
        .hass=${0}
        .autofocus=${0}
        .label=${0}
        .notFoundLabel=${0}
        .placeholder=${0}
        .value=${0}
        .getItems=${0}
        .getAdditionalItems=${0}
        .valueRenderer=${0}
        .rowRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.label,this.hass.localize("ui.components.floor-picker.no_match"),t,this.value,this._getItems,this._getAdditionalItems,i,this._rowRenderer,this._valueChanged)}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t){if(t.startsWith(z)){this.hass.loadFragmentTranslation("config");const e=t.substring(z.length);(0,p.y)(this,{suggestedName:e,createEntry:async(e,t)=>{try{const i=await(0,_.z3)(this.hass,e);t.forEach((e=>{(0,h.IO)(this.hass,e,{floor_id:i.floor_id})})),this._setValue(i.floor_id)}catch(i){(0,u.Ys)(this,{title:this.hass.localize("ui.components.floor-picker.failed_create_floor"),text:i.message})}}})}this._setValue(t)}else this._setValue(void 0)}_setValue(e){this.value=e,(0,l.B)(this,"value-changed",{value:e}),(0,l.B)(this,"change")}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._computeValueRenderer=(0,r.Z)((e=>e=>{const t=this.hass.floors[e];if(!t)return(0,s.dy)(g||(g=H`
            <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
            <span slot="headline">${0}</span>
          `),x,t);const i=t?(0,d.r)(t):void 0;return(0,s.dy)(f||(f=H`
          <ha-floor-icon slot="start" .floor=${0}></ha-floor-icon>
          <span slot="headline">${0}</span>
        `),t,i)})),this._getFloors=(0,r.Z)(((e,t,i,a,s,o,r,l,h,u)=>{const p=Object.values(e),y=Object.values(t),m=Object.values(i),v=Object.values(a);let g,f,b={};(s||o||r||l||h)&&(b=(0,c.R6)(v),g=m,f=v.filter((e=>e.area_id)),s&&(g=g.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>s.includes((0,n.M)(e.entity_id))))})),f=f.filter((e=>s.includes((0,n.M)(e.entity_id))))),o&&(g=g.filter((e=>{const t=b[e.id];return!t||!t.length||v.every((e=>!o.includes((0,n.M)(e.entity_id))))})),f=f.filter((e=>!o.includes((0,n.M)(e.entity_id))))),r&&(g=g.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))})),f=f.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&r.includes(t.attributes.device_class)}))),l&&(g=g.filter((e=>l(e)))),h&&(g=g.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&h(t)}))})),f=f.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&h(t)}))));let $,V=p;if(g&&($=g.filter((e=>e.area_id)).map((e=>e.area_id))),f&&($=(null!=$?$:[]).concat(f.filter((e=>e.area_id)).map((e=>e.area_id)))),$){const e=(0,_.N5)(y);V=V.filter((t=>{var i;return null===(i=e[t.floor_id])||void 0===i?void 0:i.some((e=>$.includes(e.area_id)))}))}u&&(V=V.filter((e=>!u.includes(e.floor_id))));return V.map((e=>{var t;const i=(0,d.r)(e);return{id:e.floor_id,primary:i,floor:e,sorting_label:(null===(t=e.level)||void 0===t?void 0:t.toString())||"zzzzz",search_labels:[i,e.floor_id,...e.aliases].filter((e=>Boolean(e)))}}))})),this._rowRenderer=e=>(0,s.dy)(b||(b=H`
    <ha-combo-box-item type="button" compact>
      ${0}
      <span slot="headline">${0}</span>
    </ha-combo-box-item>
  `),e.icon_path?(0,s.dy)($||($=H`
            <ha-svg-icon
              slot="start"
              style="margin: 0 4px"
              .path=${0}
            ></ha-svg-icon>
          `),e.icon_path):(0,s.dy)(V||(V=H`
            <ha-floor-icon
              slot="start"
              .floor=${0}
              style="margin: 0 4px"
            ></ha-floor-icon>
          `),e.floor),e.primary),this._getItems=()=>this._getFloors(this.hass.floors,this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeFloors),this._allFloorNames=(0,r.Z)((e=>Object.values(e).map((e=>{var t;return null===(t=(0,d.r)(e))||void 0===t?void 0:t.toLowerCase()})).filter(Boolean))),this._getAdditionalItems=e=>{if(this.noAdd)return[];const t=this._allFloorNames(this.hass.floors);return e&&!t.includes(e.toLowerCase())?[{id:z+e,primary:this.hass.localize("ui.components.floor-picker.add_new_sugestion",{name:e}),icon_path:C}]:[{id:z,primary:this.hass.localize("ui.components.floor-picker.add_new"),icon_path:C}]}}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],k.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)()],k.prototype,"label",void 0),(0,a.__decorate)([(0,o.Cb)()],k.prototype,"value",void 0),(0,a.__decorate)([(0,o.Cb)()],k.prototype,"helper",void 0),(0,a.__decorate)([(0,o.Cb)()],k.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean,attribute:"no-add"})],k.prototype,"noAdd",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"include-domains"})],k.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-domains"})],k.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"include-device-classes"})],k.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-floors"})],k.prototype,"excludeFloors",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],k.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],k.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],k.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],k.prototype,"required",void 0),(0,a.__decorate)([(0,o.IO)("ha-generic-picker")],k.prototype,"_picker",void 0),k=(0,a.__decorate)([(0,o.Mo)("ha-floor-picker")],k),t()}catch(v){t(v)}}))},98903:function(e,t,i){i.d(t,{N5:()=>s,z3:()=>a});i(26847),i(2394),i(87799),i(27530),i(92949),i(96110);const a=(e,t)=>e.callWS(Object.assign({type:"config/floor_registry/create"},t)),s=e=>{const t={};for(const i of e)i.floor_id&&(i.floor_id in t||(t[i.floor_id]=[]),t[i.floor_id].push(i));return t}},58528:function(e,t,i){i.d(t,{Ft:()=>a,S$:()=>s,sy:()=>o});i(1455);const a="timestamp",s="temperature",o="humidity"},2460:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);i(26847),i(1455),i(20655),i(27530);var s=i(73742),o=i(59048),r=i(7616),l=i(29740),n=(i(22543),i(94262),i(73186)),d=(i(14891),i(79760)),h=i(39711),c=(i(38573),i(19442)),_=i(57108),u=i(77204),p=i(58528),y=i(81665),m=i(99298),v=e([n,d,h,c]);[n,d,h,c]=v.then?(await v)():v;let g,f,b,$,V,H,C,x,z=e=>e;const k={round:!1,type:"image/jpeg",quality:.75,aspectRatio:1.78},L=["sensor"],A=[p.S$],E=[p.sy];class w extends o.oi{async showDialog(e){this._params=e,this._error=void 0,this._params.entry?(this._name=this._params.entry.name,this._aliases=this._params.entry.aliases,this._labels=this._params.entry.labels,this._picture=this._params.entry.picture,this._icon=this._params.entry.icon,this._floor=this._params.entry.floor_id,this._temperatureEntity=this._params.entry.temperature_entity_id,this._humidityEntity=this._params.entry.humidity_entity_id):(this._name=this._params.suggestedName||"",this._aliases=[],this._labels=[],this._picture=null,this._icon=null,this._floor=null,this._temperatureEntity=null,this._humidityEntity=null),await this.updateComplete}closeDialog(){this._error="",this._params=void 0,(0,l.B)(this,"dialog-closed",{dialog:this.localName})}_renderSettings(e){return(0,o.dy)(g||(g=z`
      ${0}

      <ha-textfield
        .value=${0}
        @input=${0}
        .label=${0}
        .validationMessage=${0}
        required
        dialogInitialFocus
      ></ha-textfield>

      <ha-icon-picker
        .hass=${0}
        .value=${0}
        @value-changed=${0}
        .label=${0}
      ></ha-icon-picker>

      <ha-floor-picker
        .hass=${0}
        .value=${0}
        @value-changed=${0}
        .label=${0}
      ></ha-floor-picker>

      <ha-labels-picker
        .hass=${0}
        .value=${0}
        @value-changed=${0}
        .placeholder=${0}
      ></ha-labels-picker>

      <ha-picture-upload
        .hass=${0}
        .value=${0}
        crop
        select-media
        .cropOptions=${0}
        @change=${0}
      ></ha-picture-upload>
    `),e?(0,o.dy)(f||(f=z`
            <ha-settings-row>
              <span slot="heading">
                ${0}
              </span>
              <span slot="description"> ${0} </span>
            </ha-settings-row>
          `),this.hass.localize("ui.panel.config.areas.editor.area_id"),e.area_id):o.Ld,this._name,this._nameChanged,this.hass.localize("ui.panel.config.areas.editor.name"),this.hass.localize("ui.panel.config.areas.editor.name_required"),this.hass,this._icon,this._iconChanged,this.hass.localize("ui.panel.config.areas.editor.icon"),this.hass,this._floor,this._floorChanged,this.hass.localize("ui.panel.config.areas.editor.floor"),this.hass,this._labels,this._labelsChanged,this.hass.localize("ui.panel.config.areas.editor.add_labels"),this.hass,this._picture,k,this._pictureChanged)}_renderAliasExpansion(){return(0,o.dy)(b||(b=z`
      <ha-expansion-panel
        outlined
        .header=${0}
        expanded
      >
        <div class="content">
          <p class="description">
            ${0}
          </p>
          <ha-aliases-editor
            .hass=${0}
            .aliases=${0}
            @value-changed=${0}
          ></ha-aliases-editor>
        </div>
      </ha-expansion-panel>
    `),this.hass.localize("ui.panel.config.areas.editor.aliases_section"),this.hass.localize("ui.panel.config.areas.editor.aliases_description"),this.hass,this._aliases,this._aliasesChanged)}_renderRelatedEntitiesExpansion(){return(0,o.dy)($||($=z`
      <ha-expansion-panel
        outlined
        .header=${0}
        expanded
      >
        <div class="content">
          <ha-entity-picker
            .hass=${0}
            .label=${0}
            .helper=${0}
            .value=${0}
            .includeDomains=${0}
            .includeDeviceClasses=${0}
            .entityFilter=${0}
            @value-changed=${0}
          ></ha-entity-picker>

          <ha-entity-picker
            .hass=${0}
            .label=${0}
            .helper=${0}
            .value=${0}
            .includeDomains=${0}
            .includeDeviceClasses=${0}
            .entityFilter=${0}
            @value-changed=${0}
          ></ha-entity-picker>
        </div>
      </ha-expansion-panel>
    `),this.hass.localize("ui.panel.config.areas.editor.related_entities_section"),this.hass,this.hass.localize("ui.panel.config.areas.editor.temperature_entity"),this.hass.localize("ui.panel.config.areas.editor.temperature_entity_description"),this._temperatureEntity,L,A,this._areaEntityFilter,this._sensorChanged,this.hass,this.hass.localize("ui.panel.config.areas.editor.humidity_entity"),this.hass.localize("ui.panel.config.areas.editor.humidity_entity_description"),this._humidityEntity,L,E,this._areaEntityFilter,this._sensorChanged)}render(){if(!this._params)return o.Ld;const e=this._params.entry,t=!this._isNameValid(),i=!e;return(0,o.dy)(V||(V=z`
      <ha-dialog
        open
        @closed=${0}
        .heading=${0}
      >
        <div>
          ${0}
          <div class="form">
            ${0} ${0}
            ${0}
          </div>
        </div>
        ${0}
        <div slot="primaryAction">
          <ha-button @click=${0}>
            ${0}
          </ha-button>
          <ha-button
            @click=${0}
            .disabled=${0}
          >
            ${0}
          </ha-button>
        </div>
      </ha-dialog>
    `),this.closeDialog,(0,m.i)(this.hass,e?this.hass.localize("ui.panel.config.areas.editor.update_area"):this.hass.localize("ui.panel.config.areas.editor.create_area")),this._error?(0,o.dy)(H||(H=z`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):"",this._renderSettings(e),this._renderAliasExpansion(),i?o.Ld:this._renderRelatedEntitiesExpansion(),i?o.Ld:(0,o.dy)(C||(C=z`<ha-button
              slot="secondaryAction"
              destructive
              @click=${0}
            >
              ${0}
            </ha-button>`),this._deleteArea,this.hass.localize("ui.common.delete")),this.closeDialog,this.hass.localize("ui.common.cancel"),this._updateEntry,t||this._submitting,e?this.hass.localize("ui.common.save"):this.hass.localize("ui.common.create"))}_isNameValid(){return""!==this._name.trim()}_nameChanged(e){this._error=void 0,this._name=e.target.value}_floorChanged(e){this._error=void 0,this._floor=e.detail.value}_iconChanged(e){this._error=void 0,this._icon=e.detail.value}_labelsChanged(e){this._error=void 0,this._labels=e.detail.value}_pictureChanged(e){this._error=void 0,this._picture=e.target.value}_aliasesChanged(e){this._aliases=e.detail.value}_sensorChanged(e){this[`_${e.target.includeDeviceClasses[0]}Entity`]=e.detail.value||null}async _updateEntry(){const e=!this._params.entry;this._submitting=!0;try{const t={name:this._name.trim(),picture:this._picture||(e?void 0:null),icon:this._icon||(e?void 0:null),floor_id:this._floor||(e?void 0:null),labels:this._labels||null,aliases:this._aliases,temperature_entity_id:this._temperatureEntity,humidity_entity_id:this._humidityEntity};e?await this._params.createEntry(t):await this._params.updateEntry(t),this.closeDialog()}catch(t){this._error=t.message||this.hass.localize("ui.panel.config.areas.editor.unknown_error")}finally{this._submitting=!1}}async _deleteArea(){var e;if(null===(e=this._params)||void 0===e||!e.entry)return;await(0,y.g7)(this,{title:this.hass.localize("ui.panel.config.areas.delete.confirmation_title",{name:this._params.entry.name}),text:this.hass.localize("ui.panel.config.areas.delete.confirmation_text"),dismissText:this.hass.localize("ui.common.cancel"),confirmText:this.hass.localize("ui.common.delete"),destructive:!0})&&(await(0,_.qv)(this.hass,this._params.entry.area_id),this.closeDialog())}static get styles(){return[u.yu,(0,o.iv)(x||(x=z`
        ha-textfield {
          display: block;
        }
        ha-expansion-panel {
          --expansion-panel-content-padding: 0;
        }
        ha-aliases-editor,
        ha-entity-picker,
        ha-floor-picker,
        ha-icon-picker,
        ha-labels-picker,
        ha-picture-upload,
        ha-expansion-panel {
          display: block;
          margin-bottom: 16px;
        }
        ha-dialog {
          --mdc-dialog-min-width: min(600px, 100vw);
        }
        .content {
          padding: 12px;
        }
        .description {
          margin: 0 0 16px 0;
        }
      `))]}constructor(...e){super(...e),this._areaEntityFilter=e=>{const t=this.hass.entities[e.entity_id];if(!t)return!1;const i=this._params.entry.area_id;if(t.area_id===i)return!0;if(!t.device_id)return!1;const a=this.hass.devices[t.device_id];return a&&a.area_id===i}}}(0,s.__decorate)([(0,r.Cb)({attribute:!1})],w.prototype,"hass",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_name",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_aliases",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_labels",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_picture",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_icon",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_floor",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_temperatureEntity",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_humidityEntity",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_error",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_params",void 0),(0,s.__decorate)([(0,r.SB)()],w.prototype,"_submitting",void 0),customElements.define("dialog-area-registry-detail",w),a()}catch(g){a(g)}}))},5460:function(e,t,i){i.d(t,{y:()=>o});i(26847),i(1455),i(27530);var a=i(29740);const s=()=>Promise.all([i.e("7530"),i.e("9740")]).then(i.bind(i,21520)),o=(e,t)=>{(0,a.B)(e,"show-dialog",{dialogTag:"dialog-floor-registry-detail",dialogImport:s,dialogParams:t})}}}]);
//# sourceMappingURL=1278.76d679b0c02a57b1.js.map