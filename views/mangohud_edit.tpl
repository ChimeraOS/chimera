% rebase('base.tpl')
<form action="/mangohud/save_config" method="post" enctype="multipart/form-data">
    <h4>MangoHud configuration file</h4>
    <hr>
    You'll be able to edit MangoHud configuration here by setting it's content.
    <div>
        <textarea name="new_content" id="new_content">{{file_content}}</textarea>
    </div>

	<button>Save</button>
</form>
