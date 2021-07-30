from datetime import datetime
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import math
import os
import pyderman
import sys


area_size = 4 * 60 # pixel (60pixel = 500m)
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
  '80': (180,   0, 104, 255),
  '50': (255,  40,   0, 255),
  '30': (255, 153,   0, 255),
  '20': (255, 245,   0, 255),
  '10': (  0,  65, 255, 255),
  '5' : ( 33, 140, 255, 255),
  '1' : (160, 210, 255, 255),
  '0' : (242, 242, 255, 255)
}

def driver_preparation(browser_name):
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

  return driver

def clear_ad(wait):
  ad_block_button = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'jmatile-clear-ad')))
  ad_block_button.click()

def get_image_filename(wait):
    map_title = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'jmatile-map-title-validtime')))
    image_title = map_title.text
    imagename = datetime.strptime(image_title, '%Y年%m月%d日%H時%M分').strftime('%Y%m%d%H%M00')
    filename = '%f_%f_%s.%s' % (lat, lon, image_title, image_ext)
    return (imagename, filename)

def get_key(d, val):
  keys = [k for k, v in d.items() if v == val]
  if keys:
    return keys[0]
  return '-1'

def get_forecasts(imagename, map_image):
  im = Image.open(BytesIO(map_image))
  # print('im.size', im.size)
  center_x, center_y = math.ceil(im.size[0] / 2) - 1, math.ceil(im.size[1] / 2) - 1
  max_rain = '-1'
  for y in range(center_y - area_size, center_y + area_size):
    for x in range(center_x - area_size, center_x + area_size):
      rgba = im.getpixel((x, y))
      # print('r, g, b, a', rgba)
      rain = get_key(notes, rgba)
      if int(max_rain) < int(rain):
        max_rain = rain
  return {imagename: max_rain.replace('-1', '-')}

def save_image_file(filename, map_image):
    with open(filename, 'wb') as f:
      f.write(map_image)

def access_nowcast(driver, lat, lon):
  driver.set_window_size(1200, 900)
  driver.get(nowcast_url % (lat, lon))
  wait = WebDriverWait(driver, 10)
  clear_ad(wait)

  forecasts = {}
  for i in range(13):
    # 予報の日時を取得
    imagename, filename = get_image_filename(wait)

    # page_image = driver.get_screenshot_as_file(image_title+'.png')
    map_image = driver.find_element_by_class_name('jmatile-map').screenshot_as_png
    forecast = get_forecasts(imagename, map_image)
    forecasts.update(forecast)
    save_image_file(filename, map_image)

    # 次へ
    try:
      driver.find_elements_by_css_selector('[id^=jmatile_time_next_')[0].click()
    except:
      pass

  return forecasts

def main(lat, lon):
  driver = driver_preparation(browser_name)
  try:
    result = {'location': {'lat': lat, 'lon': lon}}
    forecasts = access_nowcast(driver, lat, lon)
    result.update({'forecasts': forecasts})
    return result
  finally:
    driver.close()

if __name__ == '__main__':
    result = main(lat, lon)
    print('result', result)
