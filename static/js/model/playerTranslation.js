/**
 * @author nttdocomo
 */
define(function(require) {
	return Backbone.Model.extend({
		url:function(){
			if(this.isNew()){
				return '/api?method=playertranslation';
			} else {
				return '/api?method=playertranslation&id=' + this.id;
			}
		},
		parse : function(resp) {
			//if(resp.results && resp.results)
			if(resp.rv){
				return resp.rv.playertranslation;
			}
			return resp;
		}
	});
});