% rebase('base.tpl')

% if isInstalledOverview:
<a href="/library/flathub/new">
    <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"/>
</a>
% end

% for app in app_list:
<a href="/library/flathub/edit/{{ app.flatpak_id }}">
    <img src="/images/flathub/{{ app.flatpak_id }}.png" alt="{{ app.name }}" title="{{ app }}"/>
</a>
% end
