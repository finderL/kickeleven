/**
 * @author nttdocomo
 */

/*var TIME_STAMP = '?t=' + new Date().getTime();

seajs.on('fetch', function(data) {
	if (data.uri) {
		data.requestUri = data.uri + TIME_STAMP;
	}
});

seajs.on('define', function(data) {
	if (data.uri) {
		data.uri = data.uri.replace(TIME_STAMP, '');
	}
});*/
seajs.config({
	plugins : ['shim', 'text'],
	base : "./static/js/",
	alias : {
		"jquery" : "jquery-2.0.0.js",
		"underscore" : "underscore.js",
		"modernizr" : "taurus/modernizr",
		"moment" : "taurus/moment"
	},
	map : [['http://localhost:8080/static/js/taurus/', 'http://battle.ship.com/src/']],
	preload : ['jquery', 'underscore', 'modernizr', 'plugin-text'],
	vars : {
		'locale' : (navigator.language || navigator.browserLanguage).toLowerCase()
	},
});

// 加载入口模块
seajs.use("./static/js/main");