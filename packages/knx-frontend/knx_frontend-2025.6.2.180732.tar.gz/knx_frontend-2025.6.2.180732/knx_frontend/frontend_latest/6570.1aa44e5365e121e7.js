export const __webpack_ids__=["6570"];export const __webpack_modules__={72199:function(t,i,a){a.r(i),a.d(i,{HaImagecropperDialog:()=>h});var o=a(73742),e=(a(98334),a(27007)),r=a.n(e),s=a(93528),p=a(59048),c=a(7616),n=a(31733),_=(a(99298),a(77204));class h extends p.oi{showDialog(t){this._params=t,this._open=!0}closeDialog(){this._open=!1,this._params=void 0,this._cropper?.destroy(),this._cropper=void 0,this._isTargetAspectRatio=!1}updated(t){t.has("_params")&&this._params&&(this._cropper?this._cropper.replace(URL.createObjectURL(this._params.file)):(this._image.src=URL.createObjectURL(this._params.file),this._cropper=new(r())(this._image,{aspectRatio:this._params.options.aspectRatio,viewMode:1,dragMode:"move",minCropBoxWidth:50,ready:()=>{this._isTargetAspectRatio=this._checkMatchAspectRatio(),URL.revokeObjectURL(this._image.src)}})))}_checkMatchAspectRatio(){const t=this._params?.options.aspectRatio;if(!t)return!0;const i=this._cropper.getImageData();if(i.aspectRatio===t)return!0;if(i.naturalWidth>i.naturalHeight){const a=i.naturalWidth/t;return Math.abs(a-i.naturalHeight)<=1}const a=i.naturalHeight*t;return Math.abs(a-i.naturalWidth)<=1}render(){return p.dy`<ha-dialog
      @closed=${this.closeDialog}
      scrimClickAction
      escapeKeyAction
      .open=${this._open}
    >
      <div
        class="container ${(0,n.$)({round:Boolean(this._params?.options.round)})}"
      >
        <img alt=${this.hass.localize("ui.dialogs.image_cropper.crop_image")} />
      </div>
      <mwc-button slot="secondaryAction" @click=${this.closeDialog}>
        ${this.hass.localize("ui.common.cancel")}
      </mwc-button>
      ${this._isTargetAspectRatio?p.dy`<mwc-button slot="primaryAction" @click=${this._useOriginal}>
            ${this.hass.localize("ui.dialogs.image_cropper.use_original")}
          </mwc-button>`:p.Ld}

      <mwc-button slot="primaryAction" @click=${this._cropImage}>
        ${this.hass.localize("ui.dialogs.image_cropper.crop")}
      </mwc-button>
    </ha-dialog>`}_cropImage(){this._cropper.getCroppedCanvas().toBlob((t=>{if(!t)return;const i=new File([t],this._params.file.name,{type:this._params.options.type||this._params.file.type});this._params.croppedCallback(i),this.closeDialog()}),this._params.options.type||this._params.file.type,this._params.options.quality)}_useOriginal(){this._params.croppedCallback(this._params.file),this.closeDialog()}static get styles(){return[_.yu,p.iv`
        ${(0,p.$m)(s)}
        .container {
          max-width: 640px;
        }
        img {
          max-width: 100%;
        }
        .container.round .cropper-view-box,
        .container.round .cropper-face {
          border-radius: 50%;
        }
        .cropper-line,
        .cropper-point,
        .cropper-point.point-se::before {
          background-color: var(--primary-color);
        }
      `]}constructor(...t){super(...t),this._open=!1}}(0,o.__decorate)([(0,c.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,c.SB)()],h.prototype,"_params",void 0),(0,o.__decorate)([(0,c.SB)()],h.prototype,"_open",void 0),(0,o.__decorate)([(0,c.IO)("img",!0)],h.prototype,"_image",void 0),(0,o.__decorate)([(0,c.SB)()],h.prototype,"_isTargetAspectRatio",void 0),h=(0,o.__decorate)([(0,c.Mo)("image-cropper-dialog")],h)}};
//# sourceMappingURL=6570.1aa44e5365e121e7.js.map