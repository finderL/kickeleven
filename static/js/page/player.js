/**
 * @author nttdocomo
 */
define(function(require){
	require('taurus/moment');
	var Base = require('./base'),
	Table = require('../taurus/panel/table'),
	Player = require('../collection/player'),
	Match = require('../collection/match'),
	i18n = require('../i18n/zh-cn');
	return Base.extend({
		events:{
			'click .player-list a':'playerSummary'
		},
		tpl:'<div class="col-lg-3 flex-height"></div><div class="col-lg-9 flex-height"></div>',
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			this.listMatch();
			this.listPlayer();
		},
		listMatch:function(){
			var me = this;
			me.match = me.match || new Match;
			new Table({
				loading:true,
				header:false,
				refreshable:true,
				uiClass:'player-list flex-height',
				title:i18n.__('Match'),
				columns : [{
					text : i18n.__('Match Date'),
					flex : 1,
					sortable : false,
					renderer : function(value,data) {
						return moment(value).format('YYYY-MM-DD HH:mm:ss');
					},
					dataIndex : 'match_date'
				},{
					text : i18n.__('Team'),
					sortable : false,
					width:290,
					renderer : function(value,data) {
						var home = data.home_team, away = data.away_team, html = '';
						if(home.type == 2){
							html += '<a data-item-id="'+data.id+'" href="/admin/#club/'+home.owner.id+'/">'+home.owner.club_name+'</a> ';
						} else {
							html += '<a data-item-id="'+data.id+'" href="/admin/#nation/'+home.owner.id+'/">'+home.owner.full_name+'</a> ';
						}
						html += data.home_score + ' - ' + data.away_score;
						if(away.type == 2){
							html += ' <a data-item-id="'+data.id+'" href="/admin/#club/'+away.owner.id+'/">'+away.owner.club_name+'</a>';
						} else {
							html += ' <a data-item-id="'+data.id+'" href="/admin/#nation/'+away.owner.id+'/">'+away.owner.full_name+'</a>';
						}
						return html;
					},
					dataIndex : 'home_team'
				}],
				collection : me.match,
				renderTo:me.$el.find('.col-lg-3').empty(),
				pager:true
			});
			me.match.length || me.match.fetch();
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
					width:50,
					dataIndex : 'height'
				}, {
					text : i18n.__('Weight'),
					sortable : true,
					width:50,
					dataIndex : 'weight'
				}, {
					text : '年龄',
					sortable : true,
					width:50,
					renderer : function(value) {
						return taurus.Date.getAge(value, 'yyyy-mm-dd');
					},
					dataIndex : 'date_of_birth'
				}],
				collection : me.player,
				renderTo:me.$el.find('.col-lg-9').empty(),
				onRefresh:function(){
					this.collection.fetch();
				},
				pager:true
			});
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
