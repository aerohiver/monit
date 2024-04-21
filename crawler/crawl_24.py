# =====================================================
# 24. 한국데이터산업진흥원
# =====================================================
def crawl_24(driver, aY, aM, aD, bY, bM, bD):

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
    URL = "https://www.kdata.or.kr/kr/board/notice_01/boardList.do"
    driver.get(URL)

    # 게시판에서 최근 게시글 제목/날짜/소스 추출
    articles = driver.find_elements(By.CSS_SELECTOR, 'ul.bbs_list > li:not(.cate)')
    
    start_date = datetime(aY, aM, aD)
    end_date = datetime(bY, bM, bD)
    
    date_details = []
    title_details = []
    sorce_details = []
    
    for article in articles:
        date_str = article.find_element(By.CSS_SELECTOR, 'p.date').text.strip().split('\n')[-1]
        try:
            date = datetime.strptime(date_str, '%Y.%m.%d')
            if start_date <= date <= end_date:
                title = article.find_element(By.CSS_SELECTOR, 'p.tit > a').text.strip().replace("제목\n", "")
                date_details.append(date_str)
                title_details.append(title)
                sorce_details.append("한국데이터산업진흥원")
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
            
    for i in title_details:
        try:
            # WebDriverWait를 사용하여 요소가 로드될 때까지 기다리고, 요소가 발견되면 클릭
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{i}')]")) )
            element.click()
    
            time.sleep(1)
            deep_url_list.append(driver.current_url)
            
            # 클릭 후 추가 작업이 필요한 경우 여기에 코드 추가
            elements = driver.find_elements(By.CLASS_NAME, 'text_box')  # cont 작동확인
            for element in elements:
                child_text = []
                child_elements = element.find_elements(By.XPATH, ".//*")
                for child in child_elements:
                    child_text.append(child.text)  # 하위 요소의 텍스트 출력
                deep_text_list.append(trim_text_to_4097_tokens("\n".join(child_text)))
                        
            driver.get(URL)
            time.sleep(1)
        
        finally:
            print('wow')

    # 데이터프레임으로 정리 
    df = pd.DataFrame({'날짜': date_details, '사이트': sorce_details, '제목': title_details, 
                       # "요약" :summary_list, 
                       '링크': deep_url_list, '원문':deep_text_list})

    # 결과값 반환
    return df