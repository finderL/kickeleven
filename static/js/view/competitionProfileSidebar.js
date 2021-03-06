/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('../taurus/view/base'),
	i18n = require('../i18n/zh-cn');
	return Base.extend({
		tpl:'<div class="profile-avatar"><img src="<%=logo%>" /></div><div class="profile-header"><h1 class="profile-header-name"><%=name%></h1></div>',
        className:'profile-sidebar',
        initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			this.model.on('sync',function(){
				this.html();
			},this);
		},
		getTplData:function(){
			return $.extend(Base.prototype.getTplData.apply(this,arguments),{
				logo:'/static/resources/competitions/'+this.model.get('competition').logo_id + '.png',
				name:this.model.get('competition').name
			});
		}
	});
});
