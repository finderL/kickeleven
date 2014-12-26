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
	Goal = require('../../collection/goal'),
	Nation = require('../../model/nation'),
	ProfileSidebar = require('../../view/competitionProfileSidebar'),
	i18n = require('../../i18n/{locale}');
	return Base.extend({
		events:{
			'click .player-list a':'playerSummary',
			'click .results-table tr':function(e){
				var goals = new Goal(),
				$target = $(e.currentTarget),
				id = $target.attr('data-item-id'),
				result =this.results.get(id);
				if($target.hasClass('expand')){
					$target.removeClass('expand');
					$target.nextAll('[data-match-id]').remove();
				} else {
					goals.fetch({
						data:{
							match:id
						},
						success:function(collection){
							$target.after(collection.map(function(model){
								var goals_info = '<img class="" src="/images/players/20_20/<%=player.id%>.png" alt="<%=player.name%>">';
								if(model.get('owngoal')){
									goals_info += '(OG)';
								}
								return _.template('<tr data-match-id="'+result.id+'"><td></td><td>'+(model.get('team_id') == result.get('team1_id') ? goals_info:'')+'</td><td><%=minute%></td><td>'+(model.get('team_id') == result.get('team2_id') ? goals_info:'')+'</td></tr>',model.toJSON())
							}).join('')).addClass('expand');
						}
					});
				}
			}
		},
		tpl:'<div class="col-lg-2"></div><div class="col-lg-3"></div></div><div class="col-lg-3"></div><div class="col-lg-4 flex-height"></div>',
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
						renderTo:me.$el.find('.col-lg-2')
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
				success:function(collection){
					if(collection.length){
						new Table({
							loading:true,
							hideHeaders:true,
							rowTemplate:'<tr data-item-id="<%=id%>">',
							refreshable:true,
							header:false,
							uiClass:'results-table',
							title:i18n.__('Results'),
							columns : [{
								text : i18n.__('Date'),
								renderer : function(value,data) {
									return '<span title="' + moment(value).format('MMM DD, YYYY HH:mm') + '">' + moment(value).format('DD/MM') + '</span>';
								},
								dataIndex : 'play_at'
							},{
								text : i18n.__('Home'),
								align:'right',
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'">'+value.team_name+'<img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
								},
								dataIndex : 'team1'
							},{
								text : i18n.__('Result'),
								renderer : function(fieldValue, cellValues, record, recordIndex, fullIndex) {
									return [record.score1 !== null ? record.score1 : '0',record.score2 !== null ? record.score2 : '0'].join(':');
								},
								dataIndex : 'team2'
							},{
								text : i18n.__('Away'),
								align:'left',
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'"><img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/>'+value.team_name+'</a>';
								},
								dataIndex : 'team2'
							}],
							collection : collection,
							renderTo:me.$el.find('.col-lg-3:eq(0)')
						});
					}
				}
			};
			this.results = new Match();
			this.results.fetch(option);
		},
		listFixtures:function(model){
			var me = this,
			option = {
				data:{
					'event':this.model.id,
					limit:10,
					'fixtures':1
				},
				success:function(collection){
					if(collection.length){
						new Table({
							loading:true,
							hideHeaders:true,
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
								text : '',
								renderer : function(value,data) {
									return 'vs'
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
			table = new Tables();
			table.fetch({
				data:{
					'event':this.model.id
				}
			});
			new Table({
				loading:true,
				refreshable:true,
				uiClass:'player-list flex-height',
				title:i18n.__('League Table'),
				columns : [{
					text : i18n.__('Team'),
					renderer : function(fieldValue, cellValues, record) {
						return '<a data-item-id="'+record.id+'" href="/#!team/'+record.id+'/">'+fieldValue+'</a>';
					},
					dataIndex : 'team_name'
				},{
					text : i18n.__('M'),
					renderer : function(fieldValue, cellValues, record, recordIndex, fullIndex) {
						if(record.wins !== null || record.draws !== null || record.loses !== null){
							return record.wins + record.draws + record.loses;
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
					renderer : function(fieldValue, cellValues, record, recordIndex, fullIndex) {
						if(record.goals_for !== null){
							return record.goals_for;
						}
						return '-';
					},
					dataIndex : 'goals_for'
				},{
					text : i18n.__('GA'),
					renderer : function(fieldValue, cellValues, record, recordIndex, fullIndex) {
						if(record.goals_against !== null){
							return record.goals_against;
						}
						return '-';
					},
					dataIndex : 'goals_against'
				},{
					text : i18n.__('+/-'),
					renderer : function(fieldValue, cellValues, record, recordIndex, fullIndex) {
						if(record.goals_for !== null && record.goals_against !== null){
							return record.goals_for - record.goals_against;
						}
						return '-';
					},
					dataIndex : 'goals_for'
				},{
					text : i18n.__('Pts'),
					renderer : function(fieldValue, cellValues, record, recordIndex, fullIndex) {
						if(fieldValue !== null){
							return fieldValue * 3 + record.draws * 1 + record.init_point;
						}
						return '-';
					},
					dataIndex : 'wins'
				}],
				collection : table,
				renderTo:me.$el.find('>.col-lg-4')
			});
		}
	});
});
