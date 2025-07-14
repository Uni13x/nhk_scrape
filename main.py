import time
import chromedriver_autoinstaller
import pandas as pd
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def main():

  parser = argparse.ArgumentParser(description="NHKニュース検索スクレイピング (Selenium + BeautifulSoup)")
  parser.add_argument("--keyword", required=True, help="検索ワード（例: 地震, AI, 経済 など）")
  parser.add_argument("--max_articles", type=int, default=5, help="取得する記事の最大件数 (デフォルト: 5)")
  parser.add_argument("--output", default="output.csv", help="出力CSVファイル名 (デフォルト: output.csv)")
  args = parser.parse_args()

  keyword = args.keyword
  max_articles = args.max_articles
  output_file = args.output

  options = Options()
  options.add_argument("--incognito")
  options.add_argument("--log-level=3") 

  chromedriver_autoinstaller.install()

  driver = webdriver.Chrome(options=options)
  driver.set_page_load_timeout(60)
  driver.set_script_timeout(20)
  driver.maximize_window()

  search_url = f"https://www3.nhk.or.jp/news/nsearch/?qt={keyword}"

  try:
    driver.get(search_url)
    time.sleep(3)
  except TimeoutException as e:
    print(f"接続がタイムアウト: {e}")
    return

  data = []

  while True:
    soup = BeautifulSoup(driver.page_source, "lxml")
    articles = soup.select("ul.search--list > li")

    for article in articles:
      if len(data) >= max_articles:
        break

      title_tag = article.select_one("em.title")
      url_tag = article.select_one("a")
      
      if title_tag and url_tag:
        title = title_tag.text.strip()
        url = url_tag["href"]
        
        if url.startswith("/"):
          url = f"https://www3.nhk.or.jp/{url}"

        data.append({
          "title": title,
          "url": url
        })

    if len(data) >= max_articles:
      break
        

    try:
      next_btn = driver.find_element(By.CSS_SELECTOR, "li.nav--pager-next > a")
      driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_btn)
      time.sleep(3)
      next_btn.click()
      time.sleep(2)

    except (NoSuchElementException, ElementClickInterceptedException):
      print("次のボタンが見つからないため、終了")
      break

  driver.quit()

  df = pd.DataFrame(data)
  df.to_csv(output_file, index=False, encoding="UTF-8")
  print(f"{len(data)} 件の記事を `{output_file}` に保存しました。")

if __name__ == "__main__":
  main()
