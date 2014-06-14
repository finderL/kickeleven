/**
 * @author nttdocomo
 */
define(function(require) {
	return Backbone.Model.extend({
		url:function(){
			if(this.isNew()){
				return '/api?method=match' + (this.isAdmin ? '&admin=1':'');
			} else {
				return '/api?method=match&id=' + this.id + (this.isAdmin ? '&admin=1':'');
			}
		}
	});
});