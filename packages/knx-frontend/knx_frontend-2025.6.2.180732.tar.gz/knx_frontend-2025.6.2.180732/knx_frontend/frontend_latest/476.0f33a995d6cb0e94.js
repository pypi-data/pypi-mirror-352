export const __webpack_ids__=["476"];export const __webpack_modules__={26440:function(e,t,i){i.r(t);var o=i(73742),a=i(59048),s=i(7616),r=i(29740),l=(i(86776),i(74207),i(38573),i(77204));class h extends a.oi{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._duration=e.duration||"00:00:00",this._restore=e.restore||!1):(this._name="",this._icon="",this._duration="00:00:00",this._restore=!1)}focus(){this.updateComplete.then((()=>this.shadowRoot?.querySelector("[dialogInitialFocus]")?.focus()))}render(){return this.hass?a.dy`
      <div class="form">
        <ha-textfield
          .value=${this._name}
          .configValue=${"name"}
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.generic.name")}
          autoValidate
          required
          .validationMessage=${this.hass.localize("ui.dialogs.helper_settings.required_error_msg")}
          dialogInitialFocus
        ></ha-textfield>
        <ha-icon-picker
          .hass=${this.hass}
          .value=${this._icon}
          .configValue=${"icon"}
          @value-changed=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.generic.icon")}
        ></ha-icon-picker>
        <ha-textfield
          .configValue=${"duration"}
          .value=${this._duration}
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.timer.duration")}
        ></ha-textfield>
        <ha-formfield
          .label=${this.hass.localize("ui.dialogs.helper_settings.timer.restore")}
        >
          <ha-checkbox
            .configValue=${"restore"}
            .checked=${this._restore}
            @click=${this._toggleRestore}
          >
          </ha-checkbox>
        </ha-formfield>
      </div>
    `:a.Ld}_valueChanged(e){if(!this.new&&!this._item)return;e.stopPropagation();const t=e.target.configValue,i=e.detail?.value||e.target.value;if(this[`_${t}`]===i)return;const o={...this._item};i?o[t]=i:delete o[t],(0,r.B)(this,"value-changed",{value:o})}_toggleRestore(){this._restore=!this._restore,(0,r.B)(this,"value-changed",{value:{...this._item,restore:this._restore}})}static get styles(){return[l.Qx,a.iv`
        .form {
          color: var(--primary-text-color);
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `]}constructor(...e){super(...e),this.new=!1}}(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],h.prototype,"new",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_name",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_icon",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_duration",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_restore",void 0),h=(0,o.__decorate)([(0,s.Mo)("ha-timer-form")],h)}};
//# sourceMappingURL=476.0f33a995d6cb0e94.js.map