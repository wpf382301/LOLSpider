import sqlite3

from tools import make_local_dir, check_name_valid


def create_table_hero(cursor_):
    sql_create_table_hero = "CREATE TABLE `hero` (" \
                            "`name` varchar(255) NOT NULL," \
                            "`tag` varchar(255) DEFAULT NULL," \
                            "`物理攻击` int(11) DEFAULT NULL," \
                            "`魔法攻击` int(11) DEFAULT NULL," \
                            "`防御能力` int(11) DEFAULT NULL," \
                            "`上手难度` int(11) DEFAULT NULL," \
                            "`profile` varchar(255) DEFAULT NULL," \
                            "PRIMARY KEY (`name`))"
    try:
        cursor_.execute(sql_create_table_hero)
    except Exception as e:
        print(sql_create_table_hero)
        print(e)


def create_table_skill(cursor_):
    sql_create_table_skill = "CREATE TABLE `skill` (" \
                             "`name` varchar(255) NOT NULL," \
                             "`q_name` varchar(255) DEFAULT NULL," \
                             "`w_name` varchar(255) DEFAULT NULL," \
                             "`e_name` varchar(255) DEFAULT NULL," \
                             "`r_name` varchar(255) DEFAULT NULL," \
                             "`bd_name` varchar(255) DEFAULT NULL," \
                             "`q_img` varchar(255) DEFAULT NULL," \
                             "`w_img` varchar(255) DEFAULT NULL," \
                             "`e_img` varchar(255) DEFAULT NULL," \
                             "`r_img` varchar(255) DEFAULT NULL," \
                             "`bd_img` varchar(255) DEFAULT NULL," \
                             "`q_des` text," \
                             "`w_des` text," \
                             "`e_des` text," \
                             "`r_des` text," \
                             "`bd_des` varchar(255) DEFAULT NULL," \
                             "`q_data` varchar(255) DEFAULT NULL," \
                             "`w_data` varchar(255) DEFAULT NULL," \
                             "`e_data` varchar(255) DEFAULT NULL," \
                             "`r_data` varchar(255) DEFAULT NULL," \
                             "`bd_data` varchar(255) DEFAULT NULL," \
                             "PRIMARY KEY (`name`)," \
                             "CONSTRAINT `skill_ibfk_1` FOREIGN KEY (`name`) REFERENCES `hero` (`name`)" \
                             " ON DELETE CASCADE ON UPDATE CASCADE)"
    try:
        cursor_.execute(sql_create_table_skill)
    except Exception as e:
        print(sql_create_table_skill)
        print(e)


def create_table_skin(cursor_):
    sql_create_table_skin = "CREATE TABLE `skin` (" \
                            "`name` varchar(255) NOT NULL," \
                            "`skin_name` varchar(255) NOT NULL," \
                            "`skin_img` varchar(255) DEFAULT NULL," \
                            "`xianding` varchar(255) DEFAULT NULL," \
                            "`price` varchar(255) DEFAULT NULL," \
                            "`series` varchar(255) DEFAULT NULL," \
                            "PRIMARY KEY (`name`,`skin_name`)," \
                            "CONSTRAINT `skin_ibfk_1` FOREIGN KEY (`name`) REFERENCES `hero` (`name`)" \
                            " ON DELETE CASCADE ON UPDATE CASCADE)"
    try:
        cursor_.execute(sql_create_table_skin)
    except Exception as e:
        print(sql_create_table_skin)
        print(e)


def create_table_equipment(cursor_):
    sql_create_table_equipment = "CREATE TABLE `equipment` (" \
                                 "`id` int(11) NOT NULL," \
                                 "`name` varchar(255) DEFAULT NULL," \
                                 "`cost` int(11) DEFAULT NULL," \
                                 "`levellimit` text," \
                                 "`grouplimit` text," \
                                 "`stats` text," \
                                 "`consumable` text," \
                                 "`active` text," \
                                 "`passive` text," \
                                 "`uniques` text," \
                                 "`others` text," \
                                 "`rules` text," \
                                 "`tree` varchar(255) DEFAULT NULL," \
                                 "`tag` varchar(255) DEFAULT ''," \
                                 "`img` varchar(255) DEFAULT NULL," \
                                 "PRIMARY KEY (`id`))"
    try:
        cursor_.execute(sql_create_table_equipment)
    except Exception as e:
        print(sql_create_table_equipment)
        print(e)


def create_table_equipment_1(cursor_):
    sql_create_table_equipment_1 = "CREATE TABLE `equipment_1` (" \
                                   "`name` varchar(255) NOT NULL," \
                                   "`起始装备` varchar(255) DEFAULT NULL," \
                                   "`核心物品` varchar(255) DEFAULT NULL," \
                                   "`进攻型物品` varchar(255) DEFAULT NULL," \
                                   "`防御型物品` varchar(255) DEFAULT NULL," \
                                   "PRIMARY KEY (`name`)," \
                                   "CONSTRAINT `equipment_1_ibfk_1` FOREIGN KEY (`name`) REFERENCES " \
                                   "`hero` (`name`) ON DELETE CASCADE ON UPDATE CASCADE)"
    try:
        cursor_.execute(sql_create_table_equipment_1)
    except Exception as e:
        print(sql_create_table_equipment_1)
        print(e)


def create_table_equipment_2(cursor_):
    sql_create_table_equipment_2 = "CREATE TABLE `equipment_2` (" \
                                   "`name` varchar(255) NOT NULL," \
                                   "`起始装备` varchar(255) DEFAULT NULL," \
                                   "`核心物品` varchar(255) DEFAULT NULL," \
                                   "`进攻型物品` varchar(255) DEFAULT NULL," \
                                   "`防御型物品` varchar(255) DEFAULT NULL," \
                                   "PRIMARY KEY (`name`)," \
                                   "CONSTRAINT `equipment_2_ibfk_1` FOREIGN KEY (`name`) REFERENCES " \
                                   "`hero` (`name`) ON DELETE CASCADE ON UPDATE CASCADE)"
    try:
        cursor_.execute(sql_create_table_equipment_2)
    except Exception as e:
        print(sql_create_table_equipment_2)
        print(e)


def create_tables(tables, cursor):
    if "hero" not in tables:
        create_table_hero(cursor)
    if "skill" not in tables:
        create_table_skill(cursor)
    if "skin" not in tables:
        create_table_skin(cursor)
    if "equipment" not in tables:
        create_table_equipment(cursor)
    if "equipment_1" not in tables:
        create_table_equipment_1(cursor)
    if "equipment_2" not in tables:
        create_table_equipment_2(cursor)


def drop_table(table, cursor_):
    sql_drop_table = "DROP TABLE IF EXISTS `%s`" % table
    try:
        cursor_.execute(sql_drop_table)
    except Exception as e:
        print(sql_drop_table)
        print(e)


def find_type(table, tag, cursor_):
    result = None
    sql = "SELECT * from {} where tag like '%{}%'".format(table, tag)
    try:
        cursor_.execute(sql)
        result = cursor_.fetchall()
    except sqlite3.OperationalError:
        print(sql)
        print("未找到%s表,重新创建" % table)
        # drop_table(table, cursor_)
        if table == "hero":
            create_table_hero(cursor_)
        else:
            create_table_equipment(cursor_)
        result = find_type(table, tag, cursor_)
    except Exception as e:
        print(sql)
        print(e)
    return result


def find_hero_skin(name, cursor_):
    result = None
    sql = "SELECT * from skin where name = '" + name + "'"
    try:
        cursor_.execute(sql)
        result = cursor_.fetchall()
    except sqlite3.OperationalError:
        print(sql)
        # drop_table("skin", cursor_)
        print("未找到skin表,重新创建")
        create_table_skin(cursor_)
        result = find_hero_skin(name, cursor_)
    except Exception as e:
        print(sql)
        print(e)
    return result


def find_hero_skill(name, cursor_):
    result = None
    sql = "SELECT * from skill where name = '" + name + "'"
    try:
        cursor_.execute(sql)
        result = cursor_.fetchone()
    except sqlite3.OperationalError:
        print(sql)
        # drop_table("skill", cursor_)
        print("未找到skill表,重新创建")
        create_table_skill(cursor_)
        result = find_hero_skill(name, cursor_)
    except Exception as e:
        print(sql)
        print(e)
    return result


def check_db(cursor_):
    sql = "SELECT name FROM sqlite_master where type='table'"
    try:
        cursor_.execute(sql)
        result = cursor_.fetchall()
        if result:
            tables = []
            for _ in result:
                tables.append(_[0])
            create_tables(tables, cursor_)
            if len(result) < 6:
                return False
            else:
                return True
    except Exception as e:
        print(e)


def fuzzy_search(cursor: sqlite3.Cursor, value, table, key, key_word):
    result = None
    sql = "SELECT " + value + " from " + table + " where " + key + " like '%" + key_word + "%'"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except sqlite3.OperationalError:
        print(sql)
        return None
    except Exception as e:
        print(sql)
        print(e)
    return result


def find_hero_sqlite3(cursor, hero_name):
    result = None
    sql = "SELECT name from hero where name = '" + hero_name + "'"
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        print(sql)
        # drop_table("hero", cursor)
        print("未找到hero表,重新创建")
        create_table_hero(cursor)
        return None
    except Exception as e:
        print(sql)
        print(e)
    return result


def find_equipment_sqlite3(cursor, equipment_id):
    result = None
    sql = "SELECT id from equipment where id = {}".format(equipment_id)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        print(sql)
        # drop_table("equipment", cursor)
        print("未找到equipment表,重新创建")
        create_table_equipment(cursor)
        return None
    except Exception as e:
        print(sql)
        print(e)
    return result


def find_(cursor, equipment_id, deep, r: list):
    result = find_build_tree(cursor, equipment_id)
    if not result:
        return
    if len(r) <= deep:
        r.append([])
    r[deep].append(result[0])
    if not result[0]:
        return
    for i in r[deep]:
        if i:
            for j in i.split(","):
                find_(cursor, j, deep + 1, r)


def find_build_tree(cursor, equipment_id):
    result = None
    sql = "SELECT tree from equipment where id = {}".format(equipment_id)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        print(sql)
        print("未找到equipment表,重新创建")
        create_table_equipment(cursor)
        return None
    except Exception as e:
        print(sql)
        print(e)
    return result


def save_to_sqlite3_hero(cursor, hero_name, hero_tags, hero_attributes_dic, profile_dir):
    sql_1 = "INSERT INTO hero(name, tag, profile"
    sql_2 = " VALUES('" + hero_name + "','" + ','.join(hero_tags) + "','" + profile_dir + "'"
    for key in hero_attributes_dic.keys():
        sql_1 = sql_1 + ",`" + key + "`"
        sql_2 = sql_2 + "," + hero_attributes_dic[key]
    sql_1 = sql_1 + ")"
    sql_2 = sql_2 + ")"
    sql = sql_1 + sql_2
    try:
        cursor.execute(sql)
    except Exception as e:
        print(sql)
        print(e)


def save_to_sqlite3_skill(cursor, hero_name, skills_dic, skills_dir):
    sql_1 = "INSERT INTO skill(name"
    sql_2 = " VALUES('" + hero_name + "'"
    for key in skills_dic.keys():
        for _ in skills_dic[key].keys():
            sql_1 = sql_1 + ",`" + _ + "`"
            if '_img' in _:
                sql_2 = sql_2 + ",'" + make_local_dir(
                    skills_dic[key][_], skills_dir, check_name_valid(skills_dic[key][key + '_name'])) + "'"
            else:
                sql_2 = sql_2 + ",'" + skills_dic[key][_] + "'"
    sql_1 = sql_1 + ")"
    sql_2 = sql_2 + ")"
    sql = sql_1 + sql_2
    try:
        cursor.execute(sql)
    except Exception as e:
        print(sql)
        print(e)


def save_to_sqlite3_skin(cursor, hero_name, hero_img_url, skin_dir, name):
    sql = "INSERT INTO skin(name, skin_name, skin_img)" \
          + " VALUES('" + hero_name + "','" + name.replace("'", "''") + "','" \
          + make_local_dir(hero_img_url, skin_dir, check_name_valid(name)).replace("'", "''") + "')"
    try:
        cursor.execute(sql)
    except Exception as e:
        print(sql)
        print(e)


def save_to_sqlite3_equipment(cursor, table_name, hero_name, equipment_dic):
    sql_1 = "INSERT INTO `" + table_name + "`(name"
    sql_2 = " VALUES(`" + hero_name + "`"
    for key in equipment_dic.keys():
        sql_1 = sql_1 + ",`" + key + "`"
        sql_2 = sql_2 + ",'" + ','.join(equipment_dic[key]) + "'"
    sql_1 = sql_1 + ")"
    sql_2 = sql_2 + ")"
    sql = sql_1 + sql_2
    try:
        cursor.execute(sql)
    except Exception as e:
        print(sql)
        print(e)


def save_to_sqlite3_equipment_1(cursor, equipment_dir, equipment_dic):
    sql = "INSERT INTO equipment(id, name, cost, levellimit, grouplimit, stats, consumable, active," \
          " passive, uniques, others, rules, tree, img)" + " VALUES(" + \
          equipment_dic["id"] + ",'" + \
          equipment_dic["name"] + "'," + \
          equipment_dic["cost"] + ",'" + \
          ",".join(equipment_dic["levellimit"]) + "','" + \
          ",".join(equipment_dic["grouplimit"]) + "','" + \
          ",".join(equipment_dic["stats"]) + "','" + \
          ",".join(equipment_dic["consumable"]) + "','" + \
          ",".join(equipment_dic["active"]) + "','" + \
          ",".join(equipment_dic["passive"]) + "','" + \
          ",".join(equipment_dic["unique"]) + "','" + \
          ",".join(equipment_dic["others"]) + "','" + \
          ",".join(equipment_dic["rules"]).replace("'", "''") + "','" + \
          ",".join(equipment_dic["tree"]) + "','" + \
          make_local_dir(equipment_dic["img"], equipment_dir,
                         check_name_valid(equipment_dic["id"])) + "')"
    try:
        cursor.execute(sql)
    except Exception as e:
        print(sql)
        print(e)
