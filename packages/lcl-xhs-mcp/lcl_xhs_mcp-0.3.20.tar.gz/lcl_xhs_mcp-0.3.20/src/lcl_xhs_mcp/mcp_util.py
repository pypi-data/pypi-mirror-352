# This program will automate Xiaohongshu login and save/load cookies.
# It will require manual intervention for the verification code step.
import os
import sys
# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory to sys.path
sys.path.append(os.path.dirname(current_dir))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from .image_generate import image_generation_gemini, download_and_save_images

import time
import json
import os
import logging
import asyncio



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='./app.log',
    filemode='a',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)
class AuthManager:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        if not os.path.exists('./cookies'):
            os.makedirs('./cookies')
        self.COOKIE_FILE = f'./cookies/{phone_number}.json'
        # Use a headless browser if you don't need to see the browser window
        options = webdriver.ChromeOptions()
        # For headless mode
        # options.add_argument('--headless')
        # options.add_argument("--disable-gpu")

        # options.add_argument('--no-sandbox')
        # chrome_options.add_argument('window-size=1920x1080')#页面部分内容是动态加载得时候，无头模式默认size为0x0，需要设置最大化窗口并设置windowssize，不然会出现显示不全的问题
        # chrome_options.add_argument('--start-maximized')    #页面部分内容是动态加载得时候，无头模式默认size为0x0，需要设置最大化窗口并设置windowssize，不然会出现显示不全的问题
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.113 Safari/537.36"
        # options.add_argument(f"user-agent={user_agent}")        
        # options.add_argument("--disable-blink-features=AutomationControlled")  # 隐藏自动化特征
        # options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options) # Or use Firefox, Edge, etc.
        self.driver.maximize_window()

        self.has_cookie = self.load_cookies()
        logger.info(f"cookie文件路径: {os.path.abspath(self.COOKIE_FILE)}")
        # time.sleep(5)

    def __del__(self):
        # 在这里执行清理操作
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")


    def save_cookies(self):
        """Saves cookies to a file."""
        cookies = self.driver.get_cookies()
        # 如果文件存在则先清空文件内容
        if os.path.exists(self.COOKIE_FILE):
            open(self.COOKIE_FILE, 'w').close()
        # 重新写入cookies数据
        with open(self.COOKIE_FILE, 'w') as f:
            json.dump(cookies, f)
        logger.info(f"Cookies saved to {self.COOKIE_FILE}")
    
    def load_cookies(self):
        """Loads cookies from a file and adds them to the browser."""
        if not os.path.exists(self.COOKIE_FILE):
            logger.info('Cookie文件不存在，返回False')
            return False
        
        try:
            logger.info(f'从{self.COOKIE_FILE}加载cookies')
            with open(self.COOKIE_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if not cookies or len(cookies) == 0:
                logger.info('cookies为空或不存在，返回False')
                return False
            self.driver.get("https://creator.xiaohongshu.com")
            for cookie in cookies:
                # Selenium requires domain to be set for adding cookies
                # Need to handle potential domain issues depending on the site
                # For simplicity, we'll add them after navigating to the site
                self.driver.add_cookie(cookie)
                
            logger.info(f'成功加载 {len(cookies)} 个cookies')
            return True
            
        except Exception as e:
            logger.error(f'加载cookies出错: {str(e)}')
            return False

    async def create_note(self, title, content, image_urls):
        # 会在成功登录的情况调用该函数。
        """创建小红书笔记并上传图片."""
        
        try:
            # 导航到发布笔记的页面
            self.driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
            time.sleep(3)
            if self.driver.current_url != "https://creator.xiaohongshu.com/publish/publish?from=menu":
                return "登录失败"

            tabs = self.driver.find_elements(By.CSS_SELECTOR, ".creator-tab")
            if len(tabs) > 1:
                tabs[2].click()
            time.sleep(1)
            logger.info("点击了上传图文按钮")
        except Exception as e:
            logger.error(f"点击上传图文按钮出错: {str(e)}")
            return f"创建笔记失败: {str(e)}"

        # 生成图片，保存在本地
        if len(image_urls) == 0:
            logger.info("未提供图片URL，开始自动生成图片")
            image_urls = image_generation_gemini(title)
            logger.info(f"生成图片地址为: {image_urls}")
        else:
            image_urls = await download_and_save_images(image_urls)
        try:
            file_input_selector = '.upload-input'
            file_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, file_input_selector))
            )
            logger.info("找到文件上传输入框")

            # 将图片文件路径发送给输入框
            # Selenium会自动处理多个文件路径，用换行符分隔
            image_paths_string = "\n".join(image_urls) # image_urls 应该是本地文件路径列表
            # # TODO:For test
            # image_paths_string = "C:/Users/1c1/Desktop/公众号推文/创建公众号文章预览图.png"
            file_input.send_keys(image_paths_string)
            logger.info(f"已发送 {len(image_urls)} 个图片文件路径")

            # 填写标题和内容，并点击发布按钮
            # 标题HTML代码:<div class="d-input --color-text-title --color-bg-fill"><!----><input class="d-text" type="text" placeholder="填写标题会有更多赞哦～" value=""><!----><!----><!----></div>
            # 使用XPath定位标题输入框
            title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".d-text"))
            )
            title_input.send_keys(title)
            logger.info(f"已输入标题: {title}")
            # 内容HTML代码:<div class="ql-editor ql-blank" contenteditable="true" aria-owns="quill-mention-list" data-placeholder="输入正文描述，真诚有价值的分享予人温暖"><p><br></p></div>
            content_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor"))
            )
            content_input.send_keys(content)
            logger.info(f"已输入内容: {content}")
            # 发布按钮HTML代码:<span class="d-text --color-static --color-current --size-text-paragraph d-text-nowrap d-text-ellipsis d-text-nowrap" style="text-underline-offset: auto;"><!---->发布<!----><!----><!----></span>
            # 发布button HTML代码：<button data-v-34b0c0bc="" data-v-30daec93="" data-v-0624972c-s="" type="button" class="d-button d-button-large --size-icon-large --size-text-h6 d-button-with-content --color-static bold --color-bg-fill --color-text-paragraph custom-button red publishBtn" data-impression="{&quot;noteTarget&quot;:{&quot;type&quot;:&quot;NoteTarget&quot;,&quot;value&quot;:{&quot;noteEditSource&quot;:1,&quot;noteType&quot;:1}},&quot;event&quot;:{&quot;type&quot;:&quot;Event&quot;,&quot;value&quot;:{&quot;targetType&quot;:{&quot;type&quot;:&quot;RichTargetType&quot;,&quot;value&quot;:&quot;note_compose_target&quot;},&quot;action&quot;:{&quot;type&quot;:&quot;NormalizedAction&quot;,&quot;value&quot;:&quot;impression&quot;},&quot;pointId&quot;:50979}},&quot;page&quot;:{&quot;type&quot;:&quot;Page&quot;,&quot;value&quot;:{&quot;pageInstance&quot;:{&quot;type&quot;:&quot;PageInstance&quot;,&quot;value&quot;:&quot;creator_service_platform&quot;}}}}"><div class="d-button-content"><!----><span class="d-text --color-static --color-current --size-text-paragraph d-text-nowrap d-text-ellipsis d-text-nowrap" style="text-underline-offset: auto;"><!---->发布<!----><!----><!----></span><!----></div></button>
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".publishBtn"))
            )
            # 等待图片上传完毕
            time.sleep(3)
            publish_button.click()
            time.sleep(2)
            logger.info("点击了发布按钮")

            logger.info("笔记创建流程已执行图片上传步骤")
            return "成功发布到小红书上" # 或者根据实际情况返回发布结果

        except Exception as e:
            logger.error(f"创建笔记出错: {str(e)}")
            return f"发送小红书失败: {str(e)}"

        

    def login_with_verification_code(self, verification_code):
        """Automates the login process."""
        self.driver.get("https://creator.xiaohongshu.com/login")
        self.load_cookies()
        self.driver.refresh()
        time.sleep(3)
        # 尝试加载Cookie来快速登录，如果不成功，重新进行手机验证码登录流程
        if self.has_cookie:
            logger.info("Attempted login with saved cookies.")
            if self.driver.current_url != "https://creator.xiaohongshu.com/login":
                print("使用cookies登录成功")
                return "登录成功"
            else:
                # Continue with manual login steps if cookie login fails
                self.driver.delete_all_cookies()
                logger.info("Saved cookies did not result in login. Proceeding with manual login.")
                # return None
        else:
            logger.info("No saved cookies found. Proceeding with manual login.")

        self.driver.get("https://creator.xiaohongshu.com/login")

        # 等待页面加载完成    
        time.sleep(5)
        try:
            phone_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='手机号']")))
            phone_input.clear()
            phone_input.send_keys(self.phone_number)
        except:
            logger.info("Phone number input not found.")
            return "登录失败，网页可能发生变动，请联系维护人员"

        code_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='验证码']")))
        code_input.clear()
        code_input.send_keys(verification_code)

        # 点击登录按钮
        login_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".beer-login-btn")))
        login_button.click()

        # 等待登录成功,获取token
        time.sleep(3)
        # 保存cookies
        self.save_cookies()
        return "登录成功"
    

    def login_without_verification_code(self):
        """Automates the login process."""
        self.driver.get("https://creator.xiaohongshu.com/login")
        self.load_cookies()
        self.driver.refresh()
        time.sleep(3)
        # 尝试加载Cookie来快速登录，如果不成功，重新进行手机验证码登录流程
        if self.has_cookie:
            logger.info("Attempted login with saved cookies.")
            if self.driver.current_url != "https://creator.xiaohongshu.com/login":
                print("使用cookies登录成功")
                return "登录成功"
            else:
                # Continue with manual login steps if cookie login fails
                self.driver.delete_all_cookies()
                logger.info("Saved cookies did not result in login. Proceeding with manual login.")
                # return None
        else:
            logger.info("No saved cookies found. Proceeding with manual login.")

        self.driver.get("https://creator.xiaohongshu.com/login")

        # 等待页面加载完成    
        time.sleep(5)
        try:
            phone_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='手机号']")))
            phone_input.clear()
            phone_input.send_keys(self.phone_number)
        except:
            logger.info("Phone number input not found.")
            return "登录失败，网页可能发生变动，请联系维护人员"
        # <span class="login-btn" data-v-a93a7d02="">登录</span>
        try:
            send_code_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".css-uyobdj")))
            send_code_btn.click()
        except:
            # 尝试其他可能的选择器
            try:
                send_code_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".css-1vfl29")))
                send_code_btn.click()
            except:
                try:
                    send_code_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'发送验证码')]")))
                    send_code_btn.click()
                except:
                    return "无法找到发送验证码按钮"

        return "发送验证码成功,请提醒用户输入验证码"
        


if __name__ == "__main__":
    # Replace with the phone number you want to use
    your_phone_number = "19921987257"
    
    # IMPORTANT: You will need to manually enter the verification code in the browser window that opens.
    auth = AuthManager(your_phone_number)
    # msg = auth.login_with_verification_code("501807")
    # msg = auth.login_without_verification_code()
    
    async def main():
        msg = await auth.create_note('上海', '测试内容', [])
        
    asyncio.run(main())
    time.sleep(10)