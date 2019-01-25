/**
 * Created by tarena on 19-1-1.
 */

$(function(){


	var error_password = false;
	var error_check_password = false;




	$('#pwd').blur(function() {
		check_pwd();
	});

	$('#cpwd').blur(function() {
		check_cpwd();
	});




	function check_pwd(){
		var len = $('#pwd').val().length;
		if(len<7||len>15)
		{
			$('#pwd').next().html('密码最少7位，最长15位');
            $('#pwd').next().show()
		}
		else
		{
			$('#pwd').next().hide();
			error_password = false;
		}
	}


	function check_cpwd(){
		var pass = $('#pwd').val();
		var cpass = $('#cpwd').val();

		if(pass!=cpass)
		{
			$('#cpwd').next().html('两次输入的密码不一致');
			$('#cpwd').next().show();
			error_check_password = true;
		}
		else{
			$('#cpwd').next().hide();
			error_check_password = false;
		}

	}


	$('#ps').submit(function() {
		check_pwd();
		check_cpwd();
		if( error_password == false && error_check_password == false )
		{
			return true;
		}
		else
		{
			return false;
		}

	});





});
