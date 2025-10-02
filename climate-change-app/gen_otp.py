"""
Author: Tom
"""

import pyotp

if __name__ == '__main__':
    otp_key = input('Enter OTP key: ')
    totp = pyotp.TOTP(otp_key)
    print(totp.now())
