% rebase('base.tpl')

<p class="platform-login-description">Please <a target="_blank" href="https://www.epicgames.com/id/login?redirectUrl=https://www.epicgames.com/id/api/redirect">login to the Epic Games Store</a> and paste the sid value that appears below.</p>

<form action="/platforms/{{platform}}/authenticate" method="post" enctype="multipart/form-data">
	<div class="label">SID</div>
	<input type="password" name="password"/>

	<button>Login</button>
</form>