"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5213"],{78184:function(e,i,t){t.r(i);t(26847),t(87799),t(27530);var a=t(73742),s=t(59048),o=t(7616),n=t(29740),l=(t(86932),t(74207),t(71308),t(38573),t(77204));let h,d,r=e=>e;class u extends s.oi{set item(e){var i,t,a;(this._item=e,e)?(this._name=e.name||"",this._icon=e.icon||"",this._max=null!==(i=e.max)&&void 0!==i?i:100,this._min=null!==(t=e.min)&&void 0!==t?t:0,this._mode=e.mode||"slider",this._step=null!==(a=e.step)&&void 0!==a?a:1,this._unit_of_measurement=e.unit_of_measurement):(this._item={min:0,max:100},this._name="",this._icon="",this._max=100,this._min=0,this._mode="slider",this._step=1)}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,s.dy)(h||(h=r`
      <div class="form">
        <ha-textfield
          .value=${0}
          .configValue=${0}
          @input=${0}
          .label=${0}
          autoValidate
          required
          .validationMessage=${0}
          dialogInitialFocus
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
        ></ha-icon-picker>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          step="any"
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          step="any"
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-expansion-panel
          header=${0}
          outlined
        >
          <div class="layout horizontal center justified">
            ${0}
            <ha-formfield
              .label=${0}
            >
              <ha-radio
                name="mode"
                value="slider"
                .checked=${0}
                @change=${0}
              ></ha-radio>
            </ha-formfield>
            <ha-formfield
              .label=${0}
            >
              <ha-radio
                name="mode"
                value="box"
                .checked=${0}
                @change=${0}
              ></ha-radio>
            </ha-formfield>
          </div>
          <ha-textfield
            .value=${0}
            .configValue=${0}
            type="number"
            step="any"
            @input=${0}
            .label=${0}
          ></ha-textfield>

          <ha-textfield
            .value=${0}
            .configValue=${0}
            @input=${0}
            .label=${0}
          ></ha-textfield>
        </ha-expansion-panel>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this._min,"min",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.min"),this._max,"max",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.max"),this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings"),this.hass.localize("ui.dialogs.helper_settings.input_number.mode"),this.hass.localize("ui.dialogs.helper_settings.input_number.slider"),"slider"===this._mode,this._modeChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.box"),"box"===this._mode,this._modeChanged,this._step,"step",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.step"),this._unit_of_measurement||"","unit_of_measurement",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.unit_of_measurement")):s.Ld}_modeChanged(e){(0,n.B)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{mode:e.target.value})})}_valueChanged(e){var i;if(!this.new&&!this._item)return;e.stopPropagation();const t=e.target,a=t.configValue,s="number"===t.type?Number(t.value):(null===(i=e.detail)||void 0===i?void 0:i.value)||t.value;if(this[`_${a}`]===s)return;const o=Object.assign({},this._item);void 0===s||""===s?delete o[a]:o[a]=s,(0,n.B)(this,"value-changed",{value:o})}static get styles(){return[l.Qx,(0,s.iv)(d||(d=r`
        .form {
          color: var(--primary-text-color);
        }

        ha-textfield {
          display: block;
          margin-bottom: 8px;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],u.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],u.prototype,"new",void 0),(0,a.__decorate)([(0,o.SB)()],u.prototype,"_name",void 0),(0,a.__decorate)([(0,o.SB)()],u.prototype,"_icon",void 0),(0,a.__decorate)([(0,o.SB)()],u.prototype,"_max",void 0),(0,a.__decorate)([(0,o.SB)()],u.prototype,"_min",void 0),(0,a.__decorate)([(0,o.SB)()],u.prototype,"_mode",void 0),(0,a.__decorate)([(0,o.SB)()],u.prototype,"_step",void 0),(0,a.__decorate)([(0,o.SB)()],u.prototype,"_unit_of_measurement",void 0),u=(0,a.__decorate)([(0,o.Mo)("ha-input_number-form")],u)}}]);
//# sourceMappingURL=5213.6f79fbd2c9d12d30.js.map