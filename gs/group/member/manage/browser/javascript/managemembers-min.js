jQuery.noConflict();GSManageMembers=function(){function c(){var f=null,d=null,e=null;
f=jQuery(this);d=jQuery(".ptnCoach :radio");e=f.prop("checked");if(e==true){for(i=0;
i<d.length;i=i+1){jQuery(d[i]).prop("checked",false)}f.prop("checked",true)}}function b(){var g=null,d=null,e=null,f=null;
g=jQuery(this);d=g.attr("id").split("-")[0].split(".")[1];e=jQuery("#"+d+"-actions input");
f=g.prop("checked");if(f==true){for(i=0;i<e.length;i=i+1){jQuery(e[i]).prop("checked",false).attr("disabled","disabled")
}g.removeAttr("disabled").prop("checked",true)}else{for(i=0;i<e.length;i=i+1){jQuery(e[i]).removeAttr("disabled")
}}}function a(){var h=null,d=null,g=null,f=null,e=null;h=jQuery(this);d=h.attr("id").split("-")[0].split(".")[1];
g=h.attr("id").split("-")[1];f=h.prop("checked");if(g=="moderatorAdd"){e=jQuery("#form\\."+d+"-moderatedAdd")
}else{ptnCoachInputName=d+"-ptnCoach";e=[jQuery("#form\\."+d+"-moderatorAdd"),jQuery("#form\\."+d+"-groupAdminAdd"),jQuery("#form\\."+d+"-postingMemberAdd"),jQuery("input[name='form\\."+ptnCoachInputName+"']")]
}if(f==true){for(i=0;i<e.length;i=i+1){jQuery(e[i]).prop("checked",false).attr("disabled","disabled")
}h.removeAttr("disabled").prop("checked",true)}else{for(i=0;i<e.length;i=i+1){jQuery(e[i]).removeAttr("disabled")
}}}return{init:function(){jQuery(".ptnCoach :radio").change(c);jQuery(".remove :checkbox").change(b);
jQuery(".moderatorAdd :checkbox").change(a);jQuery(".moderatedAdd :checkbox").change(a)
}}}();jQuery(window).load(function(){GSManageMembers.init()});