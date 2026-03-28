from config.settings import *

# Android device capabilities
AOS_REAL_CHROME = {
    "platformName":              "Android",
    "appium:automationName":     "UiAutomator2",
    "appium:deviceName":         AOS_DEVICE["real"]["device_name"],
    "appium:udid":               AOS_DEVICE["real"]["udid"],
    "browserName":               "Chrome",
    "appium:noReset":            True,
    "appium:newCommandTimeout":  TIMEOUT["new_command"],
}

AOS_REAL_SAMSUNG = {
    "platformName":                 "Android",
    "appium:automationName":        "UiAutomator2",
    "appium:deviceName":            AOS_DEVICE["real"]["device_name"],
    "appium:udid":                  AOS_DEVICE["real"]["udid"],
    "browserName":                  "Samsung Internet",
    "appium:chromedriverExecutable": CHROMEDRIVER_PATH,
    "appium:noReset":               True,
    "appium:newCommandTimeout":     TIMEOUT["new_command"],
}

AOS_EMULATOR_CHROME = {
    "platformName":              "Android",
    "appium:automationName":     "UiAutomator2",
    "appium:deviceName":         AOS_DEVICE["emulator"]["device_name"],
    "appium:udid":               AOS_DEVICE["emulator"]["udid"],
    "browserName":               "Chrome",
    "appium:noReset":            True,
    "appium:newCommandTimeout":  TIMEOUT["new_command"],
}


# iOS device capabilities 
IOS_REAL_SAFARI = {
    "platformName":             "iOS",
    "appium:automationName":    "XCUITest",
    "appium:deviceName":        IOS_DEVICE["real"]["device_name"],
    "appium:udid":              IOS_DEVICE["real"]["udid"],
    "appium:platformVersion":   IOS_DEVICE["real"]["platform_version"],
    "browserName":              "Safari",
    "appium:noReset":           True,
    "appium:newCommandTimeout": TIMEOUT["new_command"],
    "appium:startIWDP":         True,
}

IOS_REAL_CHROME = {
    "platformName":             "iOS",
    "appium:automationName":    "XCUITest",
    "appium:deviceName":        IOS_DEVICE["real"]["device_name"],
    "appium:udid":              IOS_DEVICE["real"]["udid"],
    "appium:platformVersion":   IOS_DEVICE["real"]["platform_version"],
    "browserName":              "Chrome",
    "appium:noReset":           True,
    "appium:newCommandTimeout": TIMEOUT["new_command"],
    "appium:startIWDP":         True,
}

IOS_SIMULATOR_SAFARI = {
    "platformName":             "iOS",
    "appium:automationName":    "XCUITest",
    "appium:deviceName":        IOS_DEVICE["simulator"]["device_name"],
    "appium:platformVersion":   IOS_DEVICE["simulator"]["platform_version"],
    "browserName":              "Safari",
    "appium:noReset":           True,
    "appium:newCommandTimeout": TIMEOUT["new_command"],
}

IOS_SIMULATOR_CHROME = {
    "platformName":             "iOS",
    "appium:automationName":    "XCUITest",
    "appium:deviceName":        IOS_DEVICE["simulator"]["device_name"],
    "appium:platformVersion":   IOS_DEVICE["simulator"]["platform_version"],
    "browserName":              "Chrome",
    "appium:noReset":           True,
    "appium:newCommandTimeout": TIMEOUT["new_command"],
}