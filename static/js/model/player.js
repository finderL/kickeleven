/**
 * @author nttdocomo
 */
define(function(require) {
	require('../taurus/lang/date');
	return taurus.klass('taurus.model.Player', Backbone.Model.extend({
		defaults:{
			avatar:'none.png'
		},
		/*relations: [{
			type: Backbone.HasMany,
			key: 'nationality',
			relatedModel: 'taurus.model.National',
			reverseRelation: {
				key: 'player'
				// 'relatedModel' is automatically set to 'Zoo'; the 'relationType' to 'HasOne'.
			}
		}],*/
		url:function(){
			if(this.isNew()){
				return '/api?method=player' + (this.isAdmin ? '&admin=1':'');
			} else {
				return '/api?method=player&id=' + this.id + (this.isAdmin ? '&admin=1':'');
			}
		},
		save:function(key, val, options){
			var attrs, current, done;
			// Handle both `"key", value` and `{key: value}` -style arguments.
			if (key == null || _.isObject(key)) {
				attrs = key;
				options = val;
			} else if (key != null) {
				(attrs = {})[key] = val;
			}
			Backbone.Model.prototype.save.apply(this,[attrs, options]);
		},
		toJSON:function(){
			var json = Backbone.Model.prototype.toJSON.apply(this,arguments);
			if(!json.club){
				json.club = undefined;
			}
			return json
		},
		isManager:function(){
			return this.has('manage_club');
		},
		isGk:function(){
			return _.find(this.get('position'),function(item){
				return item.position == 7;
			});
		},
		is_club_admin:function(club){
			return _.contains(club.get('administrator'),this.id);
		},
		is_me:function(){
			return this.id === taurus.currentPlayer.id;
		},
		is_founder:function(club){
			return club.get('founder') && club.get('founder').id == this.id;
		},
		parse : function(resp) {
			//if(resp.results && resp.results)
			if(resp.rv){
				return resp.rv.player;
			}
			return resp
		}
	}));
});