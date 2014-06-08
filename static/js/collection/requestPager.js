/**
 * @author nttdocomo
 */
define(function(require) {
	require('backbone.paginator');
	return Backbone.Paginator.requestPager.extend({
		search:function(attrs){
			this.query = attrs;
			this.pager();
		},
		sync : function(method, model, options) {
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
			if(this.isAdmin){
				queryAttributes.admin = 1;
			}
			
			var queryOptions = _.clone(self.paginator_core);
			_.each(queryOptions, function(value, key){
				if( _.isFunction(value) ) {
					value = _.bind(value, self);
					value = value();
				}
				queryOptions[key] = value;
			});
			
			// Create default values if no others are specified
			queryOptions = _.defaults(queryOptions, {
				timeout: 60000,
				cache: false,
				type: 'GET',
				dataType: 'jsonp'
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
			
			var bbVer = Backbone.VERSION.split('.');
			var promiseSuccessFormat = !(parseInt(bbVer[0], 10) === 0 &&
                                   parseInt(bbVer[1], 10) === 9 &&
                                   parseInt(bbVer[2], 10) === 10);
                                   
            var success = queryOptions.success;
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
            
            var xhr = queryOptions.xhr = $.ajax( queryOptions );
            if ( model && model.trigger ) {
            	model.trigger('request', model, xhr, queryOptions);
            }
            return xhr;
		}
	});
});