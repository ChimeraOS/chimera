% rebase('base.tpl')
<form action="/mangohud/save_config" method="post" enctype="multipart/form-data">
    <h4>MangoHud configuration file</h4>
    <div>
        <textarea name="new_content" id="new_content" cols="40" rows="10">{{file_content}}</textarea>
    </div>

	<button>Save</button>
</form>
