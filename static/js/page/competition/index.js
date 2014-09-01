/**
 * @author nttdocomo
 */
define(function(require){
	require('moment');
	var Base = require('../base'),
	Table = require('../../taurus/panel/table'),
	Event = require('../../model/event'),
	Tables = require('../../collection/table'),
	Team = require('../../collection/team'),
	Match = require('../../collection/match'),
	Nation = require('../../model/nation'),
	ProfileSidebar = require('../../view/competitionProfileSidebar'),
	i18n = require('../../i18n/{locale}');
	return Base.extend({
		events:{
			'click .player-list a':'playerSummary'
		},
		tpl:'<div class="col-lg-3"></div><div class="col-lg-6"></div><div class="col-lg-3"></div>',
		initialize:function(options){
			Base.prototype.initialize.apply(this,arguments);
			var me = this;
			this.model = new Event();
			this.model.fetch({
				data:{
					competition:options.id
				},
				success:_.bind(function(model){
					document.title = model.get('competition').name;
					new ProfileSidebar({
						model:model,
						renderTo:me.$el.find('.col-lg-3:eq(0)')
					});
					this.listTeam(model);
					this.listFixtures(model);
					this.listResults(model)
				},this),
			});

		},
		listResults:function(model){
			var me = this,
			option = {
				data:{
					'event':this.model.id,
					limit:10,
					'results':1
				},
				error:function(collection, response, options){
					require.async('../../taurus/widget/prompt',function(Prompt){
						(new Prompt({
							'title':'Error',
							'content':'You got an error, try again?',
						})).on('confirm',function(){
							collection.fetch(option)
						}).show()
					})
				},
				success:function(collection){
					if(collection.length){
						new Table({
							loading:true,
							refreshable:true,
							header:false,
							uiClass:'player-list',
							title:i18n.__('Results'),
							columns : [{
								text : i18n.__('Date'),
								renderer : function(value,data) {
									return '<span title="' + moment(value).format('MMM DD, YYYY HH:mm') + '">' + moment(value).format('MMM DD, YYYY') + '</span>';
								},
								dataIndex : 'play_at'
							},{
								text : i18n.__('Home'),
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'"><img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
								},
								dataIndex : 'team1'
							},{
								text : i18n.__('Result'),
								renderer : function(value,data) {
									return [data.score1 !== null ? data.score1 : '-',data.score2 !== null ? data.score2 : '-'].join(':');
								},
								dataIndex : 'team2'
							},{
								text : i18n.__('Away'),
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'"><img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
								},
								dataIndex : 'team2'
							}],
							collection : collection,
							renderTo:me.$el.find('.col-lg-3:eq(0)')
						});
					}
				}
			},
			matchs = new Match();
			matchs.fetch(option);
		},
		listFixtures:function(model){
			var me = this,
			option = {
				data:{
					'event':this.model.id,
					limit:10,
					'fixtures':1
				},
				error:function(collection, response, options){
					require.async('../../taurus/widget/prompt',function(Prompt){
						(new Prompt({
							'title':'Error',
							'content':'You got an error, try again?',
						})).on('confirm',function(){
							collection.fetch(option)
						}).show()
					})
				},
				success:function(collection){
					if(collection.length){
						new Table({
							loading:true,
							refreshable:true,
							header:false,
							uiClass:'player-list',
							title:i18n.__('Fixtures'),
							columns : [{
								text : i18n.__('Date'),
								renderer : function(value,data) {
									return '<span title="' + moment(value).format('MMM DD, YYYY, HH:mm') + '">' + moment(value).format('MMM DD, YYYY') + '</span>';
								},
								dataIndex : 'play_at'
							},{
								text : i18n.__('Home'),
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'"><img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
								},
								dataIndex : 'team1'
							},{
								text : i18n.__('Result'),
								renderer : function(value,data) {
									return [data.score1 !== null ? data.score1 : '-',data.score2 !== null ? data.score2 : '-'].join(':');
								},
								dataIndex : 'team2'
							},{
								text : i18n.__('Away'),
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'"><img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
								},
								dataIndex : 'team2'
							}],
							collection : matchs,
							renderTo:me.$el.find('.col-lg-3:eq(1)').empty()
						});
					}
				}
			},
			matchs = new Match();
			matchs.fetch(option);
		},
		listTeam:function(model){
			var me = this;
			team = new Tables();
			team.fetch({
				data:{
					'event':this.model.id
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
						return '<a data-item-id="'+data.id+'" href="/#!team/'+data.id+'/">'+value+'</a>';
					},
					dataIndex : 'team_name'
				},{
					text : i18n.__('M'),
					renderer : function(value,data) {
						if(data.wins !== null || data.draws !== null || data.loses !== null){
							return data.wins + data.draws + data.loses;
						}
						return '-';
					},
					dataIndex : 'team_name'
				},{
					text : i18n.__('W'),
					renderer : function(value,data) {
						if(value !== null){
							return value;
						}
						return '-';
					},
					dataIndex : 'wins'
				},{
					text : i18n.__('D'),
					renderer : function(value,data) {
						if(value !== null){
							return value;
						}
						return '-';
					},
					dataIndex : 'draws'
				},{
					text : i18n.__('L'),
					renderer : function(value,data) {
						if(value !== null){
							return value;
						}
						return '-';
					},
					dataIndex : 'loses'
				},{
					text : i18n.__('GF'),
					renderer : function(value,data) {
						if(data.goals_for !== null){
							return data.goals_for;
						}
						return '-';
					},
					dataIndex : 'goals_for'
				},{
					text : i18n.__('GA'),
					renderer : function(value,data) {
						if(data.goals_against !== null){
							return data.goals_against;
						}
						return '-';
					},
					dataIndex : 'goals_against'
				},{
					text : i18n.__('+/-'),
					renderer : function(value,data) {
						if(data.goals_for !== null && data.goals_against !== null){
							return data.goals_for - data.goals_against;
						}
						return '-';
					},
					dataIndex : 'goals_for'
				},{
					text : i18n.__('Pts'),
					renderer : function(value,data) {
						if(value !== null){
							return value * 3 + data.draws * 1 + data.init_point;
						}
						return '-';
					},
					dataIndex : 'wins'
				}],
				collection : team,
				renderTo:me.$el.find('.col-lg-6').empty(),
				onRefresh:function(){
					me.collection.fetch();
				}
			});
		}
	});
});
