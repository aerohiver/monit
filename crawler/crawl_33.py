# =====================================================
# 34. 금융결제원
# =====================================================
def crawl_33(driver, aY, aM, aD, bY, bM, bD):

    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys

    import time
    from datetime import datetime

    import pandas as pd

    # 게시판 방문
    URL = "https://www.kftc.or.kr/kftc/pr/EgovPrList.do"
    driver.get(URL)
    element = driver.find_element(By.CLASS_NAME, "navm1").find_element(By.CLASS_NAME, "tit")
    element.click()

    # 게시판에서 최근 게시글 제목/날짜/소스 추출
    articles = driver.find_element(By.CSS_SELECTOR, 'tbody').find_elements(By.CSS_SELECTOR, 'tr')

    start_date = datetime(aY, aM, aD)
    end_date = datetime(bY, bM, bD)

    date_details = []
    title_details = []
    sorce_details = []
    article_details = []
  
    # 아티클 목록 찾기
    for article in articles:
        date_str = article.find_elements(By.CSS_SELECTOR, 'td')[3].text.strip().replace('-', '.')
        try:
            date = datetime.strptime(date_str, '%Y.%m.%d')
            if start_date <= date <= end_date:
                title = article.find_elements(By.CSS_SELECTOR, "td")[1].text.strip()
                date_details.append(date_str)
                title_details.append(title)
                sorce_details.append("금융결제원")
                article_details.append(article)
        except ValueError as e:
            print(f"날짜 변환 오류: {e}, 원본 문자열: '{date_str}'")
        continue

    # 세부 페이지 방문하여, 원문주소/원문 추출
    deep_url_list = []
    deep_text_list = []

    def trim_text_to_4097_tokens(text):
        if len(text) <= 4097:
            return text
        else:
            return text[:4097]

    for num, i in enumerate(article_details):
        try:
            element = driver.find_element(By.CSS_SELECTOR, 'tbody').find_elements(By.CSS_SELECTOR, 'tr')[num].find_element(By.CLASS_NAME, "txt_left").find_element(By.CSS_SELECTOR, "a")
            driver.execute_script("arguments[0].click();", element)
            deep_url_list.append(driver.current_url)
            
            full_content = []            
            full_content.append(driver.find_element(By.CSS_SELECTOR, 'tbody').find_elements(By.CSS_SELECTOR, "tr")[0].text.strip())
            try:
                for j in driver.find_element(By.CSS_SELECTOR, 'tbody').find_elements(By.CSS_SELECTOR, "tr")[1].find_elements(By.CSS_SELECTOR, "a"):
                    full_content.append(j.text.strip())
            except:
                pass
            full_content = "\n".join(full_content)   

        except Exception as e:
            print("제목 두줄 → 클릭 오류 발생")
            full_content= ""
            deep_url_list.append(URL)
            continue
            
        finally:
            print('wow')
            deep_text_list.append(trim_text_to_4097_tokens(full_content))
        
        time.sleep(1)
        driver.get(URL)
        element = driver.find_element(By.CLASS_NAME, "navm1").find_element(By.CLASS_NAME, "tit")
        element.click()
        time.sleep(1)

    # 데이터프레임으로 정리 
    df = pd.DataFrame({'날짜': date_details, '사이트': sorce_details, '제목': title_details, 
                    # "요약" :summary_list, 
                    '링크': deep_url_list, '원문':deep_text_list})

    # 결과값 반환
    return df