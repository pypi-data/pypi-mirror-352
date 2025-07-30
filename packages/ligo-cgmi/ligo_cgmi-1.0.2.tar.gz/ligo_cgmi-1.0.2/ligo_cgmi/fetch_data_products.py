from ligo.gracedb.rest import GraceDb
import os
import requests


def fetch_event(event, PE_filename='Bilby.posterior_samples.hdf5',
                skymap_filename='bayestar.multiorder.fits',
                save_path='PE', MDC=False):
    '''
    Function to fetch PE and skymaps for an event or superevent
    '''

    if not MDC:
        client = GraceDb(service_url="https://gracedb.ligo.org/api/", fail_if_noauth=True)  # noqa E501
    else:
        client = GraceDb(service_url="https://gracedb-playground.ligo.org/api/", fail_if_noauth=True)  # noqa E501

    # superevents
    if event.startswith('S'):
        response = client.superevent(event)
        group = response.json()['preferred_event_data']['group']  # noqa E501
        # CBC events
        if group == 'CBC':
            mchirp_det = response.json()['preferred_event_data']['extra_attributes']['CoincInspiral']['mchirp']  # noqa E501
        # Burst: cWB-BBH
        elif group == 'Burst':
            mchirp_det = response.json()['preferred_event_data']['extra_attributes']['MultiBurst']['mchirp']  # noqa E501

    # events
    elif event.startswith('G'):
        response = client.event(event)
        group = response.json()['group']  # noqa E501
        # CBC events
        if group == 'CBC':
            mchirp_det = response.json()['extra_attributes']['CoincInspiral']['mchirp']  # noqa E501
        # Burst: cWB-BBH
        elif group == 'Burst':
            mchirp_det = response.json()['extra_attributes']['MultiBurst']['mchirp']  # noqa E501

    else:
        print('Input a GW superevent starting with "S" or an event starting with "G"')  # noqa E501
        return None

    path = f'{save_path}/{event}'
    if not os.path.exists(path):
        os.makedirs(path)

    # only fetch skymap for CBC events
    if group == 'CBC':
        files = [PE_filename, skymap_filename]
    elif group == 'Burst':
        files = [PE_filename]
    for filename in files:
        # check if file already exists
        if not os.path.exists(f'{save_path}/{event}/{filename}'):
            try:
                with open(f'{save_path}/{event}/{filename}', 'wb') as f:
                    read_file = client.files(event, filename)
                    f.write(read_file.read())
            # remove empty file if not found
            except requests.exceptions.HTTPError:
                os.remove(f'{save_path}/{event}/{filename}')

    return mchirp_det, group


if __name__ == "__main__":
    event = 'S230226bm'  # example event
    fetch_event(event, MDC=True)
