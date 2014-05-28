/**
 * @author nttdocomo
 */
define(function(require) {
	return taurus.klass('taurus.model.Nation', Backbone.Model.extend({
		url:function(){
			if(this.isNew()){
				return '/api?method=nation';
			} else {
				return '/api?method=nation&id=' + this.id;
			}
		},
		parse : function(resp) {
			//if(resp.results && resp.results)
			if(resp.rv){
				return resp.rv.nation;
			}
			return resp
		}
		/*relations: [{
			type: Backbone.HasMany,
			key: 'national',
			relatedModel: 'taurus.model.National',
			includeInJSON:false,
			reverseRelation: {
				key: 'nation'
				// 'relatedModel' is automatically set to 'Zoo'; the 'relationType' to 'HasOne'.
			}
		}]*/
	}));
});