% rebase('base.tpl')

<div class="action-content">

	% if get('audio'):
		<div class="action">
						<a class="volume-down" href="/actions/audio/volume_down">
							-
						</a>
						% if get('audio')['muted']:
							<a class="volume" style="color : lightgreen" href="/actions/audio/toggle_mute"><i class="ri-volume-up-fill"></i> {{get('audio')['volume']}}</a>
						% else:
							<a class="volume" style="color : crimson" href="/actions/audio/toggle_mute"><i class="ri-volume-mute-fill"></i> {{get('audio')['volume']}}</a>
						% end
						<a class="volume-up" href="/actions/audio/volume_up">
							+
						</a>
		</div>
	% end

	<a href="/actions/mangohud">
		<div class="action">
			<i class="ri-dashboard-2-fill"></i> Performance Overlay
		</div>
	</a>

	<a href="/actions/steam/overlay">
		<div class="action">
			<i class="ri-stack-fill"></i> Steam Overlay
		</div>
	</a>

	<a href="/actions/retroarch/load_state">
		<div class="action">
			<i class="ri-upload-2-fill"></i> Load Game
		</div>
	</a>

	<a href="/actions/retroarch/save_state">
		<div class="action">
			<i class="ri-download-2-fill"></i> Save Game
		</div>
	</a>

	<a href="/actions/steam/compositor">
		<div class="action">
			<i class="ri-window-fill"></i> Window Mode
		</div>
	</a>

	<a href="/actions/steam/restart">
		<div class="action">
			<i class="ri-refresh-fill"></i> Restart Steam
		</div>
	</a>

	<a href="/actions/suspend">
		<div class="action">
			<i class="ri-pause-circle-fill"></i> Suspend
		</div>
	</a>

	<a href="/actions/reboot">
		<div class="action">
			<i class="ri-restart-fill"></i> Reboot
		</div>
	</a>

	<a href="/actions/poweroff">
		<div class="action">
			<i class="ri-shut-down-line"></i> Power Off
		</div>
	</a>
</div>