# ODrive Modular Component

This module implements the motor driver for ODrive Robotics' [ODrive S1](https://odriverobotics.com/shop/odrive-s1) and [ODrive Pro](https://odriverobotics.com/shop/odrive-pro) motors to be used with [`viam-server`](https://docs.viam.com/get-started/installation/). This driver supports either a `serial` or `canbus` motor.

## Getting Started

To use this module, follow the instructions to [add a module from the Viam registry](https://docs.viam.com/registry/configure/), choose the **Motor** component, and select the `odrive:serial` or `odrive:canbus` model from the [`odrive` module](https://app.viam.com/module/viam/odrive), depending on how you have connected your ODrive motor.

## Configuration

### Prepare your single-board computer

1. If you haven’t already, [install viam-server](https://docs.viam.com/get-started/installation/) on your single-board computer.
2. Install [`odrivetool`](https://docs.odriverobotics.com/v/latest/interfaces/odrivetool.html), [`python-can`](https://pypi.org/project/python-can/), [`cantools`](https://pypi.org/project/cantools/), and the [Viam Python SDK](https://python.viam.dev).
3. Enable SPI communication on your single-board computer to support the use of several common CANHats. If you are using a Raspberry Pi, see [these instructions](https://docs.viam.com/get-started/installation/prepare/rpi-setup/#enable-communication-protocols). Other single-board computers may have other ways of setting up CANBus communications; consult the documentation for your specific board for further guidance.

### Configure your ODrive motor hardware

> [!NOTE]  
> When making the initial connection to set up the ODrive, you must make a `serial` connection. If you intend to use a `canbus` connection, you can either leave the serial connection plugged in, or remove it and just leave the CANH and CANL pins wired after you initially set up the ODrive.

Use `odrivetool` to configure and tune your motor properly. This configuration remains on the same ODrive motor controller across reboots, but you can run `odrivetool` again to make changes to the configuration as needed. See the [ODrive documentation](https://docs.odriverobotics.com/v/latest/getting-started.html) for more information.
   * Note that `iq_msg_rate_ms` in the config defaults to `0`, and you **must** set this to around `100` to use the [motor API's `SetPower` method](https://docs.viam.com/components/motor/#setpower).
   * See the section [Add an `odrive_config_file`](#add-an-odrive_config_file) for more information on dynamic configuration.
* See the [ODrive CAN documentation](https://docs.odriverobotics.com/v/latest/can-guide.html) for detailed information on how to set up CAN on your ODrive.

### Connect your ODrive to your single-board computer

Connect your ODrive motor to your single-board computer in one of the following ways:

* For a `serial` connection: plug the [USB Isolator for ODrive](https://odriverobotics.com/shop/usb-c-to-usb-a-cable-and-usb-isolator) into a USB port on your board, and then plug a USB-A to USB-C cable from the isolator to the ODrive.
* For a `canbus` connection: wire the CANH and CANL pins from your board to your ODrive. Refer to the [ODrive pinout diagram](https://docs.odriverobotics.com/v/latest/pinout.html) for further guidance.
    * You must make a `serial` connection initially to set up your ODrive, even if you intend to use a `canbus` connection eventually. After setting up the ODrive using a `serial` connection, if you wish to use the `canbus` model, you can either leave the serial connection plugged in or remove it and leave only the CANH and CANL pins wired.
    * If you are using a Raspberry Pi, you must run `sudo ip link set can0 up type can bitrate <baud_rate>` in the terminal on your single-board computer in order to receive CAN messages. See [Troubleshooting: CAN Link Issues](#can-link-issues) for more details.

### Configure the ODrive motor

> [!NOTE]  
> Before configuring your motor, you must [create a robot](https://docs.viam.com/fleet/machines/#add-a-new-robot).

Navigate to the **Config** tab of your robot’s page in [the Viam app](https://app.viam.com/). Click on the **Components** subtab and click **Create component**. Select the `motor` type, then select the `odrive:serial` or `odrive:canbus` model. Enter a name for your motor and click **Create**.

On the new component panel, copy and paste the following attribute template into your motor’s **Attributes** box, depending on whether you are using a `serial` connection or a `canbus` connection:

### `viam:odrive:serial`

```json
{
  "serial_number": "NUM000",
  "odrive_config_file": "local/path/to/motor/config.json"
}
```

Update the `serial_number` field with the specific serial number of your ODrive motor (if you are using more than one), and replace the `odrive_config_file` path with the path to your file, as written by `odrivetool` when you [configured your ODrive motor hardware](#configure).

### `viam:odrive:canbus`

```json
{
  "canbus_node_id": 0
}
```

Update the `canbus_node_id` (int) to the node ID of whichever CAN node you'd like to use.

> [!NOTE]  
> For more information, see [Configure a Robot](https://docs.viam.com/build/configure/).

### Attributes

The following attributes are available for the motor resources available in the Viam ODrive module:

| Name | Type | Inclusion | Description |
| ---- | ---- | --------- | ----------- |
| `canbus_node_id` | int | Optional | Required for successful initialization of the `"canbus"` type. <br> Node ID of the CAN node you would like to use. You configured this when [setting up your ODrive](https://docs.odriverobotics.com/v/latest/can-guide.html#setting-up-the-odrive). <br> Example: `0` |
| `odrive_config_file` | string | Optional | Filepath of a separate JSON file containing your ODrive's native configuration. </br> See the [Odrive S1 Modular Component repository](https://github.com/viamrobotics/odrive/tree/main/sample-configs) for an example of this file. |
| `serial_number` | string | Optional | The serial number of the ODrive. Note that this is not necessary if you only have one ODrive connected. See [Troubleshooting](#hanging) for help finding this value. |
| `canbus_baud_rate` | string | Optional | [Baud rate](https://docs.odriverobotics.com/v/latest/can-guide.html#setting-up-the-odrive) of the ODrive CAN protocol. This attribute is only available for `"canbus"` connections. </br> Use [`odrivetool`](https://docs.odriverobotics.com/v/latest/odrivetool.html) to obtain this value with `<odrv>.can.config.baud_rate`. Format the string as a multiple of 1000 (k). <br> Example: `"250k"` |

Check the [**Logs** tab](https://docs.viam.com/program/debug/) of your machine in the Viam app to make sure your ODrive motor has connected and no errors are being raised.

### Add an `odrive_config_file`

To add an `odrive_config_file` and reconfigure your ODrive natively each time the motor is initialized on the robot:

1. Using `odrivetool`, run the `odrivetool backup-config config.json` command on your single-board computer to extract your configurations from your ODrive to a file named `config.json`. See the [ODrive documentation](https://docs.odriverobotics.com/v/latest/odrivetool.html#configuration-backup) for more info.
2. Set `iq_msg_rate_ms` in the configuration file to around `100` to use the [motor API's `SetPower` method](https://docs.viam.com/components/motor/#setpower).
3. If you add an `odrive_config_file` to an `canbus` motor, you must leave the serial connection established with your ODrive plugged in to the USB port, in addition to wiring the CANH and CANL pins. Alternatively, you can run the `odrivetool restore-config /path/to/config.json` command in your terminal instead of adding an `odrive_config_file`.

See the [ODrive sample `config.json` file](https://github.com/viamrobotics/odrive/tree/main/sample-configs) for an example of an `odrive_config_file`.

### Example `serial` configuration

This example shows the configuration for an ODrive motor using a `serial` connection, including an `odrive_config_file`.

You can add or edit this configuration on your robot's page on the [Viam app](https://app.viam.com/).
Navigate to the **Config** tab on your robot's page and select **Raw JSON** mode.

```json
{
  "modules": [
    {
      "type": "registry",
      "name": "viam_odrive",
      "module_id": "viam:odrive",
      "version": "0.0.13"
    }
  ],
  "components": [
    {
      "name": "my-odrive-motor",
      "model": "viam:odrive:serial",
      "type": "motor",
      "namespace": "rdk",
      "attributes": {
        "odrive_config_file": "/path/to/my/config.json"
      },
      "depends_on": []
    }
  ]
}
```

### Example `canbus` configuration

This example shows the configuration for two ODrive motors using a `canbus` connection, where each motor specifies its own `odrive_config_file`.

You can add or edit this configuration on your robot's page on the [Viam app](https://app.viam.com/).
Navigate to the **Config** tab on your robot's page and select **Raw JSON** mode.

```json
{
  "modules": [
    {
      "type": "registry",
      "name": "viam_odrive",
      "module_id": "viam:odrive",
      "version": "0.0.13"
    }
  ],
  "components": [
    {
      "model": "viam:odrive:canbus",
      "namespace": "rdk",
      "attributes": {
        "canbus_node_id": 0,
        "odrive_config_file": "/path/to/first/config.json",
        "serial_number": "NUM0001"
      },
      "depends_on": [],
      "type": "motor",
      "name": "my-odrive-motor"
    },
    {
      "model": "viam:odrive:canbus",
      "namespace": "rdk",
      "attributes": {
        "canbus_node_id": 2,
        "odrive_config_file": "/path/to/second/config.json",
        "serial_number": "NUM0002"
      },
      "depends_on": [],
      "type": "motor",
      "name": "my-odrive-motor-2"
    }
  ]
}
```

## Next Steps

- To test your ODrive motor, go to the [**Control** tab](https://docs.viam.com/fleet/machines/#control).
- To write code to control your ODrive motor, use one of the [available SDKs](https://docs.viam.com/build/program/).
- To view examples using a motor component, explore [these tutorials](https://docs.viam.com/tutorials/).
  
## Troubleshooting

### Unstable Behavior
* The motor is likely not properly tuned. 
See the [ODrive documentation](https://docs.odriverobotics.com/v/latest/control.html) for instructions on how to tune.

### Hanging
* If you have provided a serial number, make sure it is the correct serial number. ODrives have **2 serial numbers**: one that will be printed out when you start `odrivetool`, and one that can be accessed in `odrivetool` by running `odrv0.serial_number`. The **correct** serial number is the one that is printed out when you start `odrivetool`.
* If you have not provided a serial number or you are sure you have provided the correct serial number, you are likely connected to the ODrive elsewhere. Make sure any connections via Python, `odrivetool` or the GUI are closed.

### CAN Link Issues
* If you get an error of `"Device or resource busy"`, try setting CAN down and back up with the command `sudo ip link set can0 down` followed by `sudo ip link set can0 up type can bitrate <baud_rate>`
    * You will have to do this any time you want to change the baud rate
* If you get an error of `"Network is down"`, try setting CAN up with the command `sudo ip link set can0 up type can bitrate <baud_rate>`

## License
Copyright 2021-2023 Viam Inc.

Apache 2.0 - See [LICENSE](https://github.com/viamrobotics/odrive/blob/main/LICENSE) file
