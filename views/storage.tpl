% rebase('base.tpl')
<form action="/system/storage/format" method="post" enctype="multipart/form-data">
    <h1>Storage Config</h1>
    <ul>
    % for disk in disks:
        % include('disk.tpl', disk=disk)
    % end
    </ul>
</form>
