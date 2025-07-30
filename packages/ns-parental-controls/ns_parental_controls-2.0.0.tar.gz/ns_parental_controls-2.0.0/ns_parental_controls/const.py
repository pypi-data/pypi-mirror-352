MOBILE_APP_PKG = "com.nintendo.znma"
MOBILE_APP_VERSION = "2.0.0"
MOBILE_APP_BUILD = "999"
OS_NAME = "ANDROID"
OS_VERSION = "33"
OS_STR = f"{OS_NAME} {OS_VERSION}"
DEVICE_MODEL = "Pixel 4 XL"
BASE_URL = "https://api-lp1.pctl.srv.nintendo.net/moon/v1"
USER_AGENT = f"moon_ANDROID/{MOBILE_APP_VERSION} ({MOBILE_APP_PKG}; build:{MOBILE_APP_BUILD}; {OS_STR})"
DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

ENDPOINTS = {
    "get_account_details": {
        "url": "{BASE_URL}/users/{ACCOUNT_ID}",
        "method": "GET"
    },
    "get_account_devices": {
        "url": "{BASE_URL}/users/{ACCOUNT_ID}/devices?filter.device.activated.$eq=true",
        "method": "GET"
    },
    "get_account_device": {
        "url": "{BASE_URL}/users/{ACCOUNT_ID}/devices/{DEVICE_ID}",
        "method": "GET"
    },
    "get_device_daily_summaries": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/daily_summaries",
        "method": "GET"
    },
    "get_device_monthly_summaries": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/monthly_summaries",
        "method": "GET"
    },
    "get_device_parental_control_setting": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/parental_control_setting",
        "method": "GET"
    },
    "update_device_parental_control_setting": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/parental_control_setting",
        "method": "POST"
    },
    "update_device_whitelisted_applications": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/parental_control_setting/whitelisted_applications",
        "method": "POST"
    },
    "get_device_parental_control_setting_state": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/parental_control_setting_state",
        "method": "GET"
    },
    "update_device_alarm_setting_state": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/alarm_setting_state",
        "method": "POST"
    },
    "get_device_alarm_setting_state": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/alarm_setting_state",
        "method": "POST"
    },
    "get_device_monthly_summary": {
        "url": "{BASE_URL}/devices/{DEVICE_ID}/monthly_summaries/{YEAR}-{MONTH}",
        "method": "GET"
    }
}
ACCOUNT_API_BASE = "https://api.accounts.nintendo.com/2.0.0"
MY_ACCOUNT_ENDPOINT = f"{ACCOUNT_API_BASE}/users/me"
TOKEN_URL = "https://accounts.nintendo.com/connect/1.0.0/api/token"
CLIENT_ID = "54789befb391a838"  # original
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token"
CLIENT_ID = "54789befb391a838"
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token"

REDIRECT_URI = f"npf{CLIENT_ID}://auth"
SCOPE = "openid+user+user.mii+moonUser:administration+moonDevice:create+moonOwnedDevice:administration+moonParentalControlSetting+moonParentalControlSetting:update+moonParentalControlSettingState+moonPairingState+moonSmartDevice:administration+moonDailySummary+moonMonthlySummary"

AUTHORIZE_URL = "https://accounts.nintendo.com/connect/1.0.0/authorize?{}"
SESSION_TOKEN_URL = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
TOKEN_URL = "https://accounts.nintendo.com/connect/1.0.0/api/token"

ACCOUNT_API_BASE = "https://api.accounts.nintendo.com/2.0.0"
MY_ACCOUNT_ENDPOINT = f"{ACCOUNT_API_BASE}/users/me"
