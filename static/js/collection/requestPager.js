/**
 * @author nttdocomo
 */
define(function(require) {
	require('backbone.paginator');
	var bbVer = _.map(Backbone.VERSION.split('.'), function(digit) {
		return parseInt(digit, 10);
	});
	return Backbone.Paginator.requestPager.extend({
		search:function(attrs){
			this.query = attrs;
			this.pager();
		},
		pager:function(options){
			if ( !_.isObject(options) ) {
				options = {};
			}
			var self = this,queryAttributes = {};
			self.setDefaults();
			// Some values could be functions, let's make sure
			// to change their scope too and run them
			_.each(_.result(self, "server_api"), function(value, key){
				if( _.isFunction(value) ) {
					value = _.bind(value, self);
					value = value();
				}
				if(value)
					queryAttributes[key] = value;
			});
			_.each(_.result(self, "query"), function(value, key){
				if(value)
					queryAttributes[key] = value;
			});
			
			var queryOptions = _.clone(self.paginator_core);
			_.each(queryOptions, function(value, key){
				if( _.isFunction(value) ) {
					value = _.bind(value, self);
					value = value();
				}
				queryOptions[key] = value;
			});
			
			// Allows the passing in of {data: {foo: 'bar'}} at request time to overwrite server_api defaults
			if( options.data ){
				options.data = decodeURIComponent($.param(_.extend(queryAttributes,options.data)));
			}else{
				options.data = decodeURIComponent($.param(queryAttributes));
			}
			
			queryOptions = _.extend(queryOptions, {
				data: decodeURIComponent($.param(queryAttributes)),
				processData: false,
				url: _.result(queryOptions, 'url')
			}, options);
			return this.fetch( queryOptions );
		},
		sync : function(method, model, options) {
			var queryOptions = options,
			promiseSuccessFormat = !(bbVer[0] === 0 &&
		                                   bbVer[1] === 9 &&
		                                   bbVer[2] === 10),
		    isBeforeBackbone_1_0 = bbVer[0] === 0,
		    success = queryOptions.success;
            queryOptions.success = function ( resp, status, xhr ) {
            	if ( success ) {
            		// This is to keep compatibility with Backbone 0.9.10
            		if (promiseSuccessFormat) {
            			success( resp, status, xhr );
            		} else {
            			success( model, resp, queryOptions );
            		}
            	}
            	/*if ( model && model.trigger ) {
            		model.trigger( 'sync', model, resp, queryOptions );
            	}*/
            };
            
            var error = queryOptions.error;
            queryOptions.error = function ( xhr ) {
            	if ( error ) {
            		error( model, xhr, queryOptions );
            	}
            	if ( model && model.trigger ) {
            		model.trigger( 'error', model, xhr, queryOptions );
            	}
            };
			if(this.isAdmin){
				if(queryOptions.data){
					queryOptions.data['admin'] = 1;
				} else {
					queryOptions.data = {
						'admin' : 1
					};
				}
			}
			
			// Create default values if no others are specified
			/*queryOptions = _.defaults(queryOptions, {
				timeout: 60000,
				cache: false,
				type: 'GET',
				dataType: 'jsonp'
			});*/
			return Backbone.Collection.prototype.sync.call(this, method, model, queryOptions);
            
            /*var xhr = queryOptions.xhr = $.ajax( queryOptions );
            if ( model && model.trigger ) {
            	model.trigger('request', model, xhr, queryOptions);
            }
            return xhr;*/
		}
	});
});