% rebase('base.tpl')
<form action="/settings/update" method="post" enctype="multipart/form-data">
    <h4>Logging in</h4>
    <hr>
    <div class="label">Generate a new password for each login</div>
	<input type="checkbox" name="generate_password" id="generate_password" onclick="setShowPasswordField()" {{'checked' if not settings["keep_password"] else ''}} />

    <div id="password">
    <div class="label">Log in password</div>
	<input name="login_password" value="{{settings["password"]}}" />
	</div>

    <h4>FTP Server</h4>
    <hr>
	<div class="label">Enable FTP server</div>
	<input type="checkbox" name="enable_ftp_server" id="enable_ftp_server" onclick="setShowFTPSettings()" {{'checked' if settings["enable_ftp_server"] else ''}} />

    <div id="ftp">
        <div class="label">FTP username</div>
        <input name="ftp_username" value="{{settings["ftp_username"]}}" />

        <div class="label">FTP password</div>
        <input name="ftp_password" value="{{settings["ftp_password"]}}"" />

        <div class="label">FTP port</div>
        <input type="number" name="ftp_port" value="{{settings["ftp_port"]}}"" />
    </div>

	<button>Save</button>
</form>
<script>
    function setShowPasswordField() {
        let checkBox = document.getElementById('generate_password')
        let passwordDiv = document.getElementById('password')
        if (checkBox.checked) {
            passwordDiv.style.visibility = 'hidden'
            passwordDiv.style.display = 'none';
        } else {
            passwordDiv.style.visibility = 'visible'
            passwordDiv.style.display = 'block';
        }
    }
    function setShowFTPSettings() {
        let checkBox = document.getElementById('enable_ftp_server')
        let ftpDiv = document.getElementById('ftp')
        if (checkBox.checked) {
            ftpDiv.style.visibility = 'visible'
            ftpDiv.style.display = 'block';
        } else {
            ftpDiv.style.visibility = 'hidden'
            ftpDiv.style.display = 'none';
        }
    }
    setShowPasswordField()
    setShowFTPSettings()
</script>