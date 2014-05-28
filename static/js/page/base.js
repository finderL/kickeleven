/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('../taurus/view/base');
	return taurus.view('taurus.page.Base',Base.extend({
		tpl:'<div class="span3"></div><div class="span9"></div>',
		className:'row flex-height',
		addComponent:function(component){
			this.components = this.components || [];
			this.components.push(component)
		}
	}))
})