/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('../taurus/view/base'),
	Transfer = require('../collection/transfer'),
	Table = require('../taurus/view/table'),
	i18n = require('../i18n/zh-cn');
	return Base.extend({
		tpl:'<%_.each(transfers,function(transfer){%><div class="transfer-summary"><div class="content"><a class="js-player-profile-link user-thumb" href="/JohnLegere" data-user-id="<%=transfer.player_id%>"><img class="avatar js-action-profile-avatar " src="/static/tmp/none.png" alt="">\
      <span class="account-group-inner js-action-profile-name" data-player-id="<%=transfer.player_id%>">\
        <b class="fullname"><%=transfer.player.name%></b>\
      </span>\
    </a><div class="transfer-date"><%=moment(transfer.transfer_date).format("YYYY-MM-DD")%></div></div></div><%})%>',
        className:'recent-trasfers',
        initialize:function(){
        	Base.prototype.initialize.apply(this,arguments);
        	this.collection.on('sync',function(){
        		this.html();
        	},this)
        },
		getTplData:function(){
			return $.extend(Base.prototype.getTplData.apply(this,arguments),{
				transfers:this.collection.toJSON()
			});
		}
	});
});
