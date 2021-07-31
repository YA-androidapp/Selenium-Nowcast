from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import math
import os
import sys
import time


# pixel (60pixel = 500m)
area_size = 60  # 経緯度を中心に1km四方
browser_name = 'firefox'
image_ext = 'png'
lat = 35.681236
lon = 139.76712
nowcast_url = 'https://www.jma.go.jp/bosai/nowc/#zoom:14/lat:%f/lon:%f/colordepth:deep/elements:hrpns'

try:
    if len(sys.argv) == 3:
        lat = float(sys.argv[1])
        lon = float(sys.argv[2])
except:
    pass

notes = {
    '80': (180, 0, 104, 255),
    '50': (255, 40, 0, 255),
    '30': (255, 153, 0, 255),
    '20': (255, 245, 0, 255),
    '10': (0, 65, 255, 255),
    '5': (33, 140, 255, 255),
    '1': (160, 210, 255, 255),
    '0': (242, 242, 255, 255)
}


def driver_preparation(browser_name, debug_mode):
    if debug_mode:
        if browser_name == 'chrome':
            info = pyderman.install(browser=pyderman.chrome, chmod=True, overwrite=False, return_info=True)
        else:
            info = pyderman.install(browser=pyderman.firefox, chmod=True, overwrite=False, return_info=True)

        if isinstance(info, dict):
            driver_name = info['driver']
            driver_path = info['path']
        elif isinstance(info, str):
            driver_name = (os.path.basename(info)).split('_')[0]
            driver_path = info

        if driver_name == 'chromedriver':
            driver = webdriver.Chrome(driver_path)
        elif driver_name == 'geckodriver':
            driver = webdriver.Firefox(executable_path=driver_path)
    else:
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

    return driver


def clear_ad(wait):
    ad_block_button = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'jmatile-clear-ad')))
    ad_block_button.click()


def get_image_filename(wait):
    map_title = wait.until(
        expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'jmatile-map-title-validtime')))
    image_title = map_title.text
    imagename = datetime.strptime(image_title, '%Y年%m月%d日%H時%M分').strftime('%Y%m%d%H%M00')
    filename = '%f_%f_%s.%s' % (lat, lon, image_title, image_ext)
    return (imagename, filename)


def get_key(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return '-1'


def get_forecasts(imagename, filename, map_image, debug_mode):
    im = Image.open(BytesIO(map_image))
    center_x, center_y = math.ceil(im.size[0] / 2) - 1, math.ceil(im.size[1] / 2) - 1
    max_rain = '-1'
    for y in range(center_y - area_size, center_y + area_size):
        for x in range(center_x - area_size, center_x + area_size):
            rgba = im.getpixel((x, y))
            rain = get_key(notes, rgba)
            if int(max_rain) < int(rain):
                max_rain = rain

    if debug_mode:
        draw = ImageDraw.Draw(im)
        draw.rectangle((center_x - area_size, center_y - area_size, center_x + area_size, center_y + area_size),
                       outline=(255, 0, 0))
        im.save(filename)

    return {imagename: max_rain.replace('-1', '-')}


def access_nowcast(driver, lat, lon, page, debug_mode):
    driver.set_window_size(600, 600)
    driver.get(nowcast_url % (lat, lon))
    wait = WebDriverWait(driver, 15)
    time.sleep(1)
    try:
        clear_ad(wait)
    except:
        pass

    forecasts = {}
    for i in range(page):
        time.sleep(1)

        # 予報の日時を取得
        imagename, filename = get_image_filename(wait)

        # page_image = driver.get_screenshot_as_file(image_title+'.png')
        map_image = driver.find_element_by_class_name('jmatile-map').screenshot_as_png
        forecast = get_forecasts(imagename, filename, map_image, debug_mode)
        forecasts.update(forecast)

        # 次へ
        try:
            driver.find_elements_by_css_selector('[id^=jmatile_time_next_')[0].click()
        except:
            pass

    return forecasts


def main(lat, lon, page, debug_mode):
    driver = driver_preparation(browser_name, debug_mode)
    try:
        result = {'location': {'lat': lat, 'lon': lon}}
        forecasts = access_nowcast(driver, lat, lon, page, debug_mode)
        result.update({'forecasts': forecasts})
        return result
    finally:
        driver.close()


if __name__ == '__main__':
    import pyderman
    result = main(lat, lon, 13, True)
    print('result', result)
