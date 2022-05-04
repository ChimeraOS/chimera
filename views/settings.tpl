% rebase('base.tpl')
<form action="/system/update" method="post" enctype="multipart/form-data">
    <h4>Performance Overlay</h4>
    <hr>
    <a class="button" href="/system/mangohud/edit_config">
        Configure MangoHud
    </a>
    
    <h4>Storage</h4>
    <hr>
    <a class="button" href="/system/storage">
        Configure Storage
    </a>

    <h4>Logging in</h4>
    <hr>
    By default a random password is shown on your TV every time you try to log in here. This can be disabled by configuring a set password.

    <div class="label">Generate a new password for each login</div>
	<input type="checkbox" name="generate_password" id="generate_password" onclick="setShowPasswordField()" {{'checked' if not settings["keep_password"] else ''}} />

    <div id="password">
    <div class="label">Log in password</div>
	<input name="login_password" id="login_password" type="password" placeholder="password" pattern=".{8,}" title="8 characters or more" oninput="setConfirmPasswordRequired(this)"/>
	<input id="confirm_login_password" type="password" placeholder="confirm password" oninput="passwordMatchCheck(this)"/>

	</div>

    <h4>FTP Server</h4>
    <hr>
    FTP can be used for transferring files to and from this machine. You can connect to use with an FTP client at ftp://{{hostname}}:{{settings["ftp_port"]}}/ if enabled.<br>

	<div class="label">Enable FTP server</div>
	<input type="checkbox" name="enable_ftp_server" id="enable_ftp_server" onclick="setShowFTPSettings()" {{'checked' if settings["enable_ftp_server"] else ''}} />

    <div id="ftp">
        <div class="label">FTP username</div>
        <input name="ftp_username" value="{{settings["ftp_username"]}}" pattern=".{5,}" title="5 characters or more"/>

        <div class="label">FTP password</div>
        <input name="ftp_password" value="{{settings["ftp_password"]}}" pattern=".{8,}" title="8 characters or more"/>

        <div class="label">FTP port</div>
        <input type="number" name="ftp_port" value="{{settings["ftp_port"]}}" min="1025" max="65535"/>
    </div>

	<h4>SSH</h4>
    <hr>
    SSH allows you to access the command line of this machine remotely. Once your SSH public key has been added, you can connect to this server with "ssh {{username}}@{{hostname}}".<br>

    <div class="label">Add public key</div>
    <input name="ssh_key"/>

    % if len(ssh_key_ids) > 0:
    <div class="label">Current public keys</div>
        <table class="settings">
            <thead>
            <tr>
                <th>ID</th>
                <th>Delete</th>
            </tr>
            </thead>
            % for key_id in ssh_key_ids:
                <tr>
                    <td>{{key_id}}</td>
                    <td><input type="checkbox" name="{{key_id}}" /></td>
                </tr>
            % end
        </table>
    % end

	<button>Save</button>
</form>
<script>
    function setShowPasswordField() {
        let checkBox = document.getElementById('generate_password');
        let passwordDiv = document.getElementById('password');
        let passwordField = document.getElementById('login_password');
        if (checkBox.checked) {
            passwordDiv.style.visibility = 'hidden';
            passwordDiv.style.display = 'none';
            passwordField.required = false;
        } else {
            passwordDiv.style.visibility = 'visible';
            passwordDiv.style.display = 'block';
            % if not password_is_set:
                passwordField.required = true;
            % end
        }
    }
    function setShowFTPSettings() {
        let checkBox = document.getElementById('enable_ftp_server');
        let ftpDiv = document.getElementById('ftp');
        if (checkBox.checked) {
            ftpDiv.style.visibility = 'visible';
            ftpDiv.style.display = 'block';
        } else {
            ftpDiv.style.visibility = 'hidden';
            ftpDiv.style.display = 'none';
        }
    }
    function passwordMatchCheck(input) {
        let passwordField = document.getElementById('login_password');
        if (input.value != passwordField.value) {
            input.setCustomValidity('Must match password field');
        } else {
            input.setCustomValidity('');
        }
    }
    function setConfirmPasswordRequired(input) {
        let confirm = document.getElementById('confirm_login_password')
        if (input.value.length > 0) {
            confirm.required = true
        } else {
            confirm.required = false
        }
    }

    setShowPasswordField()
    setShowFTPSettings()
</script>
