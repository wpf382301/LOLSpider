import os
import re
import sqlite3

from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, MoveTargetOutOfBoundsException, \
    WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from MyDB import find_hero_sqlite3, save_to_sqlite3_hero, save_to_sqlite3_skill, save_to_sqlite3_equipment, \
    save_to_sqlite3_skin, find_equipment_sqlite3, save_to_sqlite3_equipment_1, check_db
from MyUI import ProgressBar
from tools import download_img, check_name_valid, make_local_dir


class LOLSpider:
    def __init__(self):
        self.hero_dir = "heroes"
        self.equipment_dir = "equipments"
        self.hero_detail_count = 0
        self.g_count = 0
        self.flag_should_stop = False

    def get_hero(self, browser: WebDriver, wait, cursor, progressbar: ProgressBar):
        try:
            browser.get('http://lol.qq.com/web201310/info-heros.shtml')
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#jSearchHeroDiv")))
            self.g_count = 0
            items = browser.find_elements_by_css_selector("#jSearchHeroDiv > li")
            t_count = 0
            for item in items:
                if self.flag_should_stop:
                    return False
                t_count += 1
                if progressbar:
                    progressbar.step = t_count / len(items) / 2 * progressbar.pbar.maximum()
                print('\n--------------------------%d--------------------------\n' % t_count)
                hero_name = item.find_element_by_css_selector('a').get_attribute('title').replace(' ', '-')
                hero_profile = item.find_element_by_css_selector('img').get_attribute('src')
                hero_url = item.find_element_by_css_selector('a').get_attribute('href')
                print(hero_url)
                print(hero_name)
                hero = {
                    'name': hero_name,
                    'profile': hero_profile
                }

                result = find_hero_sqlite3(cursor, hero_name)
                if not result:
                    handle = browser.current_window_handle
                    js = "window.open(\"" + hero_url + "\")"
                    browser.execute_script(js)
                    self.get_hero_details(browser, wait, cursor, hero, handle)
            return True
        except TimeoutException:
            self.g_count += 1
            if self.g_count < 4:
                print('Open page error, try again...')
                self.get_hero(browser, wait, cursor, progressbar)
            else:
                print('Can not open the page!')
                return False
        except NoSuchWindowException:
            print('Browser has closed')
            return False

    def get_hero_details(self, browser: WebDriver, wait, cursor, hero, handle):
        try:
            handles = browser.window_handles
            for newhandle in handles:
                if newhandle != handle:
                    browser.switch_to.window(newhandle)
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#skinNAV > li"))
                    )
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#DATAtags"))
                    )
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#DATAinfo"))
                    )
                    browser.execute_script("window.scrollTo(0,document.body.scrollHeight/2)")
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#DATAspellsNAV > li"))
                    )
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#DATAspells"))
                    )
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#infospellsTAB"))
                    )
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#infospellsTABclassBlocks"))
                    )
                    self.hero_detail_count = 0
                    skill_buttons = browser.find_elements_by_css_selector("#DATAspellsNAV > li")
                    equipment_buttons = browser.find_elements_by_css_selector("#infospellsTAB > li")
                    html = browser.page_source
                    doc = pq(html)

                    skins = doc("#skinNAV > li").items()
                    skin_dic = {}
                    for t in skins:
                        skin_url = t.find('img').attr('src').replace('small', 'big')
                        skin_name = t.find('a').attr('title')
                        skin_dic[skin_name] = skin_url
                    hero['skins'] = skin_dic

                    tags = doc("#DATAtags > span").items()
                    tag_arr = []
                    for t in tags:
                        tag_arr.append(t.text())
                    hero['tags'] = tag_arr

                    attributes = doc("#DATAinfo > dt").items()
                    attributes_value = doc("#DATAinfo > dd").items()
                    attribute_dic = {}
                    for t in attributes:
                        attribute_name = t.text()
                        attribute_value = next(attributes_value).find('i').attr('title')
                        attribute_dic[attribute_name] = attribute_value
                    hero['attributes'] = attribute_dic

                    skills = doc("#DATAspellsNAV > li").items()
                    skill_urls = []
                    skill_names = []
                    skill_keys = []
                    skill_dess = []
                    skill_dataes = {}
                    for t in skills:
                        skill_urls.append(t.find('img').attr('src'))
                    skill_dic = {}
                    for button in skill_buttons:
                        button.click()
                        html = browser.page_source
                        doc = pq(html)
                        t_skill = next(doc("#DATAspells > div").items())
                        skill_name = t_skill.find('h5').text()
                        skill_key = t_skill.find('em').text().replace('快捷键：', '').replace('被动技能', 'bd').lower()

                        t_skill = next(doc("#DATAspells > p").items())
                        skill_des = t_skill.text()

                        data_uls = doc("#DATAspells > ul").items()
                        try:
                            t_skill = next(data_uls)
                            skill_data = t_skill.find('li').items()
                            skill_data_t = []
                            for _ in skill_data:
                                skill_data_t.append(_.text())
                            skill_dataes[skill_key] = ",".join(skill_data_t)
                        except StopIteration:
                            pass
                        skill_names.append(skill_name)
                        skill_keys.append(skill_key)
                        skill_dess.append(skill_des)
                    for i in range(0, len(skill_urls)):
                        t__ = {
                            skill_keys[i] + '_name': skill_names[i],
                            skill_keys[i] + '_img': skill_urls[i],
                            skill_keys[i] + '_des': skill_dess[i]
                        }
                        if skill_keys[i] in skill_dataes.keys():
                            t__[skill_keys[i] + '_data'] = skill_dataes[skill_keys[i]]
                        skill_dic[skill_keys[i]] = t__
                    hero['skills'] = skill_dic

                    equipment_dic_1 = {}
                    button = equipment_buttons[0]
                    button.click()
                    html = browser.page_source
                    doc = pq(html)
                    equipments = doc("#infospellsTABclassBlocks > dt").items()
                    equipments_url = doc("#infospellsTABclassBlocks > dd").items()
                    if equipments:
                        for equipment in equipments:
                            temp = []
                            for _ in pq(next(equipments_url))('img').items():
                                temp.append(_.attr('data-title'))
                            equipment_dic_1[equipment.text()] = temp
                    hero['equipment_1'] = equipment_dic_1

                    equipment_dic_2 = {}
                    button = equipment_buttons[1]
                    button.click()
                    html = browser.page_source
                    doc = pq(html)
                    equipments = doc("#infospellsTABaramBlocks > dt").items()
                    equipments_url = doc("#infospellsTABaramBlocks > dd").items()
                    if equipments:
                        for equipment in equipments:
                            temp = []
                            for _ in pq(next(equipments_url))('img').items():
                                temp.append(_.attr('data-title'))
                            equipment_dic_2[equipment.text()] = temp
                    hero['equipment_2'] = equipment_dic_2

                    print(hero)
                    self.save_hero(cursor, hero)
                    browser.close()
                    browser.switch_to.window(handle)
        except TimeoutException as e:
            print(e)
            self.hero_detail_count += 1
            if self.hero_detail_count < 4:
                print('Open skin page error, try again...')
                browser.refresh()
                self.get_hero_details(browser, wait, cursor, hero, handle)
            else:
                print("Can not open %s's skin page!" % hero['name'])
                browser.close()
                browser.switch_to.window(handle)
                self.hero_detail_count = 0

    def save_hero(self, cursor, hero):
        save_dir = os.path.join(self.hero_dir, hero['name'])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        profile_dir = os.path.join(save_dir, 'profile')
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        skills_dir = os.path.join(save_dir, 'skills')
        if not os.path.exists(skills_dir):
            os.makedirs(skills_dir)

        skin_dir = os.path.join(save_dir, 'skins')
        if not os.path.exists(skin_dir):
            os.makedirs(skin_dir)

        download_img(hero['profile'], profile_dir, check_name_valid(hero['name']))
        save_to_sqlite3_hero(cursor, hero['name'], hero['tags'], hero['attributes'],
                             make_local_dir(hero['profile'], profile_dir,
                                            check_name_valid(hero['name'])))

        for key in hero['skills'].keys():
            download_img(hero['skills'][key][key + '_img'], skills_dir,
                         check_name_valid(hero['skills'][key][key + '_name']))
        save_to_sqlite3_skill(cursor, hero['name'], hero['skills'], skills_dir)

        save_to_sqlite3_equipment(cursor, 'equipment_1', hero['name'], hero['equipment_1'])

        save_to_sqlite3_equipment(cursor, 'equipment_2', hero['name'], hero['equipment_2'])

        for key in hero['skins'].keys():
            download_img(hero['skins'][key], skin_dir, check_name_valid(key))
            save_to_sqlite3_skin(cursor, hero['name'], hero['skins'][key], skin_dir, key)

    def get_equipment(self, browser: WebDriver, wait, cursor, progressbar: ProgressBar):
        try:
            browser.get('http://lol.qq.com/web201310/info-item.shtml')
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#jSearchItemDiv")))
            self.g_count = 0
            items = browser.find_elements_by_css_selector("#jSearchItemDiv > li")
            t_count = 0
            for item in items:
                if self.flag_should_stop:
                    return False
                t_count += 1
                if progressbar:
                    progressbar.step = (t_count / len(items) + 1) / 2 * progressbar.pbar.maximum()
                print('\n--------------------------%d--------------------------\n' % t_count)
                equipment_id = item.get_attribute('data-title')
                equipment_name = item.text
                equipment_url = item.find_element_by_css_selector('img').get_attribute('src')
                print(equipment_name)
                equipment = {
                    'id': equipment_id,
                    'name': equipment_name,
                    'img': equipment_url
                }
                y = item.location['y']
                result = find_equipment_sqlite3(cursor, equipment_id)
                if not result:
                    t_item = browser.find_element_by_css_selector("#jSearchItemDiv > li:nth-child(%s)" % t_count)
                    try:
                        ActionChains(browser).move_to_element(t_item).perform()
                    except MoveTargetOutOfBoundsException:
                        browser.execute_script("window.scrollTo(0, %s)" % y)
                        ActionChains(browser).move_to_element(t_item).perform()
                    self.get_equipment_details(browser, cursor, equipment)
            return True
        except TimeoutException:
            self.g_count += 1
            if self.g_count < 4:
                print('Open equipment page error, try again...')
                self.get_equipment(browser, wait, cursor, progressbar)
            else:
                print('Can not open the page!')
                return False
        except NoSuchWindowException:
            print('Browser has closed')
            return False

    def get_equipment_details(self, browser: WebDriver, cursor, equipment):
        html = browser.page_source
        doc = pq(html)
        cost = doc("#itemFromTop > div.item-title")
        t_stats_1 = {
            "cost": cost("p>span").text()
        }
        t_desc = str(doc("#itemFromTop > div.item-desc"))
        t_del = {
            "<a .*?>": "</a>",
            "<font.*?>": "</font>",
            "<u>": "</u>",
            "<i>": "</i>",
            "<scalehealth>": "</scalehealth>",
            "<scalelevel>": "</scalelevel>"
        }
        for _ in t_del.keys():
            t_desc = re.compile(_).sub("", t_desc)
            t_desc = t_desc.replace(t_del[_], "")
        t_1 = ["grouplimit", "levellimit", "flavortext", "stats", "rules", "active", "passive", "unlockedpassive",
               "consumable", "unique"]
        t_2 = {
            t_1[0]: "<grouplimit>(.*?)</grouplimit>",
            t_1[1]: "<levellimit>(.*?)</levellimit>",
            t_1[2]: "<flavortext>(.*?)</flavortext>",
            t_1[3]: "<stats>(.*?)</stats>",
            t_1[4]: "<rules>(.*?)</rules>",
            t_1[5]: "<active>(.*?：</active>.*?)<.*?>",
            t_1[6]: "<passive>(.*?：</passive>.*?)<.*?>",
            t_1[7]: "<unlockedpassive>(.{1,10}：</unlockedpassive>.*?)<.*?>",
            t_1[8]: "<consumable>(.*?：</consumable>.*?)<.*?>",
            t_1[9]: "<unique>(.*?：</unique>.*?)<.*?>"
        }
        t_stats_2 = {}
        for t_3 in t_1:
            t_4 = re.compile(t_2[t_3]).findall(t_desc)
            t_desc = re.compile(t_2[t_3]).sub("", t_desc)
            t_desc = re.compile("<" + t_3 + ">").sub("", t_desc)
            t_desc = re.compile("</" + t_3 + ">").sub("", t_desc)
            t_stats_2[t_3] = t_4
        t_stats_2["others"] = [re.compile("<.*?>").sub("", t_desc)]
        for key in t_stats_2.keys():
            if t_stats_2[key]:
                t_stats_key = t_stats_2[key].copy()
                t_stats_2[key].clear()
                for i in range(0, len(t_stats_key)):
                    t_1 = t_stats_key[i].split("<br/>")
                    for t_2 in t_1:
                        if t_2:
                            t_stats_2[key].append(re.compile('<(.*?)>').sub("", t_2))
        tree = doc("#itemFromTree > div > div:nth-child(2) > ul > li").items()
        trees = []
        for _ in tree:
            tree_src = _.find("img").attr("src")
            trees.append(tree_src.split("/")[-1].split(".")[0])
        t_stats_2["tree"] = trees
        t_stats_3 = dict(t_stats_1, **t_stats_2)
        equipment = dict(equipment, **t_stats_3)
        print(equipment)
        download_img(equipment["img"], self.equipment_dir, check_name_valid(equipment["id"]))
        save_to_sqlite3_equipment_1(cursor, self.equipment_dir, equipment)

    def getlol(self, browser: WebDriver, wait, cursor, progressbar: ProgressBar):
        try:
            browser.get('http://lol.qq.com/web201310/info-heros.shtml')
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#pageTAB")))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#jSearchHeroDiv")))
            self.g_count = 0
            tab_items = browser.find_elements_by_css_selector("#pageTAB > ul > li")
            for i in range(0, len(tab_items)):
                if self.flag_should_stop:
                    return False
                if i == 0:
                    flag_hero = self.get_hero(browser, wait, cursor, progressbar)
                    if not flag_hero:
                        return False
                elif i == 1:
                    flag_equipment = self.get_equipment(browser, wait, cursor, progressbar)
                    if not flag_equipment:
                        return False
                else:
                    break
            return True
        except TimeoutException:
            self.g_count += 1
            if self.g_count < 4:
                print('Open page error, try again...')
                self.getlol(browser, wait, cursor, progressbar)
            else:
                print('Can not open the page!')
                return False
        except NoSuchWindowException:
            print('Browser has closed')
            return False
        except Exception as e:
            print(e)
            return False

    # def main():
    #     # browser = webdriver.PhantomJS(executable_path="phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    #     browser = webdriver.Firefox()
    #     wait = WebDriverWait(browser, 5)
    #     conn = sqlite3.connect("lol.db")
    #     cursor = conn.cursor()
    #
    #     check_db(cursor)
    #     getlol(browser, wait, cursor)
    #
    #     conn.commit()
    #     cursor.close()
    #     conn.close()
    #     browser.close()

    def main_external(self, progressbar: ProgressBar, type_update):
        if type_update == 0:
            browser = webdriver.PhantomJS(executable_path="phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
        else:
            browser = webdriver.Firefox()
        wait = WebDriverWait(browser, 5)
        conn = sqlite3.connect("lol.db")
        cursor = conn.cursor()

        check_db(cursor)
        flag_lol = self.getlol(browser, wait, cursor, progressbar)
        if self.flag_should_stop:
            if progressbar:
                progressbar.step = -2
            cursor.close()
            conn.close()
            try:
                browser.close()
            except WebDriverException as e:
                print(e)
            return
        if not flag_lol and progressbar:
            progressbar.step = -1
        conn.commit()
        cursor.close()
        conn.close()
        try:
            browser.close()
        except WebDriverException as e:
            print(e)

    def stop(self):
        self.flag_should_stop = True

        # if __name__ == '__main__':
        #     browser = webdriver.Firefox()
        #     wait = WebDriverWait(browser, 5)
        #     conn = sqlite3.connect("lol.db")
        #     cursor = conn.cursor()
        #     get_hero_test(browser, wait, cursor)
        #     conn.commit()
        #     cursor.close()
        #     conn.close()
        #     browser.close()
