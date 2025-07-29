export const __webpack_ids__=["5213"];export const __webpack_modules__={78184:function(e,t,i){i.r(t);var a=i(73742),s=i(59048),o=i(7616),l=i(29740),n=(i(86932),i(74207),i(71308),i(38573),i(77204));class h extends s.oi{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._max=e.max??100,this._min=e.min??0,this._mode=e.mode||"slider",this._step=e.step??1,this._unit_of_measurement=e.unit_of_measurement):(this._item={min:0,max:100},this._name="",this._icon="",this._max=100,this._min=0,this._mode="slider",this._step=1)}focus(){this.updateComplete.then((()=>this.shadowRoot?.querySelector("[dialogInitialFocus]")?.focus()))}render(){return this.hass?s.dy`
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
          .value=${this._min}
          .configValue=${"min"}
          type="number"
          step="any"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.input_number.min")}
        ></ha-textfield>
        <ha-textfield
          .value=${this._max}
          .configValue=${"max"}
          type="number"
          step="any"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.input_number.max")}
        ></ha-textfield>
        <ha-expansion-panel
          header=${this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings")}
          outlined
        >
          <div class="layout horizontal center justified">
            ${this.hass.localize("ui.dialogs.helper_settings.input_number.mode")}
            <ha-formfield
              .label=${this.hass.localize("ui.dialogs.helper_settings.input_number.slider")}
            >
              <ha-radio
                name="mode"
                value="slider"
                .checked=${"slider"===this._mode}
                @change=${this._modeChanged}
              ></ha-radio>
            </ha-formfield>
            <ha-formfield
              .label=${this.hass.localize("ui.dialogs.helper_settings.input_number.box")}
            >
              <ha-radio
                name="mode"
                value="box"
                .checked=${"box"===this._mode}
                @change=${this._modeChanged}
              ></ha-radio>
            </ha-formfield>
          </div>
          <ha-textfield
            .value=${this._step}
            .configValue=${"step"}
            type="number"
            step="any"
            @input=${this._valueChanged}
            .label=${this.hass.localize("ui.dialogs.helper_settings.input_number.step")}
          ></ha-textfield>

          <ha-textfield
            .value=${this._unit_of_measurement||""}
            .configValue=${"unit_of_measurement"}
            @input=${this._valueChanged}
            .label=${this.hass.localize("ui.dialogs.helper_settings.input_number.unit_of_measurement")}
          ></ha-textfield>
        </ha-expansion-panel>
      </div>
    `:s.Ld}_modeChanged(e){(0,l.B)(this,"value-changed",{value:{...this._item,mode:e.target.value}})}_valueChanged(e){if(!this.new&&!this._item)return;e.stopPropagation();const t=e.target,i=t.configValue,a="number"===t.type?Number(t.value):e.detail?.value||t.value;if(this[`_${i}`]===a)return;const s={...this._item};void 0===a||""===a?delete s[i]:s[i]=a,(0,l.B)(this,"value-changed",{value:s})}static get styles(){return[n.Qx,s.iv`
        .form {
          color: var(--primary-text-color);
        }

        ha-textfield {
          display: block;
          margin-bottom: 8px;
        }
      `]}constructor(...e){super(...e),this.new=!1}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],h.prototype,"new",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_name",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_icon",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_max",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_min",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_mode",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_step",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_unit_of_measurement",void 0),h=(0,a.__decorate)([(0,o.Mo)("ha-input_number-form")],h)}};
//# sourceMappingURL=5213.479038c3c84c64fa.js.map