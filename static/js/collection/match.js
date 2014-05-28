/**
 * @author nttdocomo
 */
define(function(require) {
	require('../model/match');
	return taurus.klass('taurus.collection.Match', Backbone.Collection.extend({
		url:'/api?method=match.search',
		model : taurus.model.Match,
		parse : function(resp) {
			var results = resp.rv.match;
			return results;
		}
	}));
})