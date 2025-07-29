export const __webpack_ids__=["1278"];export const __webpack_modules__={94262:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),r=i(29740);i(24340);class l extends s.oi{render(){return this.aliases?s.dy`
      <ha-multi-textfield
        .hass=${this.hass}
        .value=${this.aliases}
        .disabled=${this.disabled}
        .label=${this.hass.localize("ui.dialogs.aliases.label")}
        .removeLabel=${this.hass.localize("ui.dialogs.aliases.remove")}
        .addLabel=${this.hass.localize("ui.dialogs.aliases.add")}
        item-index
        @value-changed=${this._aliasesChanged}
      >
      </ha-multi-textfield>
    `:s.Ld}_aliasesChanged(e){(0,r.B)(this,"value-changed",{value:e})}constructor(...e){super(...e),this.disabled=!1}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array})],l.prototype,"aliases",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],l.prototype,"disabled",void 0),l=(0,a.__decorate)([(0,o.Mo)("ha-aliases-editor")],l)},86026:function(e,t,i){i.d(t,{m:()=>r});var a=i(73742),s=i(59048),o=i(7616);i(40830);const r=e=>{switch(e.level){case 0:return"M11,10H13V16H11V10M22,12H19V20H5V12H2L12,3L22,12M15,10A2,2 0 0,0 13,8H11A2,2 0 0,0 9,10V16A2,2 0 0,0 11,18H13A2,2 0 0,0 15,16V10Z";case 1:return"M12,3L2,12H5V20H19V12H22L12,3M10,8H14V18H12V10H10V8Z";case 2:return"M12,3L2,12H5V20H19V12H22L12,3M9,8H13A2,2 0 0,1 15,10V12A2,2 0 0,1 13,14H11V16H15V18H9V14A2,2 0 0,1 11,12H13V10H9V8Z";case 3:return"M12,3L22,12H19V20H5V12H2L12,3M15,11.5V10C15,8.89 14.1,8 13,8H9V10H13V12H11V14H13V16H9V18H13A2,2 0 0,0 15,16V14.5A1.5,1.5 0 0,0 13.5,13A1.5,1.5 0 0,0 15,11.5Z";case-1:return"M12,3L2,12H5V20H19V12H22L12,3M11,15H7V13H11V15M15,18H13V10H11V8H15V18Z"}return"M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"};class l extends s.oi{render(){if(this.floor.icon)return s.dy`<ha-icon .icon=${this.floor.icon}></ha-icon>`;const e=r(this.floor);return s.dy`<ha-svg-icon .path=${e}></ha-svg-icon>`}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],l.prototype,"floor",void 0),(0,a.__decorate)([(0,o.Cb)()],l.prototype,"icon",void 0),l=(0,a.__decorate)([(0,o.Mo)("ha-floor-icon")],l)},10600:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),r=i(28105),l=i(29740),n=i(76151),d=i(41099),h=i(57108),c=i(51729),_=i(98903),p=i(81665);const u=()=>Promise.all([i.e("9278"),i.e("428")]).then(i.bind(i,21520));i(57264),i(86026),i(75691),i(78645),i(40830);const y="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",m="___ADD_NEW___";class g extends s.oi{async open(){await this.updateComplete,await(this._picker?.open())}render(){const e=this.placeholder??this.hass.localize("ui.components.floor-picker.floor"),t=this._computeValueRenderer(this.hass.floors);return s.dy`
      <ha-generic-picker
        .hass=${this.hass}
        .autofocus=${this.autofocus}
        .label=${this.label}
        .notFoundLabel=${this.hass.localize("ui.components.floor-picker.no_match")}
        .placeholder=${e}
        .value=${this.value}
        .getItems=${this._getItems}
        .getAdditionalItems=${this._getAdditionalItems}
        .valueRenderer=${t}
        .rowRenderer=${this._rowRenderer}
        @value-changed=${this._valueChanged}
      >
      </ha-generic-picker>
    `}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t){if(t.startsWith(m)){this.hass.loadFragmentTranslation("config");const e=t.substring(13);i=this,a={suggestedName:e,createEntry:async(e,t)=>{try{const i=await(0,_.z3)(this.hass,e);t.forEach((e=>{(0,h.IO)(this.hass,e,{floor_id:i.floor_id})})),this._setValue(i.floor_id)}catch(i){(0,p.Ys)(this,{title:this.hass.localize("ui.components.floor-picker.failed_create_floor"),text:i.message})}}},(0,l.B)(i,"show-dialog",{dialogTag:"dialog-floor-registry-detail",dialogImport:u,dialogParams:a})}var i,a;this._setValue(t)}else this._setValue(void 0)}_setValue(e){this.value=e,(0,l.B)(this,"value-changed",{value:e}),(0,l.B)(this,"change")}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._computeValueRenderer=(0,r.Z)((e=>e=>{const t=this.hass.floors[e];if(!t)return s.dy`
            <ha-svg-icon slot="start" .path=${"M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z"}></ha-svg-icon>
            <span slot="headline">${t}</span>
          `;const i=t?(0,d.r)(t):void 0;return s.dy`
          <ha-floor-icon slot="start" .floor=${t}></ha-floor-icon>
          <span slot="headline">${i}</span>
        `})),this._getFloors=(0,r.Z)(((e,t,i,a,s,o,r,l,h,p)=>{const u=Object.values(e),y=Object.values(t),m=Object.values(i),g=Object.values(a);let v,f,b={};(s||o||r||l||h)&&(b=(0,c.R6)(g),v=m,f=g.filter((e=>e.area_id)),s&&(v=v.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>s.includes((0,n.M)(e.entity_id))))})),f=f.filter((e=>s.includes((0,n.M)(e.entity_id))))),o&&(v=v.filter((e=>{const t=b[e.id];return!t||!t.length||g.every((e=>!o.includes((0,n.M)(e.entity_id))))})),f=f.filter((e=>!o.includes((0,n.M)(e.entity_id))))),r&&(v=v.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))})),f=f.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&r.includes(t.attributes.device_class)}))),l&&(v=v.filter((e=>l(e)))),h&&(v=v.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&h(t)}))})),f=f.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&h(t)}))));let $,V=u;if(v&&($=v.filter((e=>e.area_id)).map((e=>e.area_id))),f&&($=($??[]).concat(f.filter((e=>e.area_id)).map((e=>e.area_id)))),$){const e=(0,_.N5)(y);V=V.filter((t=>e[t.floor_id]?.some((e=>$.includes(e.area_id)))))}p&&(V=V.filter((e=>!p.includes(e.floor_id))));return V.map((e=>{const t=(0,d.r)(e);return{id:e.floor_id,primary:t,floor:e,sorting_label:e.level?.toString()||"zzzzz",search_labels:[t,e.floor_id,...e.aliases].filter((e=>Boolean(e)))}}))})),this._rowRenderer=e=>s.dy`
    <ha-combo-box-item type="button" compact>
      ${e.icon_path?s.dy`
            <ha-svg-icon
              slot="start"
              style="margin: 0 4px"
              .path=${e.icon_path}
            ></ha-svg-icon>
          `:s.dy`
            <ha-floor-icon
              slot="start"
              .floor=${e.floor}
              style="margin: 0 4px"
            ></ha-floor-icon>
          `}
      <span slot="headline">${e.primary}</span>
    </ha-combo-box-item>
  `,this._getItems=()=>this._getFloors(this.hass.floors,this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeFloors),this._allFloorNames=(0,r.Z)((e=>Object.values(e).map((e=>(0,d.r)(e)?.toLowerCase())).filter(Boolean))),this._getAdditionalItems=e=>{if(this.noAdd)return[];const t=this._allFloorNames(this.hass.floors);return e&&!t.includes(e.toLowerCase())?[{id:m+e,primary:this.hass.localize("ui.components.floor-picker.add_new_sugestion",{name:e}),icon_path:y}]:[{id:m,primary:this.hass.localize("ui.components.floor-picker.add_new"),icon_path:y}]}}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],g.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)()],g.prototype,"label",void 0),(0,a.__decorate)([(0,o.Cb)()],g.prototype,"value",void 0),(0,a.__decorate)([(0,o.Cb)()],g.prototype,"helper",void 0),(0,a.__decorate)([(0,o.Cb)()],g.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean,attribute:"no-add"})],g.prototype,"noAdd",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"include-domains"})],g.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-domains"})],g.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"include-device-classes"})],g.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-floors"})],g.prototype,"excludeFloors",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],g.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],g.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],g.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],g.prototype,"required",void 0),(0,a.__decorate)([(0,o.IO)("ha-generic-picker")],g.prototype,"_picker",void 0),g=(0,a.__decorate)([(0,o.Mo)("ha-floor-picker")],g)},98903:function(e,t,i){i.d(t,{N5:()=>s,z3:()=>a});i(92949),i(96110);const a=(e,t)=>e.callWS({type:"config/floor_registry/create",...t}),s=e=>{const t={};for(const i of e)i.floor_id&&(i.floor_id in t||(t[i.floor_id]=[]),t[i.floor_id].push(i));return t}},58528:function(e,t,i){i.d(t,{Ft:()=>a,S$:()=>s,sy:()=>o});const a="timestamp",s="temperature",o="humidity"},2460:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);var s=i(73742),o=i(59048),r=i(7616),l=i(29740),n=(i(22543),i(94262),i(19728),i(14891),i(10600),i(39711)),d=(i(38573),i(19442),i(57108)),h=i(77204),c=i(58528),_=i(81665),p=i(99298),u=e([n]);n=(u.then?(await u)():u)[0];const y={round:!1,type:"image/jpeg",quality:.75,aspectRatio:1.78},m=["sensor"],g=[c.S$],v=[c.sy];class f extends o.oi{async showDialog(e){this._params=e,this._error=void 0,this._params.entry?(this._name=this._params.entry.name,this._aliases=this._params.entry.aliases,this._labels=this._params.entry.labels,this._picture=this._params.entry.picture,this._icon=this._params.entry.icon,this._floor=this._params.entry.floor_id,this._temperatureEntity=this._params.entry.temperature_entity_id,this._humidityEntity=this._params.entry.humidity_entity_id):(this._name=this._params.suggestedName||"",this._aliases=[],this._labels=[],this._picture=null,this._icon=null,this._floor=null,this._temperatureEntity=null,this._humidityEntity=null),await this.updateComplete}closeDialog(){this._error="",this._params=void 0,(0,l.B)(this,"dialog-closed",{dialog:this.localName})}_renderSettings(e){return o.dy`
      ${e?o.dy`
            <ha-settings-row>
              <span slot="heading">
                ${this.hass.localize("ui.panel.config.areas.editor.area_id")}
              </span>
              <span slot="description"> ${e.area_id} </span>
            </ha-settings-row>
          `:o.Ld}

      <ha-textfield
        .value=${this._name}
        @input=${this._nameChanged}
        .label=${this.hass.localize("ui.panel.config.areas.editor.name")}
        .validationMessage=${this.hass.localize("ui.panel.config.areas.editor.name_required")}
        required
        dialogInitialFocus
      ></ha-textfield>

      <ha-icon-picker
        .hass=${this.hass}
        .value=${this._icon}
        @value-changed=${this._iconChanged}
        .label=${this.hass.localize("ui.panel.config.areas.editor.icon")}
      ></ha-icon-picker>

      <ha-floor-picker
        .hass=${this.hass}
        .value=${this._floor}
        @value-changed=${this._floorChanged}
        .label=${this.hass.localize("ui.panel.config.areas.editor.floor")}
      ></ha-floor-picker>

      <ha-labels-picker
        .hass=${this.hass}
        .value=${this._labels}
        @value-changed=${this._labelsChanged}
        .placeholder=${this.hass.localize("ui.panel.config.areas.editor.add_labels")}
      ></ha-labels-picker>

      <ha-picture-upload
        .hass=${this.hass}
        .value=${this._picture}
        crop
        select-media
        .cropOptions=${y}
        @change=${this._pictureChanged}
      ></ha-picture-upload>
    `}_renderAliasExpansion(){return o.dy`
      <ha-expansion-panel
        outlined
        .header=${this.hass.localize("ui.panel.config.areas.editor.aliases_section")}
        expanded
      >
        <div class="content">
          <p class="description">
            ${this.hass.localize("ui.panel.config.areas.editor.aliases_description")}
          </p>
          <ha-aliases-editor
            .hass=${this.hass}
            .aliases=${this._aliases}
            @value-changed=${this._aliasesChanged}
          ></ha-aliases-editor>
        </div>
      </ha-expansion-panel>
    `}_renderRelatedEntitiesExpansion(){return o.dy`
      <ha-expansion-panel
        outlined
        .header=${this.hass.localize("ui.panel.config.areas.editor.related_entities_section")}
        expanded
      >
        <div class="content">
          <ha-entity-picker
            .hass=${this.hass}
            .label=${this.hass.localize("ui.panel.config.areas.editor.temperature_entity")}
            .helper=${this.hass.localize("ui.panel.config.areas.editor.temperature_entity_description")}
            .value=${this._temperatureEntity}
            .includeDomains=${m}
            .includeDeviceClasses=${g}
            .entityFilter=${this._areaEntityFilter}
            @value-changed=${this._sensorChanged}
          ></ha-entity-picker>

          <ha-entity-picker
            .hass=${this.hass}
            .label=${this.hass.localize("ui.panel.config.areas.editor.humidity_entity")}
            .helper=${this.hass.localize("ui.panel.config.areas.editor.humidity_entity_description")}
            .value=${this._humidityEntity}
            .includeDomains=${m}
            .includeDeviceClasses=${v}
            .entityFilter=${this._areaEntityFilter}
            @value-changed=${this._sensorChanged}
          ></ha-entity-picker>
        </div>
      </ha-expansion-panel>
    `}render(){if(!this._params)return o.Ld;const e=this._params.entry,t=!this._isNameValid(),i=!e;return o.dy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        .heading=${(0,p.i)(this.hass,e?this.hass.localize("ui.panel.config.areas.editor.update_area"):this.hass.localize("ui.panel.config.areas.editor.create_area"))}
      >
        <div>
          ${this._error?o.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
          <div class="form">
            ${this._renderSettings(e)} ${this._renderAliasExpansion()}
            ${i?o.Ld:this._renderRelatedEntitiesExpansion()}
          </div>
        </div>
        ${i?o.Ld:o.dy`<ha-button
              slot="secondaryAction"
              destructive
              @click=${this._deleteArea}
            >
              ${this.hass.localize("ui.common.delete")}
            </ha-button>`}
        <div slot="primaryAction">
          <ha-button @click=${this.closeDialog}>
            ${this.hass.localize("ui.common.cancel")}
          </ha-button>
          <ha-button
            @click=${this._updateEntry}
            .disabled=${t||this._submitting}
          >
            ${e?this.hass.localize("ui.common.save"):this.hass.localize("ui.common.create")}
          </ha-button>
        </div>
      </ha-dialog>
    `}_isNameValid(){return""!==this._name.trim()}_nameChanged(e){this._error=void 0,this._name=e.target.value}_floorChanged(e){this._error=void 0,this._floor=e.detail.value}_iconChanged(e){this._error=void 0,this._icon=e.detail.value}_labelsChanged(e){this._error=void 0,this._labels=e.detail.value}_pictureChanged(e){this._error=void 0,this._picture=e.target.value}_aliasesChanged(e){this._aliases=e.detail.value}_sensorChanged(e){this[`_${e.target.includeDeviceClasses[0]}Entity`]=e.detail.value||null}async _updateEntry(){const e=!this._params.entry;this._submitting=!0;try{const t={name:this._name.trim(),picture:this._picture||(e?void 0:null),icon:this._icon||(e?void 0:null),floor_id:this._floor||(e?void 0:null),labels:this._labels||null,aliases:this._aliases,temperature_entity_id:this._temperatureEntity,humidity_entity_id:this._humidityEntity};e?await this._params.createEntry(t):await this._params.updateEntry(t),this.closeDialog()}catch(t){this._error=t.message||this.hass.localize("ui.panel.config.areas.editor.unknown_error")}finally{this._submitting=!1}}async _deleteArea(){if(!this._params?.entry)return;await(0,_.g7)(this,{title:this.hass.localize("ui.panel.config.areas.delete.confirmation_title",{name:this._params.entry.name}),text:this.hass.localize("ui.panel.config.areas.delete.confirmation_text"),dismissText:this.hass.localize("ui.common.cancel"),confirmText:this.hass.localize("ui.common.delete"),destructive:!0})&&(await(0,d.qv)(this.hass,this._params.entry.area_id),this.closeDialog())}static get styles(){return[h.yu,o.iv`
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
      `]}constructor(...e){super(...e),this._areaEntityFilter=e=>{const t=this.hass.entities[e.entity_id];if(!t)return!1;const i=this._params.entry.area_id;if(t.area_id===i)return!0;if(!t.device_id)return!1;const a=this.hass.devices[t.device_id];return a&&a.area_id===i}}}(0,s.__decorate)([(0,r.Cb)({attribute:!1})],f.prototype,"hass",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_name",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_aliases",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_labels",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_picture",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_icon",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_floor",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_temperatureEntity",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_humidityEntity",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_error",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_params",void 0),(0,s.__decorate)([(0,r.SB)()],f.prototype,"_submitting",void 0),customElements.define("dialog-area-registry-detail",f),a()}catch(y){a(y)}}))}};
//# sourceMappingURL=1278.732d2df8c1a3a164.js.map