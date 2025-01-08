% rebase('base.tpl', content_share_only=get('content_share_only'))
<script src="/public/alpinejs@3.12.0.min.js"></script>

<script>
function storage() {
	return {
        OPERATIONS : {
            format : {
                displayName : 'Format',
                deviceType : 'disk',
                warningMessage : {
                    header : dev => `Are you sure you want to format ${dev}?`,
                    body : () => 'This will erase all data on the disk and may take several minutes or more.',
                    action : dev => `Format ${dev}`,
                },
                progressMessage : dev => `Formatting ${dev} in progress. This may take several minutes or more.`,
                successMessage : dev => `Formatting ${dev} completed successfully.`,
                errorMessage : dev => `Formatting ${dev} failed.`,
            },
            add : {
                displayName : 'Add to Steam',
                deviceType : 'partition',
                progressMessage : dev => `Adding ${dev} to Steam.`,
                successMessage : dev => `Adding ${dev} to Steam completed successfully.`,
                errorMessage : dev => `Adding ${dev} to Steam failed.`,
            },
        },
        operationStatus : null,
        operationDevice : null,
        isWarningShowing : false,
        devices : [],
        operation : {},

        async init() {
            await this.load();

            setInterval(() => {
                if (this.operationStatus == 'in-progress') {
                    this.load();
                }
            }, '5000');
        },

        async load() {
            const response = await fetch('/api/storage');
            const data = await response.json();
            this.devices = data.devices;
            this.operation = data.operation;

            this.operationDevice = this.operation.options.device;
            this.operationStatus = this.operation.status;
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

        async operationCancel() {
            this.isWarningShowing = false;
        },

        async doOperation(operation, device, warn=false) {
            this.operation = { type : operation };

            if (device) {
                this.operationDevice = device.name;
            }

            if (warn) {
                this.isWarningShowing = true;
                return;
            }

            const response = await fetch('/api/storage', {
                method : 'POST',
                headers : {
                    'content-type' : 'application/json',
                },
                body : JSON.stringify({
                    operation,
                    options : {
                        device : this.operationDevice,
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
        <p x-text="OPERATIONS[operation.type].warningMessage.header(operationDevice)"></p>
        <p x-text="OPERATIONS[operation.type].warningMessage.body(operationDevice)"></p>
        <button @click="operationCancel()">Cancel</button>
        <button class="delete" @click="doOperation(operation.type)" x-text="OPERATIONS[operation.type].warningMessage.action(operationDevice)"></button>
    </div>
    <div x-cloak x-show="!isWarningShowing">
        <div x-show="operationStatus == 'in-progress'">
            <img src="/public/spinner.webp" width="128px">
            <p x-text="OPERATIONS[operation.type].progressMessage(operationDevice)"></p>
        </div>
        <p x-show="operationStatus == 'success'" x-text="OPERATIONS[operation.type].successMessage(operationDevice)"></p>
        <p x-show="operationStatus == 'error'"   x-text="OPERATIONS[operation.type].errorMessage(operationDevice)"></p>

        <div x-show="operationStatus == 'success' || operationStatus == 'error'">
            <h3>Log</h3>
            <pre style="text-align: left;" x-text="operation.log"></pre>
            <button class="narrow-content" @click="reset()">OK</button>
        </div>

        <table x-show="!operationStatus" role="grid" style="width:100%;">
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
                            <template x-for="op in Object.keys(OPERATIONS)">
                                <button class="small" x-show="device.device_type == OPERATIONS[op].deviceType" @click="doOperation(op, device, !!OPERATIONS[op].warningMessage)" x-text="OPERATIONS[op].displayName"></button>
                            </template>
                        </td>
                    </tr>
                </template>
            </tbody>
        </table>
    <div>
</div>
