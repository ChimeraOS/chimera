% rebase('base.tpl')

% if platform == 'epic-store':
<p class="platform-login-description">Please <a target="_blank" href="https://www.epicgames.com/id/login?redirectUrl=https://www.epicgames.com/id/api/redirect">login to the Epic Games Store</a> and paste the sid value that appears below.</p>
% elif platform == 'gog':
<p class="platform-login-description">Please <a target="_blank" href="https://login.gog.com/auth?client_id=46899977096215655&layout=client2%22&redirect_uri=https%3A%2F%2Fembed.gog.com%2Fon_login_success%3Forigin%3Dclient&response_type=code">login to GOG</a>. A blank page will appear with a code in the address bar after "code=". Paste the code from the address bar into the input box below.</p>
% end

<form action="/library/{{platform}}/authenticate" method="post" enctype="multipart/form-data">
% if platform == 'epic-store':
	<div class="label">SID</div>
% elif platform == 'gog':
	<div class="label">Code</div>
% end
	<input type="password" name="password"/>

	<button>Login</button>
</form>
