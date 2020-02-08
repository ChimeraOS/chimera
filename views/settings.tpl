% rebase('base.tpl')
<form action="/settings/update" method="post" enctype="multipart/form-data">
	<div class="label">Enable FTP server</div>
	<input type="checkbox" name="enable_ftp_server" {{'checked' if settings["enable_ftp_server"] else ''}} />

	<div class="label">FTP username</div>
	<input name="ftp_username" value="{{settings["ftp_username"]}}" />

	<div class="label">FTP password</div>
	<input name="ftp_password" value="{{settings["ftp_password"]}}"" />

    <div class="label">FTP port</div>
	<input type="number" name="ftp_port" value="{{settings["ftp_port"]}}"" />

	<button>Save</button>
</form>
