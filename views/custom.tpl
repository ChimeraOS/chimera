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
% if not app_list:
<p>No content available to install</p>
% else:
    % for app in app_list:
    <div class="app-container">
        <div class="img-container">
            <a href="/library/{{ platform }}/edit/{{ app.content_id }}{{ '?remote=true' if remote == True else '' }}">
                <img src="{{ app.image_url }}" alt="{{ app.name }}" title="{{ app.get('status_icon') }} {{ app.name }}">
            </a>
        </div>
        <p class="title">{{app.name}}</p>
    </div>
    % end
% end

% if not showAll and not isInstalledOverview:

    % if len(app_list) == 0:
        <p>No known compatible titles found</p>
    % end

    <div>
        <a style="min-width: 200px; width: 25%; display: inline-block;" class="button" href="?showAll=true">Show All Titles</a>
    </div>
% end
