/**
 * @author nttdocomo
 */
define(function(require){
	require('moment');
	var Base = require('./base'),
	Table = require('../taurus/panel/table'),
	Club = require('../collection/club'),
	i18n = require('../i18n/zh-cn');
	return Base.extend({
		tpl:'<div class="col-lg-12 flex-height"></div>',
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			this.listClub();
		},
		listClub:function(){
			var me = this;
			me.collection = me.collection || new Club;
			new Table({
				loading:true,
				header:false,
				refreshable:true,
				uiClass:'player-list flex-height',
				title:i18n.__('Club'),
				columns : [{
					text : i18n.__('Club Name'),
					flex : 1,
					sortable : false,
					renderer : function(value,data) {
						return '<a data-item-id="'+data.id+'" href="/#club/'+data.id+'/">'+value+'</a>';
					},
					dataIndex : 'club_name'
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
					text : 'Year Founded',
					sortable : true,
					width:200,
					renderer : function(value) {
						return moment(value).format('YYYY-MM-DD');
					},
					dataIndex : 'year_founded'
				}],
				collection : me.collection,
				renderTo:me.$el.find('.col-lg-12').empty(),
				onRefresh:function(){
					me.collection.fetch();
				},
				pager:true
			});
			//me.collection.length || me.collection.fetch();
		}
	});
});
