% rebase('base.tpl', content_share_only=get('content_share_only'))

<h2>Uploaded Files</h2>
<ul>
% for key, (path, filename) in tmpfiles.items():
    <li>
        <strong>{{filename}}</strong> (Temp name: {{key}})
        <br>
        <span>Path: {{path}}</span>
    </li>
% end
</ul>
