% rebase('base.tpl')

% if isInstalledOverview:
<div class="app-container">
    <div class="img-container">
        <a href="/library/{{ platform }}/new{{ '?remote=true' if remote == True else '' }}">
            <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut">
        </a>
    </div>
     <p class="title">&nbsp;</p>
</div>
% end

% from urllib.parse import quote
% for app in app_list:
% icon = app.get('status_icon')
% icon = icon + '  ' if icon else ''
<div class="app-container">
    <div class="img-container">
        <a href="/library/{{ platform }}/edit/{{ quote(app.content_id) }}{{ '?remote=true' if remote == True else '' }}">
            <img src="{{ app.image_url }}" alt="{{ app.name }}" title="{{ icon }}{{ app.name }}">
        </a>
    </div>
    % if not remote:
    <p class="title">{{ icon }}{{ app.name }}</p>
    % end
</div>
% end


% if not app_list and not isInstalledOverview:
% if showAll:
    <p>No content available to install</p>
% else:
    <p>No known compatible titles found</p>
% end
% end

% if not showAll and not isInstalledOverview:
    <div>
        <a style="min-width: 200px; width: 25%; display: inline-block;" class="button" href="?showAll=true">Show All Titles</a>
    </div>
% end
