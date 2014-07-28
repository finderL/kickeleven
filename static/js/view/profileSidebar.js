/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('../taurus/view/base'),
	i18n = require('../i18n/zh-cn');
	return Base.extend({
		tpl:'<div class="profile-avatar"><img src="<%=logo%>" /></div><div class="profile-header"><h1 class="profile-header-name"><%=name%></h1><h2 class="profile-header-competition"><a href="#competition/<%=competition_id%>/"><%=competition_name%></a></h2></div>',
        className:'profile-sidebar',
        initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			this.model.on('sync',function(){
				this.html();
			},this);
		},
		getTplData:function(){
			return $.extend(Base.prototype.getTplData.apply(this,arguments),{
				logo:this.model.getLogoPath(),
				name:this.model.get('team_name'),
				competition_name:this.model.get('competition').name,
				competition_id:this.model.get('competition').id
			});
		}
	});
});
