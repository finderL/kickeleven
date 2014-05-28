/**
 * @author nttdocomo
 */
define(function(require){
	require('moment');
	var Base = require('../base'),
	Table = require('../../taurus/panel/table'),
	Squad = require('../../collection/nationSquad'),
	Nation = require('../../model/nation'),
	//ClubPanel = require('../../panel/clubPanel'),
	i18n = require('../../i18n/zh-cn');
	return Base.extend({
		events:{
			'click .player-list a':'playerSummary'
		},
		tpl:'<div class="col-lg-3 flex-height"></div><div class="col-lg-9 flex-height"></div>',
		initialize:function(options){
			var me = this;
			this.model = new Nation({
				id:options.id
			});
			delete options.id;
			Base.prototype.initialize.apply(this,[options]);
			this.listPlayer();
			this.model.fetch({
				success:function(){
					/*new ClubPanel({
						model:me.model,
						renderTo:me.$el.find('.col-lg-3').empty()
					});*/
				}
			});
		},
		listPlayer:function(){
			var me = this;
			me.collection = me.collection || new Squad;
			me.collection.nation = this.model;
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
					sortable : false,
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
					sortable : false,
					width:100,
					dataIndex : 'height'
				}, {
					text : i18n.__('Weight'),
					sortable : false,
					width:100,
					dataIndex : 'weight'
				}, {
					text : 'Age',
					sortable : false,
					width:100,
					renderer : function(value) {
						return taurus.Date.getAge(value, 'yyyy-mm-dd');
					},
					dataIndex : 'date_of_birth'
				}],
				collection : me.collection,
				renderTo:me.$el.find('.col-lg-9').empty(),
				onRefresh:function(){
					me.collection.fetch();
				},
				pager:true
			});
			//me.collection.length || me.collection.fetch();
		},
		playerSummary:function(e){
			var me = this;
			require.async(['../../widget/playerDialog'],function(Panel){
				var model = me.collection.get($(e.target).attr('data-item-id'));
				(new Panel({
					width:400,
					title:model.get('full_name'),
					model:model,
					renderTo:taurus.$body
				})).show();
				model.fetch();
			});
			return false;
		}
	});
});
