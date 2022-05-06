% rebase('base.tpl')
<form action="/system/storage/format" method="post" enctype="multipart/form-data">
    <h1>Storage Config</h1>
    <ul>
    % for disk in disks:
        <p>{{disk["name"]}}, Model: {{disk["model"]}}</p>
        % for part in disk["partitions"]:
	    <p> Partition {{part["name"]}} is mounted on '{{part["mount_point"]}}' as {{part["fstype"]}}</p>
        % end
        <button name=disk type=submit value={{disk["name"]}}>Format {{disk["name"]}}</button>
    % end
    </ul>
</form>
