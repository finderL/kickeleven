/**
 * @author nttdocomo
 */
define(function(require){
	require('moment');
	var Base = require('./base');
	var Table = require('../taurus/panel/table'),
	i18n = require('../i18n/zh-cn');
	return taurus.view('taurus.page.Home',Base.extend({
		events:{
			'click .nav a':'navigate',
			'click .player-list a':'playerSummary',
			'click .club-panel a':'clubSummary',
			'click .club-panel .list-group-item:eq(0)':'squad'
		},
		tpl:'<div class="col-lg-2 flex-height"><ul class="nav nav-pills nav-stacked"><li class="active"><a href="#" data-item-type="player">'+i18n.__("Player")+'</a></li><li><a href="#" data-item-type="club">'+i18n.__("Club")+'</a></li></ul></div><div class="col-lg-2 flex-height"></div><div class="col-lg-2 flex-height"></div><div class="col-lg-6 flex-height"></div>',
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			this.listPlayer();
		},
		listPlayer:function(){
			var me = this;
			require.async(['../collection/player','../taurus/panel/table'],function(Player,Panel){
				me.player = me.player || new Player;
				new Panel({
					loading:true,
					refreshable:true,
					uiClass:'player-list flex-height',
					title:i18n.__('Player'),
					columns : [{
						text : i18n.__('Full Name'),
						flex : 1,
						sortable : false,
						renderer : function(value,data) {
							return '<a data-item-id="'+data.id+'" href="/#player/'+data.id+'/">'+value+'</a>'
						},
						dataIndex : 'full_name'
					}, {
						text : i18n.__('Nation'),
						sortable : true,
						renderer : function(value) {
							var result = [];
							if(value){
								return value.short_name;
							} else {
								return '-';
							}
						},
						dataIndex : 'nation'
					}],
					collection : me.player,
					renderTo:me.$el.find('.col-lg-2:eq(1)').empty(),
					onRefresh:function(){
						this.collection.fetch();
					}
				});
				me.player.length || me.player.fetch();
			});
		},
		listClub:function(){
			var me = this;
			require.async(['../collection/club','../taurus/panel/table'],function(Club,Panel){
				me.club = me.club || new Club;
				new Panel({
					loading:true,
					refreshable:true,
					uiClass:'club-panel flex-height',
					title:i18n.__('Club'),
					columns : [{
						text : i18n.__('Club Name'),
						flex : 1,
						sortable : false,
						renderer : function(value,data) {
							return '<a data-item-id="'+data.id+'" href="/#club/'+data.id+'/">'+value+'</a>'
						},
						dataIndex : 'club_name'
					}, {
						text : i18n.__('Nation'),
						sortable : true,
						renderer : function(value) {
							if(value){
								return value.short_name;
							} else {
								return '-';
							}
						},
						dataIndex : 'nation'
					}],
					renderTo:me.$el.find('.col-lg-2:eq(1)').empty(),
					collection:me.club,
					onRefresh:function(){
						this.collection.fetch()
					}
				});
				me.club.length || me.club.fetch();
			});
		},
		navigate:function(e){
			var me = this,
				target = $(e.target),
				parent = target.parent(),
				type = target.attr('data-item-type');
			if(!parent.hasClass('active')){
				if(type == 'player'){
					this.listPlayer();
				}
				if(type == 'club'){
					this.listClub();
				}
				parent.addClass('active').siblings().removeClass('active')
			}
			return false;
		},
		playerSummary:function(e){
			var me = this;
			require.async(['../panel/playerPanel'],function(Panel){
				var model = me.player.get($(e.target).attr('data-item-id'))
				new Panel({
					model:me.player.get($(e.target).attr('data-item-id')),
					renderTo:me.$el.find('.col-lg-2:eq(2)').empty()
				})
				model.fetch()
			});
			return false;
		},
		clubSummary:function(e){
			var me = this;
			require.async(['../panel/clubPanel'],function(Panel){
				new Panel({
					model:me.club.get($(e.target).attr('data-item-id')),
					renderTo:me.$el.find('.col-lg-2:eq(2)').empty()
				});
			});
			return false;
		},
		squad:function(e){
			var me= this, id = $(e.target).attr('data-item-id'), club = me.club.get(id);
			require.async(['../collection/squad','../taurus/panel/table'],function(Squad,Panel){
				var squad;
				if(!club.has('squad')){
					squad = new Squad;
					club.set('squad',squad)
					squad.club = club
				} else {
					squad = club.get('squad')
				}
				if(!squad.length){
					squad.fetch()
				}
				new Panel({
					pager:false,
					refreshable:true,
					uiClass:'squad-panel flex-height',
					title:i18n.__('Squad'),
					columns : [{
						text : i18n.__('Full Name'),
						flex : 1,
						sortable : false,
						renderer : function(value,data) {
							return '<span data-item-id="'+data.id+'">'+value+'</span>'
						},
						dataIndex : 'full_name'
					}, {
						text : i18n.__('Nation'),
						sortable : true,
						renderer : function(value) {
							return value.short_name;
							/*var result = [];
							if(value){
								if(value.length === 1){
									return value[0].nation_name;
								} else {
									_.each(value,function(item){
										result.push(item.nation_name);
									});
									return result.join('/');
								}
							} else {
								return '-'
							}*/
						},
						dataIndex : 'nation'
					}, {
						text : i18n.__('Pos'),
						flex : 1,
						sortable : false,
						renderer : function(value,data) {
							value = _.sortBy(value, function(position){ return position.point; });
							return _.map(value,function(position){
								return _.find(k11.POSITION,function(item){
									return item.value == position.position_name;
								})['text'] + _.find(k11.SIDE,function(item){
									return item.value == position.side;
								})['text'];
							}).join('/');
						},
						dataIndex : 'position'
					}],
					collection:squad,
					renderTo:me.$el.find('.col-lg-6').empty(),
					onRefresh:function(){
						this.collection.fetch();
					}
				});
			});
		}
	}));
});
