/**
 * @author nttdocomo
 */
seajs.config({
	plugins : ['shim', 'text'],
	base : 'http://'+location.host+'/static/js/',
	alias : {
		"jquery" : "jquery-2.0.0.js",
		"underscore" : "underscore.js",
		"modernizr" : "taurus/modernizr",
		"moment" : "taurus/moment"
	},
	map : [['http://'+location.host+'/static/js/taurus/', 'http://nttdocomo.github.io/taurus/src/']],
	preload : ['jquery', 'underscore', 'modernizr', 'plugin-text'],
	vars : {
		'locale' : (navigator.language || navigator.browserLanguage).toLowerCase()
	},
});