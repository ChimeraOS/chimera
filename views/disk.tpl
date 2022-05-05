<form action="/system/storage/format" method="post" enctype="multipart/form-data">
    <p>{{disk["name"]}}, Model: {{disk["model"]}}</p>
    <button name=disk type=submit value={{disk["name"]}}>Format {{disk["name"]}}</button>
</form>
