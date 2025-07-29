export const __webpack_ids__=["2296"];export const __webpack_modules__={6184:function(e,i,t){t.r(i);var a=t(73742),s=t(59048),o=t(7616),l=t(29740),n=(t(86932),t(4820),t(38573),t(77204));class r extends s.oi{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._maximum=e.maximum??void 0,this._minimum=e.minimum??void 0,this._restore=e.restore??!0,this._step=e.step??1,this._initial=e.initial??0):(this._name="",this._icon="",this._maximum=void 0,this._minimum=void 0,this._restore=!0,this._step=1,this._initial=0)}focus(){this.updateComplete.then((()=>this.shadowRoot?.querySelector("[dialogInitialFocus]")?.focus()))}render(){return this.hass?s.dy`
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
          .value=${this._minimum}
          .configValue=${"minimum"}
          type="number"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.counter.minimum")}
        ></ha-textfield>
        <ha-textfield
          .value=${this._maximum}
          .configValue=${"maximum"}
          type="number"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.counter.maximum")}
        ></ha-textfield>
        <ha-textfield
          .value=${this._initial}
          .configValue=${"initial"}
          type="number"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.counter.initial")}
        ></ha-textfield>
        <ha-expansion-panel
          header=${this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings")}
          outlined
        >
          <ha-textfield
            .value=${this._step}
            .configValue=${"step"}
            type="number"
            @input=${this._valueChanged}
            .label=${this.hass.localize("ui.dialogs.helper_settings.counter.step")}
          ></ha-textfield>
          <div class="row">
            <ha-switch
              .checked=${this._restore}
              .configValue=${"restore"}
              @change=${this._valueChanged}
            >
            </ha-switch>
            <div>
              ${this.hass.localize("ui.dialogs.helper_settings.counter.restore")}
            </div>
          </div>
        </ha-expansion-panel>
      </div>
    `:s.Ld}_valueChanged(e){if(!this.new&&!this._item)return;e.stopPropagation();const i=e.target,t=i.configValue,a="number"===i.type?""!==i.value?Number(i.value):void 0:"ha-switch"===i.localName?e.target.checked:e.detail?.value||i.value;if(this[`_${t}`]===a)return;const s={...this._item};void 0===a||""===a?delete s[t]:s[t]=a,(0,l.B)(this,"value-changed",{value:s})}static get styles(){return[n.Qx,s.iv`
        .form {
          color: var(--primary-text-color);
        }
        .row {
          margin-top: 12px;
          margin-bottom: 12px;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
        }
        .row div {
          margin-left: 16px;
          margin-inline-start: 16px;
          margin-inline-end: initial;
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `]}constructor(...e){super(...e),this.new=!1}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],r.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],r.prototype,"new",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_name",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_icon",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_maximum",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_minimum",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_restore",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_initial",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_step",void 0),r=(0,a.__decorate)([(0,o.Mo)("ha-counter-form")],r)}};
//# sourceMappingURL=2296.3f67f2b73a864f26.js.map