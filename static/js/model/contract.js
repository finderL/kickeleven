/**
 * @author nttdocomo
 */
define(function(require) {
	return taurus.klass('taurus.model.Contract', Backbone.Model.extend({
		url:function(){
			return '/api/contract/' + (this.get('id') || this.get('key')) + '/'
		},
		reject:function(options){
			this.save({'status':2},$.extend({
				emulateJSON:true,
				url:'/api?method=contract.reject',
				type:'POST',
				data:{
					id:this.get('id')
				},
				wait: true
			},options))
			/*$.ajax($.extend(options,{
				url:'/api/contract/reject/',
				type:'POST',
				data:{
					id:this.get('id')
				},
				success:_.bind(function(){
					this.set('status',2)
				},this)
			}))*/
		},
		accept:function(options){
			this.save({'status':1},$.extend({
				emulateJSON:true,
				url:'/api?method=contract.accept',
				type:'POST',
				data:{
					id:this.get('id')
				},
				wait: true
			},options))
			/*$.ajax($.extend(options,{
				url:'/api/contract/accept/',
				type:'POST',
				data:{
					id:this.get('id')
				},
				success:_.bind(function(){
					this.set('status',1)
				},this)
			}))*/
		}
	}));
})