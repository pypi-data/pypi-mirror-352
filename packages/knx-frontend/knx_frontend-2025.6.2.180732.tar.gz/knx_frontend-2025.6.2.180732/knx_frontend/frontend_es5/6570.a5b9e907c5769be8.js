"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["6570"],{72199:function(t,i,a){a.r(i),a.d(i,{HaImagecropperDialog:()=>u});a(26847),a(64455),a(6202),a(27530),a(41465),a(34845),a(73249),a(36330),a(38221),a(75863);var o=a(73742),e=(a(98334),a(27007)),r=a.n(e),s=a(93528),p=a(59048),c=a(7616),n=a(31733),l=(a(99298),a(77204));let h,_,d,m=t=>t;class u extends p.oi{showDialog(t){this._params=t,this._open=!0}closeDialog(){var t;this._open=!1,this._params=void 0,null===(t=this._cropper)||void 0===t||t.destroy(),this._cropper=void 0,this._isTargetAspectRatio=!1}updated(t){t.has("_params")&&this._params&&(this._cropper?this._cropper.replace(URL.createObjectURL(this._params.file)):(this._image.src=URL.createObjectURL(this._params.file),this._cropper=new(r())(this._image,{aspectRatio:this._params.options.aspectRatio,viewMode:1,dragMode:"move",minCropBoxWidth:50,ready:()=>{this._isTargetAspectRatio=this._checkMatchAspectRatio(),URL.revokeObjectURL(this._image.src)}})))}_checkMatchAspectRatio(){var t;const i=null===(t=this._params)||void 0===t?void 0:t.options.aspectRatio;if(!i)return!0;const a=this._cropper.getImageData();if(a.aspectRatio===i)return!0;if(a.naturalWidth>a.naturalHeight){const t=a.naturalWidth/i;return Math.abs(t-a.naturalHeight)<=1}const o=a.naturalHeight*i;return Math.abs(o-a.naturalWidth)<=1}render(){var t;return(0,p.dy)(h||(h=m`<ha-dialog
      @closed=${0}
      scrimClickAction
      escapeKeyAction
      .open=${0}
    >
      <div
        class="container ${0}"
      >
        <img alt=${0} />
      </div>
      <mwc-button slot="secondaryAction" @click=${0}>
        ${0}
      </mwc-button>
      ${0}

      <mwc-button slot="primaryAction" @click=${0}>
        ${0}
      </mwc-button>
    </ha-dialog>`),this.closeDialog,this._open,(0,n.$)({round:Boolean(null===(t=this._params)||void 0===t?void 0:t.options.round)}),this.hass.localize("ui.dialogs.image_cropper.crop_image"),this.closeDialog,this.hass.localize("ui.common.cancel"),this._isTargetAspectRatio?(0,p.dy)(_||(_=m`<mwc-button slot="primaryAction" @click=${0}>
            ${0}
          </mwc-button>`),this._useOriginal,this.hass.localize("ui.dialogs.image_cropper.use_original")):p.Ld,this._cropImage,this.hass.localize("ui.dialogs.image_cropper.crop"))}_cropImage(){this._cropper.getCroppedCanvas().toBlob((t=>{if(!t)return;const i=new File([t],this._params.file.name,{type:this._params.options.type||this._params.file.type});this._params.croppedCallback(i),this.closeDialog()}),this._params.options.type||this._params.file.type,this._params.options.quality)}_useOriginal(){this._params.croppedCallback(this._params.file),this.closeDialog()}static get styles(){return[l.yu,(0,p.iv)(d||(d=m`
        ${0}
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
      `),(0,p.$m)(s))]}constructor(...t){super(...t),this._open=!1}}(0,o.__decorate)([(0,c.Cb)({attribute:!1})],u.prototype,"hass",void 0),(0,o.__decorate)([(0,c.SB)()],u.prototype,"_params",void 0),(0,o.__decorate)([(0,c.SB)()],u.prototype,"_open",void 0),(0,o.__decorate)([(0,c.IO)("img",!0)],u.prototype,"_image",void 0),(0,o.__decorate)([(0,c.SB)()],u.prototype,"_isTargetAspectRatio",void 0),u=(0,o.__decorate)([(0,c.Mo)("image-cropper-dialog")],u)}}]);
//# sourceMappingURL=6570.a5b9e907c5769be8.js.map