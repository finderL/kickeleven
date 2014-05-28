/**
 * @author nttdocomo
 */
define(function(require){
	var Base = require('../taurus/view/base');
	require('../taurus/lang/date'),
	i18n = require('../i18n/zh-cn');
	return taurus.view('taurus.views.PlayerMiniProfile',Base.extend({
		/*tpl:['<div class="media"><span class="pull-left"><img data-src="holder.js/260x180" alt="260x180" style="width:112px; height:112px;" src="'+taurus.BLANK_IMAGE_URL+'"></span>',
		'<div class="media-body"><ul class="table-ul"><%=list%></ul></div></div>'].join(''),*/
		tpl:['<div class="col-lg-6"><img data-src="holder.js/300x200" alt="..." src="/static/tmp/<%=avatar%>" class="pull-left" height="180" width="180"></div>',
		'<div class="col-lg-6"><div class="form-horizontal"><%_.each(info,function(item,name){%><div class="form-group"><label class="col-sm-5 control-label"><%=_.i18n.__(name.replace(/(^[a-z]|_[a-z])/ig,function($1){return $1.toUpperCase().replace("_"," ")}))%></label><div class="col-sm-7"><p class="form-control-static"><%=item%></p></div></div><%})%></div><div class="position-label"><%=positions%></div></div>'].join(''),
        className:'player-mini-profile clearfix row',
		initialize:function(){
			Base.prototype.initialize.apply(this,arguments);
			//this.listenTo(this.model,'change:year_founded',this.update)
			//this.listenTo(this.model,'change:nation',this.html)
			this.model.on('sync',_.bind(function(){
				this.html();
			},this));
		},
		getTplData:function(){
			var json = this.model.toJSON();
			json.club = json.club ? _.template('<h5><%=_.i18n.__("Current work for %s",club)%></h5>',{
				club:json.club[0].club_name
			}) : '';
			json.age = taurus.Date.getAge(json.date_of_birth, 'yyyy-mm-dd');
			json.date_of_birth = taurus.Date.formatDate(json.date_of_birth,i18n.__('yyyy-mm-dd'));
			json.nation_flag = json.nation.normal_flag;
			json.info = _.pick(json,'date_of_birth','age','height','weight');
			var position = _.uniq(json.position,function(item){
				return item.position_name;
			});
			json.positions = json.position ? _.map(position,function(position){
				return '<span class="label label-success">'+_.find(k11.POSITION,function(item){
					return item.value == position.position_name;
				}).text+'</span>';
			}).join('\n') : '';
			/*json.age = taurus.Date.getAge(json.date_of_birth, 'yyyy-mm-dd')
			json.date_of_birth = taurus.Date.formatDate(json.date_of_birth,'yyyy-mm-dd')
			json.nation_flag = json.nation[0].flag
			json.expires = taurus.Date.formatDate(json.contract.expires,'yyyy-mm-dd')
			var prefered_foot = json.prefered_foot
			json.prefered_foot = '右脚'
			if(prefered_foot[0] > prefered_foot[1]){
				json.prefered_foot = '左脚'
				if(prefered_foot[1] > 14){
					json.prefered_foot = '左右开弓'
				}
			}*/
			return json;
		}
	}));
});
