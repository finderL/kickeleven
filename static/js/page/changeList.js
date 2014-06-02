/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('./base'),
	i18n = require('../i18n/zh-cn'),
	Breadcrumbs = require('../breadcrumbs'),
	Table = require('../taurus/panel/table');
	return Base.extend({
		tpl:'<div class="col-lg-12 flex-height"><a class="btn btn-primary" href="/admin/#<%=model%>/add/">' + i18n.__("Add") + '</a></div>',
		uiClass:'change-list',
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			new Table({
				uiClass:'flex-height',
				title:this.title,
				columns : this.columns,
				collection : this.collection,
				renderTo:this.$el.find('.col-lg-12'),
				operation:'prepend',
				events:this.events,
				pager:true
			});
			new Breadcrumbs({
				breadcrumbs:[{
					text:'Home',
					href:'/admin/#home'
				},{
					text:this.title,
					active:true
				}],
				renderTo:this.$el.find('.col-lg-12'),
				operation:'prepend'
			});
		},
		getTplData:function(){
			return {
				model:this.title.toLowerCase()
			};
		}
	});
});
