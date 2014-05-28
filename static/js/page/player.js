/**
 * @author nttdocomo
 */
define(function(require){
	require('moment');
	var Base = require('./base'),
	Table = require('../taurus/panel/table'),
	Player = require('../collection/player'),
	i18n = require('../i18n/zh-cn');
	return Base.extend({
		events:{
			'click .player-list a':'playerSummary'
		},
		tpl:'<div class="col-lg-12 flex-height"></div>',
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			this.listPlayer();
		},
		listPlayer:function(){
			var me = this;
			me.player = me.player || new Player;
			new Table({
				loading:true,
				header:false,
				refreshable:true,
				uiClass:'player-list flex-height',
				title:i18n.__('Player'),
				columns : [{
					text : i18n.__('Full Name'),
					flex : 1,
					sortable : false,
					renderer : function(value,data) {
						return '<a data-item-id="'+data.id+'" href="/#player/'+data.id+'/">'+value+'</a>';
					},
					dataIndex : 'full_name'
				}, {
					text : i18n.__('Nation'),
					sortable : true,
					width:200,
					renderer : function(value) {
						var result = [];
						if(value){
							return value.short_name;
						} else {
							return '-';
						}
					},
					dataIndex : 'nation'
				}, {
					text : i18n.__('Height'),
					sortable : true,
					width:200,
					dataIndex : 'height'
				}, {
					text : i18n.__('Weight'),
					sortable : true,
					width:200,
					dataIndex : 'weight'
				}, {
					text : '年龄',
					sortable : true,
					width:200,
					renderer : function(value) {
						return taurus.Date.getAge(value, 'yyyy-mm-dd');
					},
					dataIndex : 'date_of_birth'
				}],
				collection : me.player,
				renderTo:me.$el.find('.col-lg-12').empty(),
				onRefresh:function(){
					this.collection.fetch();
				},
				pager:true
			});
			me.player.length || me.player.fetch();
		},
		playerSummary:function(e){
			var me = this;
			require.async(['../widget/playerDialog'],function(Panel){
				var model = me.player.get($(e.target).attr('data-item-id'));
				(new Panel({
					width:400,
					title:model.get('full_name'),
					model:me.player.get($(e.target).attr('data-item-id')),
					renderTo:taurus.$body
				})).show();
				model.fetch();
			});
			return false;
		}
	});
});
