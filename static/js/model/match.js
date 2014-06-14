/**
 * @author nttdocomo
 */
define(function(require) {
	return Backbone.Model.extend({
		url:function(){
			if(this.isNew()){
				return '/api/match?' + (this.isAdmin ? '&admin=1':'');
			} else {
				return '/api/match/?id=' + this.id + (this.isAdmin ? '&admin=1':'');
			}
		}
	});
});