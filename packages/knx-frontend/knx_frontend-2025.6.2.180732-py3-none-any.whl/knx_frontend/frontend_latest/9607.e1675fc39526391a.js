export const __webpack_ids__=["9607"];export const __webpack_modules__={1166:function(t,i,e){e.r(i);var o=e(73742),s=e(59048),a=e(7616),n=e(88245),l=e(29740),d=(e(30337),e(78645),e(39651),e(93795),e(48374),e(38573),e(81665)),r=e(77204);class h extends s.oi{_optionMoved(t){t.stopPropagation();const{oldIndex:i,newIndex:e}=t.detail,o=this._options.concat(),s=o.splice(i,1)[0];o.splice(e,0,s),(0,l.B)(this,"value-changed",{value:{...this._item,options:o}})}set item(t){this._item=t,t?(this._name=t.name||"",this._icon=t.icon||"",this._options=t.options||[]):(this._name="",this._icon="",this._options=[])}focus(){this.updateComplete.then((()=>this.shadowRoot?.querySelector("[dialogInitialFocus]")?.focus()))}render(){return this.hass?s.dy`
      <div class="form">
        <ha-textfield
          dialogInitialFocus
          autoValidate
          required
          .validationMessage=${this.hass.localize("ui.dialogs.helper_settings.required_error_msg")}
          .value=${this._name}
          .label=${this.hass.localize("ui.dialogs.helper_settings.generic.name")}
          .configValue=${"name"}
          @input=${this._valueChanged}
        ></ha-textfield>
        <ha-icon-picker
          .hass=${this.hass}
          .value=${this._icon}
          .configValue=${"icon"}
          @value-changed=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.generic.icon")}
        ></ha-icon-picker>
        <div class="header">
          ${this.hass.localize("ui.dialogs.helper_settings.input_select.options")}:
        </div>
        <ha-sortable @item-moved=${this._optionMoved} handle-selector=".handle">
          <ha-list class="options">
            ${this._options.length?(0,n.r)(this._options,(t=>t),((t,i)=>s.dy`
                    <ha-list-item class="option" hasMeta>
                      <div class="optioncontent">
                        <div class="handle">
                          <ha-svg-icon .path=${"M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z"}></ha-svg-icon>
                        </div>
                        ${t}
                      </div>
                      <ha-icon-button
                        slot="meta"
                        .index=${i}
                        .label=${this.hass.localize("ui.dialogs.helper_settings.input_select.remove_option")}
                        @click=${this._removeOption}
                        .path=${"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"}
                      ></ha-icon-button>
                    </ha-list-item>
                  `)):s.dy`
                  <ha-list-item noninteractive>
                    ${this.hass.localize("ui.dialogs.helper_settings.input_select.no_options")}
                  </ha-list-item>
                `}
          </ha-list>
        </ha-sortable>
        <div class="layout horizontal center">
          <ha-textfield
            class="flex-auto"
            id="option_input"
            .label=${this.hass.localize("ui.dialogs.helper_settings.input_select.add_option")}
            @keydown=${this._handleKeyAdd}
          ></ha-textfield>
          <ha-button @click=${this._addOption}
            >${this.hass.localize("ui.dialogs.helper_settings.input_select.add")}</ha-button
          >
        </div>
      </div>
    `:s.Ld}_handleKeyAdd(t){t.stopPropagation(),"Enter"===t.key&&this._addOption()}_addOption(){const t=this._optionInput;t?.value&&((0,l.B)(this,"value-changed",{value:{...this._item,options:[...this._options,t.value]}}),t.value="")}async _removeOption(t){const i=t.target.index;if(!(await(0,d.g7)(this,{title:this.hass.localize("ui.dialogs.helper_settings.input_select.confirm_delete.delete"),text:this.hass.localize("ui.dialogs.helper_settings.input_select.confirm_delete.prompt"),destructive:!0})))return;const e=[...this._options];e.splice(i,1),(0,l.B)(this,"value-changed",{value:{...this._item,options:e}})}_valueChanged(t){if(!this.new&&!this._item)return;t.stopPropagation();const i=t.target.configValue,e=t.detail?.value||t.target.value;if(this[`_${i}`]===e)return;const o={...this._item};e?o[i]=e:delete o[i],(0,l.B)(this,"value-changed",{value:o})}static get styles(){return[r.Qx,s.iv`
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
      `]}constructor(...t){super(...t),this.new=!1,this._options=[]}}(0,o.__decorate)([(0,a.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean})],h.prototype,"new",void 0),(0,o.__decorate)([(0,a.SB)()],h.prototype,"_name",void 0),(0,o.__decorate)([(0,a.SB)()],h.prototype,"_icon",void 0),(0,o.__decorate)([(0,a.SB)()],h.prototype,"_options",void 0),(0,o.__decorate)([(0,a.IO)("#option_input",!0)],h.prototype,"_optionInput",void 0),h=(0,o.__decorate)([(0,a.Mo)("ha-input_select-form")],h)}};
//# sourceMappingURL=9607.e1675fc39526391a.js.map