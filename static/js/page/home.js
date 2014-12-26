/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('./base'),
	Panel = require('../taurus/panel/panel'),
	Table = require('../taurus/panel/table'),
	Match = require('../collection/match'),
	Tables = require('../collection/table'),
	i18n = require('../i18n/zh-cn');
	return taurus.view('taurus.page.Home',Base.extend({
		events:{
			'click .nav a':'navigate',
			'click .player-list a':'playerSummary',
			'click .club-panel a':'clubSummary',
			'click .club-panel .list-group-item:eq(0)':'squad'
		},
		tpl:'<div class="col-lg-3 flex-height"></div><div class="col-lg-3 flex-height"></div><div class="col-lg-3 flex-height"></div><div class="col-lg-3 flex-height"></div>',
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			this.recentMatch();
			this.table();
		},
		nextMatch:function(model){
			console.log(model);
			new Panel({
				title:i18n.__('Next Match'),
				content:'<div class="container-fluid"><div class="row"><div class="col-lg-5"><img src="/images/clubs/'+model.get('team1').owner.id+'.png"></div><div class="col-lg-2"></div><div class="col-lg-5"><img src="/images/clubs/'+model.get('team2').owner.id+'.png"></div></div></div>',
				renderTo:this.$el.find('>.col-lg-3:eq(0)')
			})
		},
		recentMatch:function(){
			var me = this,
			matches = new Match();
			matches.fetch({
				data:{
					'limit':10,
					'start':moment().format('YYYY-MM-DD hh:mm:ss')
				},
				success:function(collection){
					if(collection.length){
						me.nextMatch(collection.at(0))
						new Table({
							hideHeaders:true,
							loading:true,
							rowTemplate:'<tr data-item-id="<%=id%>">',
							refreshable:true,
							header:false,
							uiClass:'results-table',
							title:i18n.__('Fixtures'),
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
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" class="text-right">'+value.team_name+'</a>';
								},
								dataIndex : 'team1'
							},{
								text : i18n.__('Home'),
								cellWidth:36,
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'" class="text-right"><img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
								},
								dataIndex : 'team1'
							},{
								text : i18n.__('Away'),
								cellWidth:36,
								align:'left',
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/" title="'+value.team_name+'"><img src="/images/clubs/20_20/'+value.owner.id +'.png" height="20" width="20" alt="'+value.team_name+'"/></a>';
								},
								dataIndex : 'team2'
							},{
								text : i18n.__('Away'),
								align:'left',
								renderer : function(value,data) {
									return '<a data-item-id="'+value.id+'" href="/#!team/'+value.id+'/">'+value.team_name+'</a>';
								},
								dataIndex : 'team2'
							}],
							collection : matches,
							renderTo:me.$el.find('>.col-lg-3:eq(1)').empty()
						});
					}
				}
			});
		},
		table:function(model){
			var me = this;
			table = new Tables();
			table.fetch({
				data:{
					'event':1
				},
				success:function(){
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
						renderTo:me.$el.find('>.col-lg-3:eq(2)'),
						onRefresh:function(){
							me.collection.fetch();
						}
					});
				}
			});
		}
	}));
});
