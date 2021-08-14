% rebase('base.tpl')
<form action="/system/mangohud/save_config" method="post" enctype="multipart/form-data">
    <h4>MangoHud configuration file</h4>
    <div>
        <textarea name="new_content" id="new_content" cols="40" rows="10">{{file_content}}</textarea>
    </div>

    <a class="info-link" target="_blank" href="https://github.com/flightlessmango/MangoHud#mangohud_config-and-mangohud_configfile-environment-variables">
        Available configuration options
    </a>

    <button>Save</button>
    <button class="delete" formaction="/system/reset_mangohud">Reset</button>
</form>
