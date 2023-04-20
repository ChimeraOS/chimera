% rebase('base.tpl')
<script src="/public/alpinejs@3.12.0.min.js"></script>

<script>
function storage() {
	return {
        formattingStatus : null,
        formattingDevice : null,
        isWarningShowing : false,
        devices : [],
        operation : {},

        async init() {
            await this.load();

            setInterval(() => {
                if (this.formattingStatus == 'in-progress') {
                    this.load();
                }
            }, '5000');
        },

        async load() {
            const response = await fetch('/api/storage');
            const data = await response.json();
            this.devices = data.devices;
            this.operation = data.operation;

            this.formattingDevice = this.operation.options.device;
            this.formattingStatus = this.operation.status;
        },

        async reset() {
            const response = await fetch('/api/storage', {
                method : 'POST',
                headers : {
                    'content-type' : 'application/json',
                },
                body : JSON.stringify({
                    operation : 'reset',
                })
            });

            await this.load();
        },

        async formatWarn(device) {
            this.formattingDevice = device.name;
            this.isWarningShowing = true;
        },

        async formatCancel() {
            this.isWarningShowing = false;
        },

        async format() {
            const response = await fetch('/api/storage', {
                method : 'POST',
                headers : {
                    'content-type' : 'application/json',
                },
                body : JSON.stringify({
                    operation : 'format',
                    options : {
                        device : this.formattingDevice,
                    }
                })
            });

            await this.load();
            this.isWarningShowing = false;
        }
    };
}
</script>

<div
    x-data="storage()"
    x-init="init()"
>
    <h2>Storage Config</h2>

    <div x-cloak class="narrow-content" x-show="isWarningShowing">
        <p x-text="`Are you sure you want to format ${formattingDevice}?`"></p>
        <p>This will erase all data on the disk and may take several minutes or more.</p>
        <button @click="formatCancel()">Cancel</button>
        <button class="delete" @click="format()" x-text="`Format ${formattingDevice}`"></button>
    </div>
    <div x-cloak x-show="!isWarningShowing">
        <div x-show="formattingStatus == 'in-progress'">
            <img src="/public/spinner.webp" width="128px">
            <p x-text="`Formatting ${formattingDevice} in progress. This may take several minutes or more.`"></p>
        </div>
        <p x-show="formattingStatus == 'success'" x-text="`Formatting ${formattingDevice} completed successfully.`"></p>
        <p x-show="formattingStatus == 'error'"   x-text="`Formatting ${formattingDevice} failed.`"></p>

        <div x-show="formattingStatus == 'success' || formattingStatus == 'error'">
            <h3>Log</h3>
            <pre style="text-align: left;" x-text="operation.log"></pre>
            <button class="narrow-content" @click="reset()">OK</button>
        </div>

        <table x-show="!formattingStatus" role="grid" style="width:100%;">
            <thead>
                <tr>
                    <th class="optional" scope="col"><b>Model</b></th>
                    <th scope="col"><b>Device</b></th>
                    <th class="optional" scope="col"><b>Mount Point</b></th>
                    <th scope="col"><b>File System</b></th>
                    <th scope="col"></th>
                </tr>
            </thead>
            <tbody>
                <template x-for="device in devices">
                    <tr :class="device.device_type == 'disk' ? 'row-border' : ''">
                        <td class="optional" x-text="device.device_type == 'disk' ? `${device.model}` : ''"></td>
                        <td x-text="`${device.name}`"></td>
                        <td class="optional" x-text="device.mount_point ? `${device.mount_point}` : ''"></td>
                        <td x-text="device.fstype ? `${device.fstype}` : ''"></td>
                        <td>
                            <button class="small" x-show="device.device_type == 'disk'" @click="formatWarn(device)">Format</button>
                        </td>
                    </tr>
                </template>
            </tbody>
        </table>
    <div>
</div>
