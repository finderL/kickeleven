/**
 * @author nttdocomo
 */
seajs.config({
	plugins : ['shim', 'text'],
	base : 'http://'+location.host+'/static/js/',
	alias : {
		"underscore" : "underscore.js",
		"modernizr" : "http://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.2/modernizr.min.js",
		"backbone" : "http://cdnjs.cloudflare.com/ajax/libs/backbone.js/1.1.2/backbone-min.js",
		"backbone.paginator":"http://cdnjs.cloudflare.com/ajax/libs/backbone.paginator/0.8/backbone.paginator.min.js",
		"moment" : "http://cdnjs.cloudflare.com/ajax/libs/moment.js/2.6.0/moment.min.js"
	},
	map : [['http://www.kick11.us/static/js/taurus/', 'http://taurus.kick11.us/']],
	preload : ['plugin-text'],
	vars : {
		'locale' : (navigator.language || navigator.browserLanguage).toLowerCase()
	},
});