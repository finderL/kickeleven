/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('../taurus/view/base');
	return taurus.view('taurus.panel.Table',Base.extend({
		tpl:'<div class="panel-heading"><h3 class="panel-title"><%=title%></h3></div><%=content%>',
		className:'panel panel-default table-panel',
		afterRender:function(){
			var me = this;
			if(this.view){
				if(_.isArray(this.view)){
					require.async(_.map(this.view,function(view){
						return '../view/'+this.view;
					}),function(){
						_.each(arguments,function(View){
							new View({
								model:me.model,
								renderTo:me.$el.find('.panel-body')
							})
						})
					})
				} else{
					require.async('../view/'+this.view,function(View){
						new View({
							model:me.model,
							renderTo:me.$el.find('.panel-body')
						})
					})
				}
			}
		}
	}))
})
