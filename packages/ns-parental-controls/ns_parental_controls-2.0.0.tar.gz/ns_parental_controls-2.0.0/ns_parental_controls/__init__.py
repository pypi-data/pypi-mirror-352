import datetime
import time
from urllib.parse import urlencode

import requests

from ns_parental_controls.const import CLIENT_ID, REDIRECT_URI, SCOPE, AUTHORIZE_URL, SESSION_TOKEN_URL, TOKEN_URL, \
    GRANT_TYPE, MY_ACCOUNT_ENDPOINT, USER_AGENT, MOBILE_APP_PKG, OS_NAME, OS_VERSION, DEVICE_MODEL, MOBILE_APP_VERSION, \
    MOBILE_APP_BUILD, ENDPOINTS, BASE_URL, DAYS_OF_WEEK
from ns_parental_controls.helpers import random_string, hash_it, parse_response_url


class ParentalControl:
    '''
    This will allow you to enable/disable a device.
    Its based on the mobile app api so you have to do some wonky
    copy/paste to make it work, but its not too bad for techies.
    '''

    def __init__(self, save_state_callback=None, load_state_callback=None, callback_kwargs={}, debug=False):
        '''
        If you need to re-hydrate this object, you can use
        the save/load callbacks to restore the state.

        :param save_state_callback (Callable[[dict], None]):
        :param load_state_callback (Callable[[dict], dict]):
        :param callback_kwargs (dict): Some additional metadata that will be included in the save/load callbacks. Can be useful for storing a userId or something.
        '''
        self.debug = debug

        self.save_state_callback = save_state_callback
        self.load_state_callback = load_state_callback
        self.callback_kwargs = callback_kwargs

        self.verification_code = None
        self.session_token = None
        self.access_token = None
        self.access_token_expires_timestamp = 0
        self.id_token = None
        self.account_id = None

        self._load()

        if self.verification_code is None:
            self.verification_code = random_string()
            self._save(verification_code=self.verification_code)

    def get_auth_url(self):
        '''
        The user should go to this link.
        Assuming you are already logged in, you will
        see a "select this account" button.
        Right-click on that button and copy the link.
        You will paste that link into process_auth_link() method.
        :return str: The login url that you can click on.
        '''
        # Generate a temporary code that will be used to verify
        # the server response.
        # That way we know the response actually came from the server.

        # build the login url
        self.print('get_auth_url verification_code=', self.verification_code)
        params = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "session_token_code",
            "scope": SCOPE,
            "session_token_code_challenge": hash_it(self.verification_code),
            "session_token_code_challenge_method": "S256",
            "state": self.verification_code,
            "theme": "login_form"
        }
        login_url = AUTHORIZE_URL.format(urlencode(params)).replace("%2B", "+")
        return login_url

    def process_auth_link(self, link: str):
        '''
        This will use the link to get the needed tokens.
        :param link (str): string like 'npf54789befb391a838://auth#session_token_code=really-long-string&state=verification-code-here&session_state=abc123-'
        :return None:
        '''
        # pull out the important info from the link
        data = parse_response_url(link)
        data['client_id'] = CLIENT_ID
        data['session_token_code_verifier'] = self.verification_code

        # trade our session_token_code for a session_token
        resp = requests.post(
            url=SESSION_TOKEN_URL,
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'User-Agent': 'NASDKAPI; Android',
            }
        )
        if not resp.ok:
            self.print('process_auth_link failed', resp.text)

        self.session_token = resp.json().get('session_token')
        self._save(session_token=self.session_token)

        self.get_new_access_token()

    def get_new_access_token(self):
        '''
        Used to get either a new access token or to refresh an expired access token.
        This is called by the needed methods, you should not need to call directly.
        :return str: The access token used for HTTP requests
        '''
        # trade the session_token for an access_token
        self.print('get_new_access_token')
        resp = requests.post(
            url=TOKEN_URL,
            json={
                "client_id": CLIENT_ID,
                "grant_type": GRANT_TYPE,
                "session_token": self.session_token
            }
        )
        if not resp.ok:
            self.print(resp.text)
        else:
            # reset the verification code, so that we use a new code next time we get a session_token
            self.verification_code = random_string()

        self.access_token = resp.json()['access_token']
        self.id_token = resp.json()['id_token']
        self.access_token_expires_timestamp = (
                time.time() + resp.json()['expires_in']
        )

        self._save(
            access_token=self.access_token,
            id_token=self.id_token,
            access_token_expires_timestamp=self.access_token_expires_timestamp,
            verification_code=self.verification_code
        )

        return self.access_token

    def _save(self, **kwargs):
        '''
        Makes a call to the save_state_callback.
        You can use this to sore the state somewhere (in your database/filesystem presumably)
        :param kwargs (dict): kwargs you want to save, these will be appended/overwritten to the existing state
        :return None:
        '''
        self.print('nspc save(', kwargs)
        if self.save_state_callback:
            d = self._load().copy()
            d.update(kwargs)

            if 'verification_code' not in d:
                d['verification_code'] = self.verification_code

            self.save_state_callback(**d)

    def _load(self):
        '''
        Used to load the state from your database.
        :return dict: The state that is saved in the db, also initializes internal values like self.access_token
        '''
        if self.load_state_callback:
            data = self.load_state_callback(**self.callback_kwargs)

            code = data.get('verification_code', None)
            if code:
                self.verification_code = code

            self.session_token = data.get('session_token', None)

            self.access_token = data.get('access_token', None)
            self.id_token = data.get('id_token', None)
            self.access_token_expires_timestamp = data.get('access_token_expires_timestamp', 0)

            self.account_id = data.get('account_id', None)

            self.print('nspc load return', data)
            return data

        return {'verification_code': self.verification_code}

    def get_access_token(self):
        '''
        Use this to access the current token.
        This will handle any logic for refreshing a token that is expired.
        :return str:
        '''
        if not self.session_token:
            return None

        if self.access_token and self.access_token_expires_timestamp < time.time():
            # the access token exist and is not expired
            return self.access_token
        else:
            # the access token is missing or expired
            time.sleep(1)
            return self.get_new_access_token()

    def get_account_id(self):
        '''
        Get the user's account_id.
        This is needed for some other HTTP requests.
        You shouldnt have to call this directly.
        :return str:
        '''
        self.print('get_account_id')
        if self.account_id is None:
            resp = self.send_request(
                method='GET',
                url=MY_ACCOUNT_ENDPOINT,
            )
            self.print('get_account_id resp=', resp.text)
            self.print(resp.json())
            self.account_id = resp.json()['id']
            self._save(account_id=self.account_id)

        return self.account_id

    def send_request(self, method='GET', *a, **k):
        '''
        All API requests go through here.
        It handles authentication and headers and such.

        Note that if the request fails because of an invalid_token,
        this will refresh the token and try again 3 times.

        :param method (str): 'get' 'post', etc
        :param a:
        :param k:
        :return requests.Response: The response object from the server.
        '''
        self.print('send_request(method=', method, a, k)
        i = 3
        while i > 0:
            i -= 1
            resp = requests.request(
                method=method,
                headers={
                    "Authorization": 'Bearer ' + self.get_access_token(),
                    "User-Agent": USER_AGENT,
                    "X-Moon-App-Id": MOBILE_APP_PKG,
                    "X-Moon-Os": OS_NAME,
                    "X-Moon-Os-Version": OS_VERSION,
                    "X-Moon-Model": DEVICE_MODEL,
                    "X-Moon-TimeZone": str(time.timezone),
                    "X-Moon-Os-Language": 'en-US',
                    "X-Moon-App-Language": 'en-US',
                    "X-Moon-App-Display-Version": MOBILE_APP_VERSION,
                    "X-Moon-App-Internal-Version": MOBILE_APP_BUILD,
                },
                *a, **k
            )
            if not resp.ok:
                self.print('resp failed', resp.text)
                if 'invalid_token' in resp.text:
                    self.get_new_access_token()
            else:
                self.print('send_request resp=', resp.text)
                return resp
            time.sleep(1)
        return resp

    def get_device_id(self, device_label: str):
        if self._load():
            data = self._load()
            device_id = data.get('device_map', {}).get(device_label, None)
            if device_id:
                return device_id
            else:
                device = self.get_device(device_label)
                return device['deviceId']

    def get_device(self, device_label: str):
        '''
        Get a list of device dicts.
        :param device_label (str): The name of the device
        :return dict | None: The device dict (should prob make this a proper object)
        '''
        self.print('get_device(', device_label)
        # get the list of devices

        resp = self.send_request(
            'GET',
            url=ENDPOINTS['get_account_devices']['url'].format(
                BASE_URL=BASE_URL,
                ACCOUNT_ID=self.get_account_id()
            )

        )
        if not resp.ok:
            self.print('error getting device', resp.text)

        device_map = {}
        return_device = None

        for dev in resp.json().get('items', []):
            self.print('dev=', dev)

            # save the device_label/deviceId for later
            device_map[dev.get('label', '')] = dev.get('deviceId', None)

            if dev.get('label', '') == device_label:
                self.print('found device=', dev)
                return_device = dev
        else:
            self.print('device not found')
            for dev in resp.json().get('items', []):
                self.print('dev=', dev)

        self._save(device_map=device_map)
        return return_device

    def get_parental_control_settings(self, device):
        data = self._load()

        resp = self.send_request(
            'GET',
            url=BASE_URL + '/devices/' + device.get('deviceId') + '/parental_control_setting',

        )
        if resp.ok:
            self.print('get_parental_control_settings success')
            self.print(resp.json())

            self._save(**{
                device['deviceId']: resp.json()
            })
            data.update({
                device['deviceId']: resp.json()
            })
            self.print('get settings resp.json=', resp.json)
        else:
            self.print('get settings failed', resp.text)

        return data[device['deviceId']]

    def get_allowed_playtime_today(self, device_label: str):
        device = self.get_device(device_label)
        settings = self.get_parental_control_settings(device)
        settings["playTimerRegulations"]["timerMode"] = 'EACH_DAY_OF_THE_WEEK'
        day_of_week_regs = settings["playTimerRegulations"]["eachDayOfTheWeekRegulations"]
        current_day = DAYS_OF_WEEK[datetime.datetime.now().weekday()]
        ret = day_of_week_regs[current_day]["timeToPlayInOneDay"]["limitTime"]
        self.print(device_label, 'is allwoed to play for', ret, 'minutes today')
        return ret
    def lock_device(self, device_label: str, lock: bool):
        '''
        This is shown as "Disable Alarms for Today" in the app.
        :param device_label (str): The name of the device
        :param lock (bool): True means disable the device, False means enable the device.
        :return None:
        '''
        deviceId = self.get_device_id(device_label)

        resp = self.send_request(
            "POST",
            url=BASE_URL + '/devices/' + deviceId + '/alarm_setting_state',
            json={'status': 'TO_VISIBLE' if lock else 'TO_INVISIBLE'}
        )
        if resp.ok:
            pass
        else:
            self.print(resp.reason)
            self.print(resp.headers)
            self.print(resp.content)

        self.print('lock_device', lock, 'ok=', resp.ok)

    def set_playtime_minutes_for_today(self, device_label: str, minutes: int):
        # minutes in increments of 15 max 360(6hours)
        self.print('set_playtime_minutes_for_today minutes=', minutes)
        device = self.get_device(device_label)

        settings = self.get_parental_control_settings(device)

        # set the mode to daily, so we can set limits for just today
        settings["playTimerRegulations"]["timerMode"] = 'EACH_DAY_OF_THE_WEEK'
        day_of_week_regs = settings["playTimerRegulations"]["eachDayOfTheWeekRegulations"]
        current_day = DAYS_OF_WEEK[datetime.datetime.now().weekday()]
        day_of_week_regs[current_day]["timeToPlayInOneDay"]["enabled"] = True
        day_of_week_regs[current_day]["timeToPlayInOneDay"]["limitTime"] = minutes

        # not sure why we need this but we do
        if "bedtimeStartingTime" in settings["playTimerRegulations"]:
            if settings["playTimerRegulations"].get("bedtimeStartingTime", {}).get("hour",
                                                                                   0) == 0:
                settings["playTimerRegulations"].pop("bedtimeStartingTime")

        self.set_settings(device, settings)

    def add_playtime_minutes_for_today(self, device_label: str, minutes_to_add: int):
        # need to add time to the existing time
        device = self.get_device(device_label)
        settings = self.get_parental_control_settings(device)

        current_day = DAYS_OF_WEEK[datetime.datetime.now().weekday()]
        day_of_week_regs = settings["playTimerRegulations"]["eachDayOfTheWeekRegulations"]
        old_limit = day_of_week_regs[current_day]["timeToPlayInOneDay"]["limitTime"]
        old_played_time = self.get_today_playtime_minutes(device_label)
        old_minutes = max(old_limit, old_played_time)
        new_minutes = old_minutes + minutes_to_add
        self.print('old_minutes=', old_minutes)
        self.print('new_minutes=', new_minutes)
        day_of_week_regs[current_day]["timeToPlayInOneDay"]["limitTime"] = new_minutes

        # not sure why we need this but we do
        if "bedtimeStartingTime" in settings["playTimerRegulations"]:
            if settings["playTimerRegulations"].get("bedtimeStartingTime", {}).get("hour",
                                                                                   0) == 0:
                settings["playTimerRegulations"].pop("bedtimeStartingTime")

        self.set_settings(device, settings)

    def get_today_playtime_minutes(self, device_label: str):
        # get the amount of time the user has played on this device today
        dev_id = self.get_device_id(device_label)
        resp = self.send_request(
            method='GET',
            url=f'{BASE_URL}/devices/{dev_id}/daily_summaries'
        )
        self.print('get_today_playtime resp.json=', resp.json())

        today_date_iso = datetime.date.today().isoformat()
        for day_snapshot in resp.json().get('items', []):
            if day_snapshot.get('date', None) == today_date_iso:
                playtime_seconds = day_snapshot.get('playingTime', 0)
                playtime_minutes = playtime_seconds / 60
                self.print(device_label, 'played for', playtime_minutes, 'minutes')
                return int(playtime_minutes)

        return 0

    def set_settings(self, device: dict, settings: dict):
        # we need to send a subset of the settings
        data = {
            "unlockCode": settings["unlockCode"],
            "functionalRestrictionLevel": settings["functionalRestrictionLevel"],
            "customSettings": settings["customSettings"],
            "playTimerRegulations": settings["playTimerRegulations"]
        }
        self.print('set_settings', device['deviceId'], data)
        resp = self.send_request(
            method='POST',
            url="{BASE_URL}/devices/{DEVICE_ID}/parental_control_setting".format(
                BASE_URL=BASE_URL,
                DEVICE_ID=device['deviceId']
            ),
            json=data,
        )

        return resp

    def print(self, *a, **k):
        if self.debug:
            print(*a, **k)
