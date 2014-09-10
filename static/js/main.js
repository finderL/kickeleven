/**
 * @author nttdocomo
 */
define(function(require){
	require('./taurus/taurus');
	var Menu = require('./taurus/menu/menu');
	var Router = require('./route');
	var panel,
		clubCreatePanel,
		messageDialog,
	i18n = require('./i18n/{locale}');
	taurus.augmentObject('taurus',{
		POSITION:['Striker','Attack Midfielder','Midfielder','Defensive Midfielder','Wing Back','Defender','Sweeper','Goalkeeper']
	});
	taurus.itemPathPrefix = '';
	$(document).on('click','.btn-logout',function(){
		var form = document.createElement('form'), input = document.createElement('inpu')
		form.action = '/logout/';
		form.method = 'POST';
		form.innerHTML = '<input type="text" value="'+location.pathname + location.hash+'" name="redirect" />';
		document.body.appendChild(form);
		form.submit();
		return false;
	});
	new Menu({
		triggerEl:$('.navbar-collapse > .navbar-nav:eq(0) > li:eq(2) > a'),
		menus:[{
			text:'National',
			menus:[{
				text:'Premier League',
				href:'/#!competition/1/'
			},{
				text:'La Liga',
				href:'/#!competition/2/'
			},{
				text:'1.Bundesliga',
				href:'/#!competition/3/'
			},{
				text:'Ligue 1',
				href:'/#!competition/4/'
			},{
				text:'Serie A',
				href:'/#!competition/5/'
			}]
		}]
	})
	new Router;
	var modelFetch = Backbone.Model.prototype.fetch;
    Backbone.Model.prototype.fetch = function(options){
    	options = options ? _.clone(options) : {};
    	var model = this;
    	var error = options.error;
    	options.error = function(resp){
    		require.async('./taurus/widget/prompt',function(Prompt){
    			(new Prompt({
    				'title':'Error',
    				'content':'You got an error, try again?',
	            })).on('confirm',function(){
    				model.fetch(options);
	            }).show();
	        });
	        if (error) error(model, resp, options);
        };
        modelFetch.call(this,options);
    };
	var collectionFetch = Backbone.Collection.prototype.fetch;
    Backbone.Collection.prototype.fetch = function(options){
    	options = options ? _.clone(options) : {};
    	var collection = this;
    	var error = options.error;
    	options.error = function(resp){
    		require.async('./taurus/widget/prompt',function(Prompt){
    			(new Prompt({
    				'title':'Error',
    				'content':'You got an error, try again?',
	            })).on('confirm',function(){
    				collection.fetch(options);
	            }).show();
	        });
	        if (error) error(collection, resp, options);
        };
        collectionFetch.call(this,options);
    }
	Backbone.history.start();
});
