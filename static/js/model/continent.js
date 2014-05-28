/**
 * @author nttdocomo
 */
define(function(require){
	require('../collection/nation');
	return Backbone.Model.extend({
		url:function(){
			if(this.isNew()){
				return '/api?method=continent';
			} else {
				return '/api?method=continent&id=' + this.id;
			}
		},
		parse : function(resp) {
			//if(resp.results && resp.results)
			if(resp.rv){
				return resp.rv.continent;
			}
			return resp
		}/*,
		save:function(key, val, options){
			return Backbone.Model.prototype.save.call(this, key, val, $.extend(options,{
				emulateJSON:true
			}));
		}*/
	});
});
