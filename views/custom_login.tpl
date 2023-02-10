% rebase('base.tpl')

% if platform == 'epic-store':
<p class="platform-login-description">Please make sure you are logged in to your Epic Games Store account, then <a target="_blank" href="https://www.epicgames.com/id/api/redirect?clientId=34a02cf8f4414e29b15921876da36f9a&responseType=code">click this link</a> and paste the authorization code that appears into the input box below.</p>
% elif platform == 'gog':
<p class="platform-login-description">Please <a target="_blank" href="https://login.gog.com/auth?client_id=46899977096215655&amp;layout=client2%22&amp;redirect_uri=https%3A%2F%2Fembed.gog.com%2Fon_login_success%3Forigin%3Dclient&amp;response_type=code">login to GOG</a>. A blank page will appear with a code in the address bar after "code=". Paste the code from the address bar into the input box below.</p>
% end

<form action="/library/{{platform}}/authenticate" method="post" enctype="multipart/form-data">
% if platform == 'epic-store':
	<div class="label">Authorization Code</div>
% elif platform == 'gog':
	<div class="label">Code</div>
% end
	<input type="password" name="password"/>

	<button>Login</button>
</form>
