import os
import sqlite3

import DataUtil
import MyDB
from MyUI import ProgressBar
from tools import download_img, check_name_valid, make_local_dir


class LOLSpider:
    def __init__(self):
        self.hero_dir = "heroes"
        self.equipment_dir = "equipments"
        self.flag_should_stop = False

    def get_hero(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor, progressbar: ProgressBar):
        skins = DataUtil.get_skins_info()
        heroes = DataUtil.get_heroes_info()
        if heroes:
            t_count = 0
            for hero in heroes:
                hero_detail = DataUtil.get_hero_detail(hero['id'])
                if hero_detail:
                    hero_to_save = dict()
                    hero_to_save['name'] = hero['nick'] + '-' + hero['name']
                    hero_to_save['tags'] = [hero['tag1'], hero['tag2']] if not hero['tag3'] else [hero['tag1'],
                                                                                                  hero['tag2'],
                                                                                                  hero['tag3']]
                    hero_to_save['profile'] = 'http://down.qq.com/qqtalk/lolApp/img/hero/{}.png'.format(hero['id'])
                    hero_to_save['attributes'] = {
                        '物理攻击': hero['attack'] if hero['attack'] else '0',
                        '魔法攻击': hero['magic'] if hero['magic'] else '0',
                        '防御能力': hero['defense'] if hero['defense'] else '0',
                        '上手难度': hero['difficulty'] if hero['difficulty'] else '0'
                    }

                    hero_skill = dict()
                    for i in range(1, 6):
                        if i == 1:
                            t_skill = 'bd'
                        elif i == 2:
                            t_skill = 'q'
                        elif i == 3:
                            t_skill = 'w'
                        elif i == 4:
                            t_skill = 'e'
                        else:
                            t_skill = 'r'
                        temp_skill = dict()
                        temp_skill[t_skill + '_name'] = hero_detail['skill{}'.format(i)].split('|')[1]
                        temp_skill[t_skill + '_des'] = hero_detail['skill{}_desc'.format(i)]
                        if i == 1:
                            temp_skill[t_skill + '_img'] = 'http://down.qq.com/qqtalk/lolApp/img/passive/' + \
                                                           hero_detail['skill{}'.format(i)].split('|')[0]
                        else:
                            temp_skill[t_skill + '_img'] = 'http://down.qq.com/qqtalk/lolApp/img/spell/' + \
                                                           hero_detail['skill{}'.format(i)].split('|')[0]
                            if hero_detail['skill{}_expend'.format(i)]:
                                temp_skill[t_skill + '_data'] = hero_detail['skill{}_expend'.format(i)] + ',' + \
                                                                hero_detail['skill{}_cooling'.format(i)]
                            else:
                                temp_skill[t_skill + '_data'] = hero_detail['skill{}_cooling'.format(i)]
                        hero_skill[t_skill] = temp_skill
                    hero_to_save['skills'] = hero_skill

                    if skins:
                        hero_skins = dict()
                        for skin_detail in skins[hero['en_name']]:
                            if skin_detail['name'] == 'default':
                                skin_detail['name'] = '默认皮肤'
                            hero_skins[skin_detail[
                                'name']] = 'http://ossweb-img.qq.com/images/lol/web201310/skin/big{}.jpg'.format(
                                skin_detail['id'])
                        hero_to_save['skins'] = hero_skins

                    self.save_hero(cursor, hero_to_save)
                    conn.commit()
                else:
                    print('获取英雄详情失败({})'.format(hero['nick'] + ' ' + hero['name']))
                t_count += 1
                if progressbar:
                    progressbar.step = t_count / len(heroes) / 2 * progressbar.pbar.maximum()
        else:
            print('获取英雄列表失败')
            return False
        return True

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
        if MyDB.find_hero_sqlite3(cursor, hero['name']):
            MyDB.update_sqlite3_hero(cursor, hero['name'], hero['tags'], hero['attributes'], make_local_dir(hero['profile'], profile_dir, check_name_valid(hero['name'])))
        else:
            MyDB.save_to_sqlite3_hero(cursor, hero['name'], hero['tags'], hero['attributes'], make_local_dir(hero['profile'], profile_dir, check_name_valid(hero['name'])))

        for key in hero['skills'].keys():
            download_img(hero['skills'][key][key + '_img'], skills_dir,
                         check_name_valid(hero['skills'][key][key + '_name']))
        if MyDB.find_hero_skill(hero['name'], cursor):
            MyDB.update_to_sqlite3_skill(cursor, hero['name'], hero['skills'], skills_dir)
        else:
            MyDB.save_to_sqlite3_skill(cursor, hero['name'], hero['skills'], skills_dir)

        for key in hero['skins'].keys():
            download_img(hero['skins'][key], skin_dir, check_name_valid(key))
            if MyDB.find_special_skin(key, cursor):
                MyDB.update_sqlite3_skin(cursor, hero['name'], hero['skins'][key], skin_dir, key)
            else:
                MyDB.save_to_sqlite3_skin(cursor, hero['name'], hero['skins'][key], skin_dir, key)

    def get_equipment(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor, progressbar: ProgressBar):
        goods = DataUtil.get_goods_info()
        if goods:
            t_count = 0
            for good in goods:
                good_to_save = dict()
                good_to_save['name'] = good['name']
                good_to_save['id'] = good['good_id']
                good_detail = DataUtil.get_good_detail(good['good_id'])
                if good_detail:
                    good_to_save['cost'] = good_detail['price'] if good_detail['price'] else '0'
                    good_to_save['stats'] = good_detail['good_desc']
                    good_to_save['tree'] = good_detail['produceneedlist']
                    good_to_save['tag'] = good_detail['proplist']
                    good_to_save['img'] = 'http://ossweb-img.qq.com/images/lol/img/item/{}.png'.format(good['good_id'])
                    download_img(good_to_save['img'], self.equipment_dir, check_name_valid(good_to_save["id"]))
                    if MyDB.find_equipment_sqlite3(cursor, good_to_save['id']):
                        MyDB.update_sqlite3_equipment(cursor, self.equipment_dir, good_to_save)
                    else:
                        MyDB.save_to_sqlite3_equipment(cursor, self.equipment_dir, good_to_save)
                    conn.commit()
                else:
                    print('获取装备详情失败({})'.format(good['name']))
                t_count += 1
                if progressbar:
                    progressbar.step = (t_count / len(goods) + 1) / 2 * progressbar.pbar.maximum()
        else:
            print('获取装备列表失败')
            return False
        return True

    def getlol(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor, progressbar: ProgressBar):
        if not self.get_hero(conn, cursor, progressbar):
            return False
        if not self.get_equipment(conn, cursor, progressbar):
            return False
        return True

    def main_external(self, progressbar: ProgressBar):
        conn = sqlite3.connect("lol.db")
        cursor = conn.cursor()

        flag_lol = self.getlol(conn, cursor, progressbar)
        if self.flag_should_stop:
            if progressbar:
                progressbar.step = -2
            cursor.close()
            conn.close()
            return
        if not flag_lol:
            if progressbar:
                progressbar.step = -1
            cursor.close()
            conn.close()
            return
        conn.commit()
        cursor.close()
        conn.close()

    def stop(self):
        self.flag_should_stop = True
