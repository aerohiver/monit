# =====================================================
# 11. 공정거래위원회
# =====================================================
def crawl_11(driver, aY, aM, aD, bY, bM, bD):

    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    import time
    from datetime import datetime

    import pandas as pd

    # 게시판 방문
    URL = "https://www.ftc.go.kr/www/cop/bbs/selectBoardList.do?key=13&bbsId=BBSMSTR_000000002424&bbsTyCode=BBST01"
    driver.get(URL)
    
    # 게시판에서 최근 게시글 제목/날짜/소스 추출
    articles = driver.find_elements(By.CSS_SELECTOR, 'tbody')[1].find_elements(By.CSS_SELECTOR, 'tr')

    start_date = datetime(aY, aM, aD)
    end_date = datetime(bY, bM, bD)

    date_details = []
    title_details = []
    sorce_details = []
    article_details = []

    # 아티클 목록 찾기
    for article in articles:
        date_str = article.find_elements(By.CSS_SELECTOR, 'td')[3].text.replace("-",".")  
        try:
            date = datetime.strptime(date_str, '%Y.%m.%d')
            if start_date <= date <= end_date:
                title = article.find_elements(By.CSS_SELECTOR, "td")[1].text.strip()
                date_details.append(date_str)
                title_details.append(title)
                sorce_details.append("공정거래위원회")
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
            driver.find_elements(By.CSS_SELECTOR, 'tbody')[1].find_elements(By.CSS_SELECTOR, 'tr')[num].find_elements(By.CSS_SELECTOR, "td")[1].click()
            deep_url_list.append(driver.current_url)
            full_content = []            
            for j in driver.find_elements(By.CLASS_NAME, 'bbs_content'):
                full_content.append(j.text.strip().replace("&nbsp;", ""))
            try:
                full_content.append(driver.find_elements(By.CSS_SELECTOR, 'tbody > tr:nth-child(3) > td:nth-child(2)').text.strip())
            except:
                pass
            full_content = "\n".join(full_content)   
            
        finally:
            print('wow')

        deep_text_list.append(trim_text_to_4097_tokens(full_content))
        driver.get(URL)
        time.sleep(2)


    # 데이터프레임으로 정리 
    df = pd.DataFrame({'날짜': date_details, '사이트': sorce_details, '제목': title_details, 
                       # "요약" :summary_list, 
                       '링크': deep_url_list, '원문':deep_text_list})

    # 결과값 반환
    return df