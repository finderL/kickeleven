/**
 * @author nttdocomo
 */
define(function(require) {
	require('backbone');
	var site = require('./admin/admin').site;
	var NationAdmin = require('./admin/admin').nation;
	var patterns = require('./admin/admin').patterns;
	var route = Backbone.Router.prototype.route;
	return taurus.klass('taurus.Router', Backbone.Router.extend({
		container : taurus.$body.find('>.container-fluid'),
		initialize : function() {
			this.routeMethods = {};
			this.bind('all', this._trackPageview);
		},
		_trackPageview : function() {
			var url = Backbone.history.getFragment();
			return ga && ga('send', 'pageview', '/' + url);
		},
		routes : $.extend(patterns('admin',site.get_urls()),{
			"" : "home", // #home
			"home" : "home", // #home
			"player" : "player",
			"club" : "club",
			"club/:id/" : "club",
			"nation" : "nation",
			"nation/:id/" : "nation",
			":page/" : "page", // #playerlist
			":page/:id/" : "overview" // #contractlist
		}),
		_addRouteMethods : function(path, name) {
			var E = this.constructor.generatePathFunction(path), H = name + "Path";
			this[H] = E;
			return E
		},
		route : function(route, name, callback) {
			if (!_.isRegExp(route))
				route = this._routeToRegExp(route);
			if (_.isFunction(name)) {
				callback = name;
				name = '';
			}
			if (!callback)
				callback = this[name];
			var router = this;
			Backbone.history.route(route, function(fragment) {
				console.log(name);
				var args = router._extractParameters(route, fragment);
				callback && callback.apply(router, args);
				router.trigger.apply(router, ['route:' + name].concat(args));
				router.trigger('route', name, args);
				Backbone.history.trigger('route', router, name, args);
				var active = $('[href="#'+name+'"]');
				if(active.length){
					active.parent().addClass('active').siblings().removeClass('active');
				}
				//router.currentPage && router.currentPage.remove();
				//router.currentPage = null;
			});
			return this;
		},
		home : function() {
			var me = this;
			//var d = taurus.app.switchToPage(Array.prototype.shift.call(arguments),arguments);
			Backbone.history.navigate("player", true);
			/*require.async("./page/home", function(Page) {
				me.currentPage = new Page({
					renderTo : me.container.empty()
				});
			});*/
		},
		player:function(){
			var me = this;
			require.async("./page/player", function(Page) {
				new Page({
					renderTo : me.container.empty()
				});
			});
		},
		club:function(id){
			var me = this,
			page = id ? "./page/club/index" : "./page/club",
			options = {
				renderTo : me.container.empty()
			};
			if(id){
				$.extend(options,{
					id:id
				});
			}
			require.async(page, function(Page) {
				new Page(options);
			});
		},
		nation:function(id){
			var me = this,
			page = id ? "./page/nation/index" : "./page/nation",
			options = {
				renderTo : me.container.empty()
			};
			if(id){
				$.extend(options,{
					id:id
				});
			}
			require.async(page, function(Page) {
				new Page(options);
			});
		},
		page : function(pageName) {
			var me = this,key = _.toArray(arguments).join('')
			//var d = taurus.app.switchToPage(Array.prototype.shift.call(arguments),arguments);
			require.async("./page/" + pageName, function(Page) {
				new Page({
					renderTo : me.container.empty()
				});
			});
			//d.send('new', Array.prototype.slice.apply(arguments))
		},
		overview : function(page, id) {
			var id = Array.prototype.splice.call(arguments,1,1)
			console.log(arguments)
			console.log(id)
			var me = this;
			if(arguments.length == 1){
				Array.prototype.push.call(arguments,"index")
			}
			var path = "./page/"+ Array.prototype.slice.call(arguments,0).join("/")
			require.async(path, function(Page) {
				new Page({
					id : id,
					/*model:new Model({
					 id:id
					 }),*/
					renderTo : me.container.empty()
				})
			})
		}
	}, {
		generatePathFunction : function(path) {
			var self = this;
			return function(H) {
				var G = self.supplantPath(path, H);
				if (G === false && !taurus.isTestEnv) {
					console.error("Failed to generate a path", path, H)
				}
				return G
			}
		},
		supplantPath : function(J, L) {
			var F = J.split("#").join("/#").split("/"), E = [];
			for (var I = 0; I < F.length; I++) {
				var H = F[I], G = false;
				if (H.charAt(0) === "#") {
					H = H.slice(1);
					G = true
				}
				if (H.charAt(0) === ":") {
					var K = H.slice(1);
					if ( typeof L[K] === "undefined") {
						return false
					} else {
						H = L[K];
						if ( typeof H === "function") {
							H = H.call(L)
						}
						H = encodeURIComponent(H)
					}
				}
				if (G) {
					H = "#" + H
				}
				E.push(H)
			}
			return E.join("/").split("/#").join("#")
		}
	}));
});