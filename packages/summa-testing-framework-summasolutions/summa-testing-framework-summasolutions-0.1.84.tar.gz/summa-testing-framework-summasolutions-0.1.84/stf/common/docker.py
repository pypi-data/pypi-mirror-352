DOCKER_MODE_NORMAL = 'normal'
DOCKER_MODE_DEBUG = 'debug'

DOCKER_CHROME_IMAGE_NORMAL = 'selenium/node-chrome:3.141.59-20210929'
DOCKER_CHROME_IMAGE_DEBUG = 'selenium/node-chrome-debug:3.141.59-20210929'

DOCKER_FIREFOX_IMAGE_NORMAL = 'selenium/node-firefox:3.141.59-20210929'
DOCKER_FIREFOX_IMAGE_DEBUG = 'selenium/node-firefox-debug:3.141.59-20210929'
 

def get_chrome_image(mode):
    if mode == DOCKER_MODE_DEBUG:
        return DOCKER_CHROME_IMAGE_DEBUG

    return DOCKER_CHROME_IMAGE_NORMAL


def get_firefox_image(mode):
    if mode == DOCKER_MODE_DEBUG:
        return DOCKER_FIREFOX_IMAGE_DEBUG

    return DOCKER_FIREFOX_IMAGE_NORMAL


def get_base_config(mode):
    config = {
        'volumes': [
            '/dev/shm:/dev/shm'
        ],
        'depends_on': [
            'selenium-hub'
        ],
        'environment': [
            'HUB_HOST=selenium-hub',
            'HUB_PORT=4444',
        ],
        'networks': [
            'selenium-grid'
        ]
    }

    if mode == DOCKER_MODE_DEBUG:
        config['environment'].extend([
            'VNC_NO_PASSWORD=1',
            'NODE_DEBUG=true'
        ])

    return config


def get_chrome_config(mode):
    config = get_base_config(mode)
    config['image'] = get_chrome_image(mode)

    if mode == DOCKER_MODE_DEBUG:
        config['ports'] = ['5901:5900']

    return config


def get_firefox_config(mode):
    config = get_base_config(mode)
    config['image'] = get_firefox_image(mode)

    if mode == DOCKER_MODE_DEBUG:
        config['ports'] = ['5902:5900']

    return config