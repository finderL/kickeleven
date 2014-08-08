/**
 * @author nttdocomo
 */
define(function(require){
	require('moment');
	var Base = require('../base'),
	Table = require('../../taurus/panel/table'),
	Event = require('../../model/event'),
	Team = require('../../collection/team'),
	Match = require('../../collection/match'),
	Nation = require('../../model/nation'),
	i18n = require('../../i18n/{locale}');
	return Base.extend({
		events:{
			'click .player-list a':'playerSummary'
		},
		tpl:'<div class="col-lg-8"></div><div class="col-lg-4"></div>',
		initialize:function(options){
			Base.prototype.initialize.apply(this,arguments);
			var me = this;
			this.model = new Event();
			this.model.fetch({
				data:{
					competition:options.id
				},
				success:_.bind(function(model){
					this.listTeam(model);
					this.listMatchs(model)
				},this),
			});

		},
		listMatchs:function(model){
			var me = this;
			matchs = new Match();
			matchs.fetch({
				data:{
					'event':this.model.id,
					limit:10
				}
			});
			new Table({
				loading:true,
				refreshable:true,
				uiClass:'player-list',
				title:i18n.__('Fixtures ' + model.get('competition').name + ' ' + model.get('season').name),
				columns : [{
					text : i18n.__('Date'),
					renderer : function(value,data) {
						return moment(value).format('MMM DD, YYYY');
					},
					dataIndex : 'play_at'
				},{
					text : i18n.__('Home team'),
					renderer : function(value,data) {
						return '<a data-item-id="'+value.id+'" href="/#team/'+value.id+'/" title="'+value.team_name+'"><img src="/static/resources/clubs/'+value.owner.logo_id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
					},
					dataIndex : 'team1'
				},{
					text : i18n.__('Away team'),
					renderer : function(value,data) {
						return '<a data-item-id="'+value.id+'" href="/#team/'+value.id+'/" title="'+value.team_name+'"><img src="/static/resources/clubs/'+value.owner.logo_id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
					},
					dataIndex : 'team2'
				}],
				collection : matchs,
				renderTo:me.$el.find('.col-lg-4').empty(),
				onRefresh:function(){
					me.collection.fetch();
				}
			});
		},
		listTeam:function(model){
			var me = this;
			team = new Team();
			team.fetch({
				data:{
					'event':this.model.id,
					type:1
				}
			});
			new Table({
				loading:true,
				refreshable:true,
				uiClass:'player-list',
				title:i18n.__('CLUBS ' + model.get('competition').name + ' ' + model.get('season').name),
				columns : [{
					text : i18n.__('Club'),
					renderer : function(value,data) {
						return '<a data-item-id="'+data.id+'" href="/#team/'+data.id+'/">'+value+'</a>';
					},
					dataIndex : 'team_name'
				},{
					text : i18n.__('Matchs'),
					renderer : function(value,data) {
						return '-';
					},
					dataIndex : 'team_name'
				},{
					text : i18n.__('Wins'),
					renderer : function(value,data) {
						return '-';
					},
					dataIndex : 'team_name'
				},{
					text : i18n.__('Draws'),
					renderer : function(value,data) {
						return '-';
					},
					dataIndex : 'team_name'
				},{
					text : i18n.__('Loses'),
					renderer : function(value,data) {
						return '-';
					},
					dataIndex : 'team_name'
				}],
				collection : team,
				renderTo:me.$el.find('.col-lg-8').empty(),
				onRefresh:function(){
					me.collection.fetch();
				}
			});
		}
	});
});
