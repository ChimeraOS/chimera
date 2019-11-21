% rebase('base.tpl')

% if isInstalledOverview:
<a href="/platforms/flathub/new">
    <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"></img>
</a>
% end

% for app in app_list:
<a href="/platforms/flathub/edit/{{ app.flatpak_id }}">
    <img src="/images/flathub/{{ app.flatpak_id }}.png" alt="{{ app.name }}" title="{{ app }}"></img>
</a>
% end
