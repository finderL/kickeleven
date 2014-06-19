/**
 * @author nttdocomo
 */
seajs.config({
	plugins : ['shim', 'text'],
	base : 'http://'+location.host+'/static/js/',
	alias : {
		"jquery" : "jquery-2.0.0.js",
		"underscore" : "underscore.js",
		"modernizr" : "http://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.2/modernizr.min.js",
		"backbone" : "http://cdnjs.cloudflare.com/ajax/libs/backbone.js/1.1.2/backbone-min.js",
		"backbone.paginator":"http://cdnjs.cloudflare.com/ajax/libs/backbone.paginator/0.8/backbone.paginator.min.js",
		"moment" : "http://cdnjs.cloudflare.com/ajax/libs/moment.js/2.6.0/moment.min.js"
	},
	map : [['http://'+location.host+'/static/js/taurus/', 'http://nttdocomo.github.io/taurus/src/']],
	preload : ['jquery', 'underscore', 'modernizr', 'plugin-text'],
	vars : {
		'locale' : (navigator.language || navigator.browserLanguage).toLowerCase()
	},
});