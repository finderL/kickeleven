/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('../taurus/panel/panel');
	RecentTransfer = require('../view/recentTransfer');
	return Base.extend({
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments)
			new RecentTransfer({
				collection:this.collection,
				renderTo:this.$el.find('.panel-body')
			})
		}
	})
})
