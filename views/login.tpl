% rebase('base.tpl')
<h3>Please enter the password shown on your TV to continue</h3>
<form action="/authenticate" method="post" enctype="multipart/form-data">
	<div class="label">Password</div>
	<input type="password" name="password"/>

	<button>Login</button>
</form>
