% rebase('base.tpl')

% if isInstalledOverview:
<div class="img-container">
    <a href="/library/{{ platform }}/new">
        <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"></img>
    </a>
</div>
% end

% from urllib.parse import quote
% for app in app_list:
<div class="img-container">
    <a href="/library/{{ platform }}/edit/{{ app.content_id }}">
        <img src="{{ quote(app.image_url) }}" alt="{{ app.name }}" title="{{ app.name }}"></img>
    </a>
</div>
% end
