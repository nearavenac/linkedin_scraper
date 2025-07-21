import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .objects import Experience, Education, Scraper, Interest, Accomplishment, Contact
from linkedin_scraper import selectors, utils

class Person(Scraper):

    __TOP_CARD = "main"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
        self,
        linkedin_url=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=True,
        extra_info=False,
    ):
        self.linkedin_url = linkedin_url
        self.name = ""
        self.about = []
        self.experiences = []
        self.educations = []
        self.interests = []
        self.accomplishments = []
        self.skills = []
        self.also_viewed_urls = []
        self.contacts = []
        self.extra_info = extra_info
        
        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()
        
        self.driver = driver

        if get and driver.current_url != linkedin_url:
            driver.get(linkedin_url)

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_skill(self, skill):
        self.skills.append(skill)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop("driver", None)
        # Serializar listas de objetos personalizados
        for key in ["experiences", "educations", "interests", "accomplishments", "contacts"]:
            val = d.get(key)
            if isinstance(val, list):
                d[key] = [
                    obj.to_dict() if hasattr(obj, "to_dict") else obj.__dict__
                    for obj in val
                ]
        return d

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element(By.CLASS_NAME, class_name)
            div.find_element(By.TAG_NAME, "button").click()
        except Exception as e:
            pass

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element(By.CLASS_NAME,"pv-top-card-profile-picture").find_element(By.TAG_NAME,"img").get_attribute("title")
        except:
            return False

    def get_experiences(self):
        url = os.path.join(self.linkedin_url, "details/experience")
        scraped_experience_keys = set()

        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        
        for position in main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item"):
            position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
            
            elements = position.find_elements(By.XPATH, "*")
            if len(elements) < 2:
                continue
                
            company_logo_elem = elements[0]
            position_details = elements[1]

            try:
                company_linkedin_url = company_logo_elem.find_element(By.XPATH,"*").get_attribute("href")
                if not company_linkedin_url:
                    continue
            except NoSuchElementException:
                continue

            position_details_list = position_details.find_elements(By.XPATH,"*")
            position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
            position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
            
            if not position_summary_details:
                continue
                
            outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

            if len(outer_positions) == 4:
                position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                location = outer_positions[3].find_element(By.TAG_NAME,"span").text
            elif len(outer_positions) == 3:
                if "·" in outer_positions[2].text:
                    position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                    company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                    location = ""
                else:
                    position_title = ""
                    company = outer_positions[0].find_element(By.TAG_NAME,"span").text
                    work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    location = outer_positions[2].find_element(By.TAG_NAME,"span").text
            else:
                position_title = ""
                company = outer_positions[0].find_element(By.TAG_NAME,"span").text if outer_positions else ""
                work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text if len(outer_positions) > 1 else ""
                location = ""

            if work_times:
                parts = work_times.split("·")
                times = parts[0].strip() if parts else ""
                duration = parts[1].strip() if len(parts) > 1 else None
            else:
                times = ""
                duration = None

            from_date = " ".join(times.split(" ")[:2]) if times else ""
            to_date = " ".join(times.split(" ")[3:]) if times and len(times.split(" ")) > 3 else ""
            
            if position_summary_text:
                try:
                    ul = position_summary_text.find_element(By.TAG_NAME, "ul")
                    inner_positions = ul.find_elements(By.TAG_NAME, "li")
                    # Solo considerar inner_positions si alguno tiene al menos un .t-bold (cargo)
                    filtered_inner_positions = []
                    for li in inner_positions:
                        # Aquí puede variar el selector según el HTML de tu LinkedIn
                        if li.find_elements(By.CSS_SELECTOR, ".t-bold"):
                            filtered_inner_positions.append(li)
                    inner_positions = filtered_inner_positions
                except Exception:
                    inner_positions = []
            else:
                inner_positions = []

            if inner_positions:
                for pos in inner_positions:
                    try:
                        anchors = pos.find_elements(By.TAG_NAME, "a")
                        if not anchors:
                            print("No anchor found in this li, skipping...")
                            continue
                        anchor = anchors[0]

                        # Title
                        try:
                            position_title = anchor.find_element(By.CSS_SELECTOR, ".t-bold span[aria-hidden='true']").text
                        except Exception:
                            position_title = ""
                        # Work times & duration
                        try:
                            date_block = anchor.find_element(By.CSS_SELECTOR, ".pvs-entity__caption-wrapper[aria-hidden='true']").text
                            date_parts = date_block.split("·")
                            date_range = date_parts[0].strip()
                            duration = date_parts[1].strip() if len(date_parts) > 1 else None
                            if '-' in date_range:
                                from_str, to_str = [d.strip() for d in date_range.split('-')]
                            else:
                                from_str, to_str = date_range.strip(), None
                            from_date = utils.parse_date(from_str)
                            to_date = utils.parse_date(to_str) if to_str else None
                        except Exception:
                            from_date, to_date, duration = None, None, None
                        
                        location = ""
                        description = anchor.text

                        experience_key = (position_title, company, from_str, to_str)
                        if experience_key not in scraped_experience_keys:
                            experience = Experience(
                                position_title=position_title,
                                from_date=from_date,
                                to_date=to_date,
                                duration=duration,
                                location=location,
                                description=description,
                                institution_name=company,
                                linkedin_url=company_linkedin_url
                            )
                            self.add_experience(experience)
                            scraped_experience_keys.add(experience_key)
                    except Exception as e:
                        print(f"Error processing position: {e}")
                        continue
            else:
                description = position_summary_text.text if position_summary_text else ""

                experience_key = (position_title, company, from_date, to_date)
                if experience_key not in scraped_experience_keys:
                    experience = Experience(
                        position_title=position_title,
                        from_date=utils.parse_date(from_date),
                        to_date=utils.parse_date(to_date),
                        duration=duration,
                        location=location,
                        description=description,
                        institution_name=company,
                        linkedin_url=company_linkedin_url
                    )
                    self.add_experience(experience)
                    scraped_experience_keys.add(experience_key)

    def get_educations(self):
        url = os.path.join(self.linkedin_url, "details/education")
        scraped_education_keys = set()

        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        
        for position in main_list.find_elements(By.CLASS_NAME,"pvs-list__paged-list-item"):
            try:
                position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                
                elements = position.find_elements(By.XPATH,"*")
                if len(elements) < 2:
                    continue
                    
                institution_logo_elem = elements[0]
                position_details = elements[1]

                try:
                    institution_linkedin_url = institution_logo_elem.find_element(By.XPATH,"*").get_attribute("href")
                except NoSuchElementException:
                    institution_linkedin_url = None

                position_details_list = position_details.find_elements(By.XPATH,"*")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                
                if not position_summary_details:
                    continue
                    
                outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

                institution_name = outer_positions[0].find_element(By.TAG_NAME,"span").text if outer_positions else ""
                degree = outer_positions[1].find_element(By.TAG_NAME,"span").text if len(outer_positions) > 1 else None

                from_date, to_date = None, None
                
                if len(outer_positions) > 2:
                    try:
                        times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                        if times and "-" in times:
                            parts = [p.strip() for p in times.split("-")]
                            from_date = parts[0]
                            to_date = parts[1]
                    except (NoSuchElementException, ValueError):
                        pass

                description = position_details_list[1].text if len(position_details_list) > 1 else ""

                education_key = (institution_name, degree, from_date, to_date)
                if education_key not in scraped_education_keys:
                    education = Education(
                        from_date=utils.parse_date(from_date),
                        to_date=utils.parse_date(to_date),
                        description=description,
                        degree=degree,
                        institution_name=institution_name,
                        linkedin_url=institution_linkedin_url
                    )
                    self.add_education(education)
                    scraped_education_keys.add(education_key)
                    
            except (NoSuchElementException, IndexError) as e:
                continue

    def get_name_and_location(self):
        top_panel = self.driver.find_element(By.XPATH, "//*[@class='mt2 relative']")
        self.name = top_panel.find_element(By.TAG_NAME, "h1").text
        self.location = top_panel.find_element(By.XPATH, "//*[@class='text-body-small inline t-black--light break-words']").text

    def get_about(self):
        try:
            about = self.driver.find_element(By.ID,"about").find_element(By.XPATH,"..").find_element(By.CLASS_NAME,"display-flex").text
        except NoSuchElementException :
            about=None
        self.about = about

    def get_interests(self):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            interestContainer = self.driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']"
            )
            for interestElement in interestContainer.find_elements(By.XPATH,
                "//*[@class='pv-interest-entity pv-profile-section__card-item ember-view']"
            ):
                interest = Interest(
                    interestElement.find_element(By.TAG_NAME, "h3").text.strip()
                )
                self.add_interest(interest)
        except:
            pass

    def get_accomplishments(self):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            acc = self.driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']"
            )
            for block in acc.find_elements(By.XPATH,
                "//div[@class='pv-accomplishments-block__content break-words']"
            ):
                category = block.find_element(By.TAG_NAME, "h3")
                for title in block.find_element(By.TAG_NAME,
                    "ul"
                ).find_elements(By.TAG_NAME, "li"):
                    accomplishment = Accomplishment(category.text, title.text)
                    self.add_accomplishment(accomplishment)
        except:
            pass

    def get_contacts(self):
        try:
            self.driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mn-connections"))
            )
            connections = self.driver.find_element(By.CLASS_NAME, "mn-connections")
            if connections is not None:
                for conn in connections.find_elements(By.CLASS_NAME, "mn-connection-card"):
                    anchor = conn.find_element(By.CLASS_NAME, "mn-connection-card__link")
                    url = anchor.get_attribute("href")
                    name = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME, "mn-connection-card__name").text.strip()
                    occupation = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME, "mn-connection-card__occupation").text.strip()

                    contact = Contact(name=name, occupation=occupation, url=url)
                    self.add_contact(contact)
        except:
            connections = None

    def get_skills(self):
        scraped_skill_keys = set()
        url = os.path.join(self.linkedin_url, "details/skills")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        
        for skill_item in main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item"):
            try:
                entity = skill_item.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                span = entity.find_element(By.CSS_SELECTOR, ".t-bold span[aria-hidden='true']")
                skill_name = span.text.strip()
                if skill_name and skill_name not in scraped_skill_keys:
                    self.add_skill(skill_name)
                    scraped_skill_keys.add(skill_name)
            except Exception as e:
                continue

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        duration = None

        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        self.focus()
        self.wait(1)

        self.get_name_and_location()

        self.open_to_work = self.is_open_to_work()

        self.get_about()
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        self.get_experiences()

        self.get_educations()

        self.get_skills()

        if self.extra_info:
            self.get_contacts()

        if self.extra_info:
            if driver.current_url != self.linkedin_url:
                driver.get(self.linkedin_url)
            self.get_interests()

        if self.extra_info:
            self.get_accomplishments()

        if close_on_complete:
            driver.quit()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "<Person {name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}>".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
        )
