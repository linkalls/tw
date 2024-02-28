import PySimpleGUI as sg
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import os
import time
import threading
import json
import atexit
import chromedriver_binary_sync  # 追加

# ChromeDriverのパスを指定
# chrome_driver_path = os.path.join('driver', 'chromedriver.exe')  # コメントアウト

# 'driver'ディレクトリが存在しない場合は作成
if not os.path.exists('driver'):
    os.makedirs('driver')

# chromedriver-binary-syncを使用してChromeDriverをダウンロード
chromedriver_binary_sync.download(download_dir='driver')

# ChromeDriverのパスを取得
chrome_driver_path = os.path.join('driver', 'chromedriver.exe')

# 設定ファイルのパス
config_file = 'config.json'

# Chromeを起動するための関数
def launch_chrome():
  chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
  command = [chrome_path, '--headless']  # commandを定義
  chrome_process = subprocess.Popen(command)
  atexit.register(chrome_process.kill)  # スクリプトが終了するときにChromeを停止する
  return chrome_process

  



# 既に起動しているChromeブラウザを操作するためのwebdriverを作成する関数
def create_driver():
  options = Options()
  options.add_argument("--window-size=1980x1080")
  options.add_argument("--user-data-dir=C:\\Temp_Chrome")
  options.add_argument("--headless")  # ヘッドレスモードを有効にする
  driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
  atexit.register(driver.quit)  # スクリプトが終了するときにChromeDriverを停止する
  return driver

def load_config():
  default_config = {
    'urls_filename': 'image_urls.txt',
    'save_folder': os.getcwd(),  # 画像を保存するデフォルトフォルダ
  }
  if os.path.exists(config_file):
    with open(config_file, 'r') as file:
      config = json.load(file)
      # 'urls_filename' キーがない場合はデフォルト値を設定する
      if 'urls_filename' not in config:
        config['urls_filename'] = default_config['urls_filename']
      # 'save_folder' キーがない場合はデフォルト値を設定する
      if 'save_folder' not in config:
        config['save_folder'] = default_config['save_folder']
      return config
  else:
    return default_config

def save_config(config):
  with open(config_file, 'w') as file:
    json.dump(config, file, indent=4)  # 読みやすいようにインデントを追加

def take_screenshot(driver, file_path):
  driver.save_screenshot(file_path)

# ChromeブラウザとChromeDriverのプロセスを参照するグローバル変数
chrome_process = None
driver = None

def collect_image_urls(urls_filename, window):
  global chrome_process
  global driver

  chrome_process = launch_chrome()  # Chromeを起動
  window.write_event_value('-THREAD-', 'chromeを起動しています...')

  driver = create_driver()  # 既に起動しているChromeブラウザを操作するwebdriverを作成

  # ブックマークページに移動

  driver.get('https://twitter.com/i/bookmarks')
  window.write_event_value('-THREAD-', 'ブックマークページに移動しています...')
  time.sleep(4)  # ページの読み込みを待つ

  # 画像URLを収集
  scroll_retry_count = 0
  scroll_retry_limit = 2  # スクロールの再試行回数の上限

   # 既存のURLを読み込む
  existing_urls = set()
  if os.path.exists(urls_filename):
    with open(urls_filename, 'r') as file:
      existing_urls = set(line.strip() for line in file)

  saved_urls = set()
  try:
    while True:
      # スクロール前の位置を取得
      previous_position = driver.execute_script("return window.pageYOffset;")
      # ページを少しずつスクロール
      driver.execute_script('window.scrollBy(0, 400);')
      window.write_event_value('-THREAD-', 'ページをスクロールしています...')
      time.sleep(0.01)  # 0.01秒待機してゆっくりスクロール
      take_screenshot(driver, 'scrolling_screenshot.png') # スクリーンショットを取得

      # スクロール後の位置を取得
      new_position = driver.execute_script("return window.pageYOffset;")
      if new_position == previous_position:
        # 位置が変わっていない場合
        scroll_retry_count += 1
        if scroll_retry_count >= scroll_retry_limit:
          # 再試行回数が上限に達した場合
          window.write_event_value('-THREAD-', 'ページの最下部に到達しました。スクリプトを終了します。')
          break
        else:
          # 再試行回数が上限に達していない場合
          window.write_event_value('-THREAD-', f'ページの最下部に到達したかもしれません。再起動を試みます（{scroll_retry_count}回目）。')
          time.sleep(5)  # 再試行前に少し待機する
      else:
        # 位置が変わっている場合
        scroll_retry_count = 0  # 再試行カウンターをリセット

      # 画像要素を取得
      images = driver.find_elements(By.CSS_SELECTOR, 'img.css-9pa8cd')
      for image in images:
        try:
          image_url = image.get_attribute('src')
          if image_url.startswith('https://pbs.twimg.com/media'):
            base_url, query_string = image_url.split('?', 1)
            query_params = query_string.split('&')
            new_query_params = []
            for param in query_params:
              key, value = param.split('=')
              if key == 'name':
                if value == 'small':
                  new_query_params.append(key + '=orig')
                elif value == '360x360':
                  new_query_params.append(key + '=orig')
                elif value == '900x900':
                  new_query_params.append(key + '=orig')
                elif value == 'medium':
                  new_query_params.append(key + '=orig')
                elif value == '240x240':
                  new_query_params.append(key + '=orig')
                elif value == 'large':
                  new_query_params.append(key + '=orig')
                else:
                  new_query_params.append(param)
              else:
                new_query_params.append(param)
            high_quality_image_url = base_url + '?' + '&'.join(new_query_params)
            if high_quality_image_url not in saved_urls and (not existing_urls or high_quality_image_url not in existing_urls):
              with open(urls_filename, 'a') as file:
                file.write(high_quality_image_url + '\n')
              window.write_event_value('-THREAD-', f'画像URLを保存しました: {high_quality_image_url}')
              saved_urls.add(high_quality_image_url)
            else:
              window.write_event_value('-THREAD-', f'重複したURLをスキップしました: {high_quality_image_url}')
        except StaleElementReferenceException:
          # 要素が古くなった場合は、次の要素に進む
          continue
  except TimeoutException:
    window.write_event_value('-THREAD-', 'ページの読み込み中にタイムアウトしました。')
  except NoSuchElementException:
    window.write_event_value('-THREAD-', '要素が見つかりませんでした。')
  finally:
    driver.quit()
    chrome_process.kill()  # Chromeを終了する
    window.write_event_value('-COLLECT_DONE-', '')  # collect_image_urls 関数が完了したことを示すイベントを発火
  return list(saved_urls)


# 画像URLから画像をダウンロードして保存する関数
def download_images(image_urls, directory=None, window=None):
  # ディレクトリが指定されていない場合は、スクリプトのあるフォルダを使用
  if not directory:
    directory = os.getcwd()

  if not os.path.exists(directory):
    os.makedirs(directory)

  downloaded_urls = set()  # ダウンロード済みのURLを追跡するためのセット
  for index, url in enumerate(image_urls, start=1):  # 連番は1から始める
    if url in downloaded_urls:
      if window:
        window.write_event_value('-THREAD-', f'重複した画像です: {url}')
      else:
        print(f'重複した画像です: {url}')
      continue  # 重複しているURLはスキップ

    # URLからフォーマットを抽出
    format = 'jpg'  # フォーマットが指定されていない場合はデフォルトでjpg
    if 'format=' in url:
      format = url.split('format=')[1].split('&')[0]

    # 正しい拡張子でファイル名を生成
    filename = f'{index}.{format}'

    try:
      response = requests.get(url, stream=True)
      if response.status_code == 200:
        with open(os.path.join(directory, filename), 'wb') as file:
          for chunk in response.iter_content(1024):
            file.write(chunk)
        downloaded_urls.add(url)  # URLをダウンロード済みのセットに追加
        if window:
          window.write_event_value('-THREAD-', f'{filename}をダウンロードしました。')
    except Exception as e:
      if window:
        window.write_event_value('-THREAD-', f'エラーが発生しました: {e}')

  # すべての画像のダウンロードが完了したことを示すメッセージを出力
  if window:
    window.write_event_value('-THREAD-', 'すべての画像のダウンロードが完了しました。')
  else:
    print('すべての画像のダウンロードが完了しました。')

def main():
    config = load_config()

    layout = [
        [sg.Text('画像URLを保存するファイル名'), sg.Input(default_text=config['urls_filename'], key='-URLS_FILENAME-')],
        [sg.Text('画像を保存するフォルダ'), sg.Input(default_text=config['save_folder'], key='-SAVE_FOLDER-'), sg.FolderBrowse()],
        [sg.Output(size=(100, 20))],
        [sg.Button('画像URLを収集', key='-COLLECT-'), sg.Button('画像をダウンロード', key='-DOWNLOAD-'), sg.Button('一括処理', key='-BATCH-'), sg.Button('設定を保存', key='-SAVE-'), sg.Button('終了', key='-EXIT-')]
    ]

    window = sg.Window('Twitter Image Downloader', layout)

    while True:
        event, values = window.read(timeout=100)  # timeoutを設定してGUIが応答を続けるようにする
        if event in (sg.WINDOW_CLOSED, '-EXIT-'):
          def quit_driver_and_chrome():
            if driver is not None:
              driver.quit()  # ChromeDriverを終了する
            if chrome_process is not None:
              chrome_process.kill()  # Chromeを終了する
          threading.Thread(target=quit_driver_and_chrome, daemon=True).start()
          break
        elif event == '-THREAD-':
            print(values[event])  # スレッドからのメッセージを出力
        # '-COLLECT-'イベントの処理
        elif event == '-COLLECT-':
          threading.Thread(target=collect_image_urls, args=(values['-URLS_FILENAME-'], window), daemon=True).start()

        # '-DOWNLOAD-'イベントの処理
        elif event == '-DOWNLOAD-':
          if os.path.exists(values['-URLS_FILENAME-']):
            with open(values['-URLS_FILENAME-'], 'r') as file:
              image_urls = [line.strip() for line in file]
            threading.Thread(target=download_images, args=(image_urls, values['-SAVE_FOLDER-'], window), daemon=True).start()
          else:
            print(f"ファイルが存在しません: {values['-URLS_FILENAME-']}")

        # '-BATCH-'イベントの処理
        elif event == '-BATCH-':
          collect_thread = threading.Thread(target=collect_image_urls, args=(values['-URLS_FILENAME-'], window), daemon=True)
          collect_thread.start()
        elif event == '-COLLECT_DONE-':  # collect_image_urls 関数が完了したときの処理
          if os.path.exists(values['-URLS_FILENAME-']):
            with open(values['-URLS_FILENAME-'], 'r') as file:
              image_urls = [line.strip() for line in file]
            threading.Thread(target=download_images, args=(image_urls, values['-SAVE_FOLDER-'], window), daemon=True).start()
          else:
            print(f"ファイルが存在しません: {values['-URLS_FILENAME-']}")
        elif event == '-SAVE-':
              config['urls_filename'] = values['-URLS_FILENAME-']
              config['save_folder'] = values['-SAVE_FOLDER-']
              save_config(config)
              print("設定を保存しました。")

    window.close()

if __name__ == '__main__':
          main()    
