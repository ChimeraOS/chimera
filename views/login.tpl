% rebase('base.tpl')
% if keep_password:
<h3>Please enter your password to continue</h3>
% else:
<h3>Please enter the password shown on your display to continue</h3>
% end
% if failed:
    Given password was incorrect!
% end
<form action="/authenticate" method="post" enctype="multipart/form-data">
	<div class="label">Password</div>
	<input type="password" name="password"/>

	<button>Login</button>
</form>

% if failed and keep_password:
<form action="/forgotpassword">
	<button class="delete">Forgot password</button>
</form>
% end