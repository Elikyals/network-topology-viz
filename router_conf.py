from jnpr.junos import Device
from jnpr.junos.exception import ConnectError, CommitError
from jnpr.junos.utils.config import Config

devices = [
    {
        # Router1
        "mgnt_ip": "192.168.1.35",
        'if_config': {
            'ge-0/0/1': "72.114.96.1/30",
            'ge-0/0/3': "72.114.96.26/30",
            'lo0': "72.114.96.36/32",
            },
    },
    {
        # Router2
        "mgnt_ip": "192.168.1.36",
        'if_config': {
            'ge-0/0/1': "72.114.96.2/30",
            'ge-0/0/2': "72.114.96.5/30",
            'ge-0/0/3': "72.114.96.14/30",
            'ge-0/0/4': "72.114.96.17/30",
            'lo0': "72.114.96.37/32",
            }
    },
    {
        # Router3
        "mgnt_ip": "192.168.1.37",
        'if_config': {
            'ge-0/0/1': "72.114.96.9/30",
            'ge-0/0/3': "72.114.96.6/30",
            'lo0': "72.114.96.38/32"
            }
    },
    {
        # Router4
        "mgnt_ip": "192.168.1.38",
        'if_config': {
            'ge-0/0/1': "72.114.96.13/30",
            'ge-0/0/2': "72.114.96.10/30",
			'ge-0/0/4': "72.114.96.33/30",
            'lo0': "72.114.96.39/32"
            }
    },
    {
        # Router5
        "mgnt_ip": "192.168.1.39",
        'if_config': {
            'ge-0/0/1': "72.114.96.18/30",
            'ge-0/0/2': "72.114.96.25/30",
            'ge-0/0/3': "72.114.96.34/30",
            'lo0': "72.114.96.40/32"
            }
    }

]


for dev in devices:
    try:
        with Device(host=dev['mgnt_ip'], user="labuser", password="Labuser") as device:
            device.bind(conf=Config)
            var_dict = {'if_config': dev['if_config']}
            device.conf.load(template_path = 'template.conf', template_vars = var_dict, merge = True)
            success = device.conf.commit()
            print('Success = {0}'.format(success))
    except ConnectError as err:
        print("\nCannot connect to device: {0}".format(err))
    except CommitError as err:
        print("\nCommit error: " + repr(err))
    except Exception as err:
        print(repr(err))
