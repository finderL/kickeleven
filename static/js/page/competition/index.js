/**
 * @author nttdocomo
 */
define(function(require){
	require('moment');
	var Base = require('../base'),
	Table = require('../../taurus/panel/table'),
	Competition = require('../../model/competition'),
	Team = require('../../collection/team'),
	Nation = require('../../model/nation'),
	i18n = require('../../i18n/{locale}');
	return Base.extend({
		events:{
			'click .player-list a':'playerSummary'
		},
		tpl:'<div class="col-lg-12"></div>',
		initialize:function(options){
			Base.prototype.initialize.apply(this,arguments);
			var me = this;
			this.model = new Competition({
				id:options.id
			});
			this.model.fetch({
				success:_.bind(this.listTeam,this),
			});
		},
		listTeam:function(model){
			var me = this;
			this.team = new Team();
			this.team.fetch({
				data:{
					competition:this.model.id,
					type:1
				}
			});
			new Table({
				loading:true,
				refreshable:true,
				uiClass:'player-list',
				title:i18n.__('CLUBS ' + model.get('name') + ' 14/15'),
				columns : [{
					text : i18n.__('Club'),
					flex : 1,
					sortable : false,
					renderer : function(value,data) {
						return '<a data-item-id="'+data.id+'" href="/#team/'+data.id+'/">'+value+'</a>';
					},
					dataIndex : 'team_name'
				}],
				collection : this.team,
				renderTo:me.$el.find('.col-lg-12').empty(),
				onRefresh:function(){
					me.collection.fetch();
				}
			});
		}
	});
});
