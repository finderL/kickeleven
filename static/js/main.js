/**
 * @author nttdocomo
 */
define(function(require){
	require('./taurus/taurus');
	var Router = require('./route');
	var panel,
		clubCreatePanel,
		messageDialog,
	i18n = require('./i18n/{locale}');
	taurus.augmentObject('taurus',{
		POSITION:['Striker','Attack Midfielder','Midfielder','Defensive Midfielder','Wing Back','Defender','Sweeper','Goalkeeper']
	});
	taurus.itemPathPrefix = '';
	new Router;
	Backbone.history.start();
});
