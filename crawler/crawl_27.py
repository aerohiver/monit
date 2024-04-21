# =====================================================
# 27. 한국지능정보사회진흥원 NIA
# =====================================================
def crawl_27(driver, aY, aM, aD, bY, bM, bD):

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
    URL = "https://www.nia.or.kr/site/nia_kor/ex/bbs/List.do?cbIdx=99835"
    driver.get(URL)

    # 게시판에서 최근 게시글 제목/날짜/소스 추출
    articles = driver.find_element(By.CLASS_NAME, 'board_type01').find_elements(By.CSS_SELECTOR, 'ul > li')

    start_date = datetime(aY, aM, aD)
    end_date = datetime(bY, bM, bD)

    date_details = []
    date_datetime_details = []
    title_details = []
    sorce_details = []
    article_details = []
        
    # 전체 아티클 목록 찾기
    for article in articles:
        date_str = article.find_element(By.CLASS_NAME, 'src').text.strip().split(' ')[0]
        try:
            date = datetime.strptime(date_str, '%Y.%m.%d')
            title = article.find_element(By.CSS_SELECTOR, "span.subject.searchItem").text.strip()
            # date_details.append(date_str)
            date_datetime_details.append(date)

            # title_details.append(title)
            # sorce_details.append("한국지능정보사회진흥원")
            article_details.append(article)
        except ValueError as e:
            print(f"날짜 변환 오류: {e}, 원본 문자열: '{date_str}'")
            continue

    # 날짜에 들어오는 아티클의 인덱스만 찾기
    indices = [i for i, date in enumerate(date_datetime_details) if start_date <= date <= end_date]

    
    # 아티클 목록 찾기 (전체 다시 돌린다)
    for article in articles:
        date_str = article.find_element(By.CLASS_NAME, 'src').text.strip().split(' ')[0]
        try:
            date = datetime.strptime(date_str, '%Y.%m.%d')
            if start_date <= date <= end_date:
                title = article.find_element(By.CSS_SELECTOR, "span.subject.searchItem").text.strip()
                date_details.append(date_str)
                title_details.append(title)
                sorce_details.append("한국지능정보사회진흥원")
                # article_details.append(article)
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
        if num in indices:
            try:
                element = driver.find_element(By.CLASS_NAME, 'board_type01').find_elements(By.CSS_SELECTOR, 'ul > li')[num].find_elements(By.CSS_SELECTOR, "span")[0]
                driver.execute_script("arguments[0].click();", element)
                deep_url_list.append(driver.current_url)

                full_content = []            
                for j in driver.find_element(By.CLASS_NAME, 'con_area').find_elements(By.CSS_SELECTOR, "p, div"):
                    full_content.append(j.text.strip())
                try:
                    for j in driver.find_elements(By.CLASS_NAME, 'file_nm'):
                        full_content.append(j.find_element(By.CSS_SELECTOR, "a").text.strip())
                except:
                    pass
                full_content = "\n".join(full_content)   

            finally:
                print(num, end='\r')

            deep_text_list.append(trim_text_to_4097_tokens(full_content))
            time.sleep(2)
            driver.back()
            time.sleep(2)

            
    # 데이터프레임으로 정리 
    df = pd.DataFrame({'날짜': date_details, '사이트': sorce_details, '제목': title_details, 
                       # "요약" :summary_list, 
                       '링크': deep_url_list, '원문':deep_text_list})

    # 결과값 반환
    return df
