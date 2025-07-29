"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9607"],{1166:function(t,i,e){e.r(i);e(26847),e(87799),e(1455),e(27530);var o=e(73742),s=e(59048),a=e(7616),n=e(88245),l=e(29740),d=(e(30337),e(78645),e(39651),e(93795),e(48374),e(38573),e(81665)),r=e(77204);let h,c,p,u,_=t=>t;class g extends s.oi{_optionMoved(t){t.stopPropagation();const{oldIndex:i,newIndex:e}=t.detail,o=this._options.concat(),s=o.splice(i,1)[0];o.splice(e,0,s),(0,l.B)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{options:o})})}set item(t){this._item=t,t?(this._name=t.name||"",this._icon=t.icon||"",this._options=t.options||[]):(this._name="",this._icon="",this._options=[])}focus(){this.updateComplete.then((()=>{var t;return null===(t=this.shadowRoot)||void 0===t||null===(t=t.querySelector("[dialogInitialFocus]"))||void 0===t?void 0:t.focus()}))}render(){return this.hass?(0,s.dy)(h||(h=_`
      <div class="form">
        <ha-textfield
          dialogInitialFocus
          autoValidate
          required
          .validationMessage=${0}
          .value=${0}
          .label=${0}
          .configValue=${0}
          @input=${0}
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
        ></ha-icon-picker>
        <div class="header">
          ${0}:
        </div>
        <ha-sortable @item-moved=${0} handle-selector=".handle">
          <ha-list class="options">
            ${0}
          </ha-list>
        </ha-sortable>
        <div class="layout horizontal center">
          <ha-textfield
            class="flex-auto"
            id="option_input"
            .label=${0}
            @keydown=${0}
          ></ha-textfield>
          <ha-button @click=${0}
            >${0}</ha-button
          >
        </div>
      </div>
    `),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this._name,this.hass.localize("ui.dialogs.helper_settings.generic.name"),"name",this._valueChanged,this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this.hass.localize("ui.dialogs.helper_settings.input_select.options"),this._optionMoved,this._options.length?(0,n.r)(this._options,(t=>t),((t,i)=>(0,s.dy)(c||(c=_`
                    <ha-list-item class="option" hasMeta>
                      <div class="optioncontent">
                        <div class="handle">
                          <ha-svg-icon .path=${0}></ha-svg-icon>
                        </div>
                        ${0}
                      </div>
                      <ha-icon-button
                        slot="meta"
                        .index=${0}
                        .label=${0}
                        @click=${0}
                        .path=${0}
                      ></ha-icon-button>
                    </ha-list-item>
                  `),"M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z",t,i,this.hass.localize("ui.dialogs.helper_settings.input_select.remove_option"),this._removeOption,"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"))):(0,s.dy)(p||(p=_`
                  <ha-list-item noninteractive>
                    ${0}
                  </ha-list-item>
                `),this.hass.localize("ui.dialogs.helper_settings.input_select.no_options")),this.hass.localize("ui.dialogs.helper_settings.input_select.add_option"),this._handleKeyAdd,this._addOption,this.hass.localize("ui.dialogs.helper_settings.input_select.add")):s.Ld}_handleKeyAdd(t){t.stopPropagation(),"Enter"===t.key&&this._addOption()}_addOption(){const t=this._optionInput;null!=t&&t.value&&((0,l.B)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{options:[...this._options,t.value]})}),t.value="")}async _removeOption(t){const i=t.target.index;if(!(await(0,d.g7)(this,{title:this.hass.localize("ui.dialogs.helper_settings.input_select.confirm_delete.delete"),text:this.hass.localize("ui.dialogs.helper_settings.input_select.confirm_delete.prompt"),destructive:!0})))return;const e=[...this._options];e.splice(i,1),(0,l.B)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{options:e})})}_valueChanged(t){var i;if(!this.new&&!this._item)return;t.stopPropagation();const e=t.target.configValue,o=(null===(i=t.detail)||void 0===i?void 0:i.value)||t.target.value;if(this[`_${e}`]===o)return;const s=Object.assign({},this._item);o?s[e]=o:delete s[e],(0,l.B)(this,"value-changed",{value:s})}static get styles(){return[r.Qx,(0,s.iv)(u||(u=_`
        .form {
          color: var(--primary-text-color);
        }
        .option {
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          margin-top: 4px;
          --mdc-icon-button-size: 24px;
          --mdc-ripple-color: transparent;
          --mdc-list-side-padding: 16px;
          cursor: default;
          background-color: var(--card-background-color);
        }
        mwc-button {
          margin-left: 8px;
          margin-inline-start: 8px;
          margin-inline-end: initial;
        }
        ha-textfield {
          display: block;
          margin-bottom: 8px;
        }
        #option_input {
          margin-top: 8px;
        }
        .header {
          margin-top: 8px;
          margin-bottom: 8px;
        }
        .handle {
          cursor: move; /* fallback if grab cursor is unsupported */
          cursor: grab;
          padding-right: 12px;
          padding-inline-end: 12px;
          padding-inline-start: initial;
        }
        .handle ha-svg-icon {
          pointer-events: none;
          height: 24px;
        }
        .optioncontent {
          display: flex;
          align-items: center;
        }
      `))]}constructor(...t){super(...t),this.new=!1,this._options=[]}}(0,o.__decorate)([(0,a.Cb)({attribute:!1})],g.prototype,"hass",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean})],g.prototype,"new",void 0),(0,o.__decorate)([(0,a.SB)()],g.prototype,"_name",void 0),(0,o.__decorate)([(0,a.SB)()],g.prototype,"_icon",void 0),(0,o.__decorate)([(0,a.SB)()],g.prototype,"_options",void 0),(0,o.__decorate)([(0,a.IO)("#option_input",!0)],g.prototype,"_optionInput",void 0),g=(0,o.__decorate)([(0,a.Mo)("ha-input_select-form")],g)}}]);
//# sourceMappingURL=9607.6cc63bbc43b1c4c5.js.map