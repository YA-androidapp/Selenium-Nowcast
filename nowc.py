from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import os
import pyderman
import sys


lat = 35.681236
lon = 139.76712

try:
  if len(sys.argv) == 3:
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
except:
  pass


image_ext = 'png'

info = pyderman.install(browser=pyderman.firefox, chmod=True, overwrite=False, return_info=True)
# info = pyderman.install(browser=pyderman.chrome, chmod=True, overwrite=False, return_info=True)

# {'path': 'C:\\path\\to\\geckodriver_0.29.1.exe', 'version': '0.29.1', 'driver': 'geckodriver'}
print('info: %s %s' % (info, type(info)))

if isinstance(info, str):
  driver_name = (os.path.basename(info)).split('_')[0]
  driver_path = info
if isinstance(info, dict):
  driver_name = info['driver']
  driver_path = info['path']

if driver_name == 'geckodriver':
  driver = webdriver.Firefox(executable_path=driver_path)
elif driver_name == 'chromedriver':
  driver = webdriver.Chrome(driver_path)

driver.set_window_size(1200, 900)
wait = WebDriverWait(driver, 10)

driver.get('https://www.jma.go.jp/bosai/nowc/#zoom:14/lat:%f/lon:%f/colordepth:deep/elements:hrpns' % (lat, lon))

# 広告を非表示
ad_block_button = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'jmatile-clear-ad')))
ad_block_button.click()

for i in range(13):
  # 予報の日時を取得
  map_title = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'jmatile-map-title-validtime')))
  image_title = map_title.text # driver.find_element_by_class_name('jmatile-map-title-validtime').text
  filename = '%f_%f_%s.%s' % (lat, lon, image_title, image_ext)

  # スクリーンショットを保存
  # page_image = driver.get_screenshot_as_file(image_title+'.png')
  map_image = driver.find_element_by_class_name('jmatile-map').screenshot_as_png
  #TODO: 地図画像自体への操作
  with open(filename, 'wb') as f:
    f.write(map_image)

  # 次へ
  try:
    driver.find_elements_by_css_selector('[id^=jmatile_time_next_')[0].click()
  except:
    pass

driver.close()
