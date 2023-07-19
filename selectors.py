class selector:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    DRIVER = r'C:\Driver\Chromedriver.exe'
    INDICATOR_LINKS = "//div[@class='col-md-3 col-sm-4 col-xs-12']//ul[@class='list-unstyled']//li[@class='list-group-item']//a"
    NEWS = "//ul[@class='list-group']//li"
    HEADER = "//ul[@class='list-group']//li//b"
    LI_RIBBON = "//div[@class='pagetabs']//ul[@id='pagemenutabs']//li"
    TH_RIBBON = "//thead//th"
    TR_VALUE = "//tbody//tr"
    TITLE = "//span[@class='title-indicator']"
    MARKET = "//div[@class='container']//li[@class='dropdown  ']//li[@class='nav-item']//a"
    PAGE_HEIGHT = "return document.body.scrollHeight"
    SCROLL = "window.scrollBy(0, document.body.scrollHeight)"
    
    
