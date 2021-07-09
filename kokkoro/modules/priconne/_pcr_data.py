'''公主连接Re:dive的游戏数据'''


'''角色名称

遵照格式： id: [台服官译简体, 日文原名, 英文名(罗马音), B服官译, 常见别称, 带错别字的别称等] （<-依此顺序）
若暂无台服官译则用日文原名占位，台日用全角括号，英文用半角括号
'''
CHARA_NAME = {
    1000: ["未知角色", "未知キャラ", "Unknown"],
    1001: ["日和", "ヒヨリ", "Hiyori", "日和莉", "猫拳", "🐱👊"],
    1002: ["优衣", "ユイ", "Yui", "种田", "普田", "由衣", "结衣", "ue", "↗↘↗↘"],
    1003: ["怜", "レイ", "Rei", "剑圣", "普怜", "伶"],
    1004: ["禊", "ミソギ", "Misogi", "未奏希", "炸弹", "炸弹人", "💣"],
    1005: ["茉莉", "マツリ", "Matsuri", "跳跳虎", "老虎", "虎", "🐅"],
    1006: ["茜里", "アカリ", "Akari", "妹法", "妹妹法"],
    1007: ["宫子", "ミヤコ", "Miyako", "布丁", "布", "🍮"],
    1008: ["雪", "ユキ", "Yuki", "小雪", "镜子", "镜法", "伪娘", "男孩子", "男孩纸", "雪哥"],
    1009: ["杏奈", "アンナ", "Anna", "中二", "煤气罐"],
    1010: ["真步", "マホ", "Maho", "狐狸", "真扎", "咕噜灵波", "真布", "🦊"],
    1011: ["璃乃", "リノ", "Rino", "妹弓"],
    1012: ["初音", "ハツネ", "Hatsune", "hego", "星法", "星星法", "⭐法", "睡法"],
    1013: ["七七香", "ナナカ", "Nanaka", "娜娜卡", "77k", "77香"],
    1014: ["霞", "カスミ", "Kasumi", "香澄", "侦探", "杜宾犬", "驴", "驴子", "🔍"],
    1015: ["美里", "ミサト", "Misato", "圣母"],
    1016: ["铃奈", "スズナ", "Suzuna", "暴击弓", "暴弓", "爆击弓", "爆弓", "政委"],
    1017: ["香织", "カオリ", "Kaori", "琉球犬", "狗子", "狗", "狗拳", "🐶", "🐕", "🐶👊🏻", "🐶👊"],
    1018: ["伊绪", "イオ", "Io", "老师", "魅魔"],

    1020: ["美美", "ミミ", "Mimi", "兔子", "兔兔", "兔剑", "萝卜霸断剑", "人参霸断剑", "天兔霸断剑", "🐇", "🐰"],
    1021: ["胡桃", "クルミ", "Kurumi", "铃铛", "🔔"],
    1022: ["依里", "ヨリ", "Yori", "姐法", "姐姐法"],
    1023: ["绫音", "アヤネ", "Ayane", "熊锤", "🐻🔨", "🐻"],

    1025: ["铃莓", "スズメ", "Suzume", "女仆", "妹抖"],
    1026: ["铃", "リン", "Rin", "松鼠", "🐿", "🐿️"],
    1027: ["惠理子", "エリコ", "Eriko", "病娇"],
    1028: ["咲恋", "サレン", "Saren", "充电宝", "青梅竹马", "幼驯染", "院长", "园长", "🔋", "普电"],
    1029: ["望", "ノゾミ", "Nozomi", "偶像", "小望", "🎤"],
    1030: ["妮诺", "ニノン", "Ninon", "妮侬", "扇子"],
    1031: ["忍", "シノブ", "Shinobu", "普忍", "鬼父", "💀"],
    1032: ["秋乃", "アキノ", "Akino", "哈哈剑"],
    1033: ["真阳", "マヒル", "Mahiru", "奶牛", "🐄", "🐮", "真☀"],
    1034: ["优花梨", "ユカリ", "Yukari", "由加莉", "黄骑", "酒鬼", "奶骑", "圣骑", "🍺", "🍺👻"],

    1036: ["镜华", "キョウカ", "Kyouka", "小仓唯", "xcw", "小苍唯", "8岁", "八岁", "喷水萝", "八岁喷水萝", "8岁喷水萝"],
    1037: ["智", "トモ", "Tomo", "卜毛"],
    1038: ["栞", "シオリ", "Shiori", "tp弓", "小栞", "白虎弓", "白虎妹"],

    1040: ["碧", "アオイ", "Aoi", "香菜", "香菜弓", "绿毛弓", "毒弓", "绿帽弓", "绿帽"],

    1042: ["千歌", "チカ", "Chika", "绿毛奶"],
    1043: ["真琴", "マコト", "Makoto", "狼", "🐺", "月月", "朋", "狼姐"],
    1044: ["伊莉亚", "イリヤ", "Iriya", "伊利亚", "伊莉雅", "伊利雅", "yly", "吸血鬼", "那个女人"],
    1045: ["空花", "クウカ", "Kuuka", "抖m", "抖"],
    1046: ["珠希", "タマキ", "Tamaki", "猫剑", "🐱剑", "🐱🗡️"],
    1047: ["纯", "ジュン", "Jun", "黑骑", "saber"],
    1048: ["美冬", "ミフユ", "Mifuyu", "子龙", "赵子龙"],
    1049: ["静流", "シズル", "Shizuru", "姐姐"],
    1050: ["美咲", "ミサキ", "Misaki", "大眼", "👀", "👁️", "👁"],
    1051: ["深月", "ミツキ", "Mitsuki", "眼罩", "抖s", "医生"],
    1052: ["莉玛", "リマ", "Rima", "Lima", "草泥马", "羊驼", "🦙", "🐐"],
    1053: ["莫妮卡", "モニカ", "Monika", "毛二力"],
    1054: ["纺希", "ツムギ", "Tsumugi", "裁缝", "蜘蛛侠", "🕷️", "🕸️"],
    1055: ["步未", "アユミ", "Ayumi", "步美", "路人", "路人妹"],
    1056: ["流夏", "ルカ", "Ruka", "大姐", "大姐头", "儿力", "luka", "刘夏"],
    1057: ["吉塔", "ジータ", "Jiita", "姬塔", "团长", "吉他", "🎸", "骑空士", "qks"],
    1058: ["贪吃佩可", "ペコリーヌ", "Pecoriinu", "佩可莉姆", "吃货", "佩可", "公主", "饭团", "🍙"],
    1059: ["可可萝", "コッコロ", "Kokkoro", "可可罗", "妈", "普白"],
    1060: ["凯留", "キャル", "Kyaru", "凯露", "百地希留耶", "希留耶", "Kiruya", "黑猫", "臭鼬", "普黑", "接头霸王", "街头霸王"],
    1061: ["矛依未", "ムイミ", "Muimi", "诺维姆", "Noemu", "夏娜", "511", "无意义", "天楼霸断剑", "姆咪", "母咪"],

    1063: ["亚里莎", "アリサ", "Arisa", "鸭梨瞎", "瞎子", "亚里沙", "鸭梨傻", "亚丽莎", "亚莉莎", "瞎子弓", "🍐🦐", "yls"],

    1065: ["嘉夜", "カヤ", "Kaya", "憨憨龙", "龙拳", "🐲👊🏻", "🐉👊🏻", "接龙笨比", "鬼道嘉夜"],
    1066: ["祈梨", "イノリ", "Inori", "梨老八", "李老八", "龙锤", "🐲🔨"],
    1067: ["穗希", "ホマレ", "Homare"],
    1068: ["拉比林斯达", "ラビリスタ", "Rabirisuta", "迷宫女王", "模索路晶", "模索路", "晶"],
    1069: ["真那", "マナ", "Mana", "霸瞳皇帝", "千里真那", "千里", "霸瞳", "霸铜"],
    1070: ["似似花", "ネネカ", "Neneka", "变貌大妃", "现士实似似花", "現士実似々花", "現士実", "现士实", "nnk", "448", "捏捏卡", "变貌", "大妃"],
    1071: ["克莉丝提娜", "クリスティーナ", "Kurisutiina", "誓约女君", "克莉丝提娜·摩根", "Christina", "Cristina", "克总", "女帝", "克", "摩根"],
    1072: ["可萝爹", "長老", "Chourou", "岳父", "爷爷"],
    1073: ["拉基拉基", "ラジニカーント", "Rajinigaanto", "跳跃王", "Rajiraji", "Lajilaji", "垃圾垃圾", "教授"],

    1075: ["贪吃佩可(夏日)", "ペコリーヌ(サマー)", "Pekoriinu(Summer)", "佩可莉姆(夏日)", "水吃", "水饭", "水吃货", "水佩可", "水公主", "水饭团", "水🍙", "泳吃", "泳饭", "泳吃货", "泳佩可", "泳公主", "泳饭团", "泳🍙", "泳装吃货", "泳装公主", "泳装饭团", "泳装🍙", "佩可(夏日)", "🥡", "👙🍙", "泼妇"],
    1076: ["可可萝(夏日)", "コッコロ(サマー)", "Kokkoro(Summer)", "水白", "水妈", "水可", "水可可", "水可可萝", "水可可罗", "泳装妈", "泳装可可萝", "泳装可可罗"],
    1077: ["铃莓(夏日)", "スズメ(サマー)", "Suzume(Summer)", "水女仆", "水妹抖"],
    1078: ["凯留(夏日)", "キャル(サマー)", "Kyaru(Summer)", "凯露(夏日)", "水黑", "水黑猫", "水臭鼬", "泳装黑猫", "泳装臭鼬", "潶", "溴", "💧黑"],
    1079: ["珠希(夏日)", "タマキ(サマー)", "Tamaki(Summer)", "水猫剑", "水猫", "渵", "💧🐱🗡️", "水🐱🗡️"],
    1080: ["美冬(夏日)", "ミフユ(サマー)", "Mifuyu(Summer)", "水子龙", "水美冬"],
    1081: ["忍(万圣节)", "シノブ(ハロウィン)", "Shinobu(Halloween)", "万圣忍", "瓜忍", "🎃忍", "🎃💀"],
    1082: ["宫子(万圣节)", "ミヤコ(ハロウィン)", "Miyako(Halloween)", "万圣宫子", "万圣布丁", "狼丁", "狼布丁", "万圣🍮", "🐺🍮", "🎃🍮", "👻🍮"],
    1083: ["美咲(万圣节)", "ミサキ(ハロウィン)", "Misaki(Halloween)", "万圣美咲", "万圣大眼", "瓜眼", "🎃眼", "🎃👀", "🎃👁️", "🎃👁"],
    1084: ["千歌(圣诞节)", "チカ(クリスマス)", "Chika(Xmas)", "圣诞千歌", "圣千", "蛋鸽", "🎄💰🎶", "🎄千🎶", "🎄1000🎶"],
    1085: ["胡桃(圣诞节)", "クルミ(クリスマス)", "Kurumi(Xmas)", "圣诞胡桃", "圣诞铃铛"],
    1086: ["绫音(圣诞节)", "アヤネ(クリスマス)", "Ayane(Xmas)", "圣诞熊锤", "蛋锤", "圣锤", "🎄🐻🔨", "🎄🐻"],
    1087: ["日和(新年)", "ヒヨリ(ニューイヤー)", "Hiyori(NewYear)", "新年日和", "春猫", "👘🐱"],
    1088: ["优衣(新年)", "ユイ(ニューイヤー)", "Yui(NewYear)", "新年优衣", "春田", "新年由衣"],
    1089: ["怜(新年)", "レイ(ニューイヤー)", "Rei(NewYear)", "春剑", "春怜", "春伶", "新春剑圣", "新年怜", "新年剑圣"],
    1090: ["惠理子(情人节)", "エリコ(バレンタイン)", "Eriko(Valentine)", "情人节病娇", "恋病", "情病", "恋病娇", "情病娇"],
    1091: ["静流(情人节)", "シズル(バレンタイン)", "Shizuru(Valentine)", "情人节静流", "情姐", "情人节姐姐"],
    1092: ["安", "アン", "An", "胖安", "55kg"],
    1093: ["露", "ルゥ", "Ruu", "逃课女王"],
    1094: ["古蕾娅", "グレア", "Gurea", "龙姬", "古雷娅", "古蕾亚", "古雷亚", "古蕾雅", "🐲🐔", "🐉🐔"],
    1095: ["空花(大江户)", "クウカ(オーエド)", "Kuuka(Ooedo)", "江户空花", "江户抖m", "江m", "花m", "江花"],
    1096: ["妮诺(大江户)", "ニノン(オーエド)", "Ninon(Ooedo)", "江户扇子", "忍扇"],
    1097: ["雷姆", "レム", "Remu", "蕾姆"],
    1098: ["拉姆", "ラム", "Ramu"],
    1099: ["爱蜜莉雅", "エミリア", "Emiria", "艾米莉亚", "emt"],
    1100: ["铃奈(夏日)", "スズナ(サマー)", "Suzuna(Summer)", "瀑击弓", "水爆", "水爆弓", "水暴", "瀑", "水暴弓", "瀑弓", "泳装暴弓", "泳装爆弓"],
    1101: ["伊绪(夏日)", "イオ(サマー)", "Io(Summer)", "水魅魔", "水老师", "泳装魅魔", "泳装老师"],
    1102: ["美咲(夏日)", "ミサキ(サマー)", "Misaki(Summer)", "水大眼", "泳装大眼"],
    1103: ["咲恋(夏日)", "サレン(サマー)", "Saren(Summer)", "水电", "泳装充电宝", "泳装咲恋", "水着咲恋", "水电站", "水电宝", "水充", "👙🔋"],
    1104: ["真琴(夏日)", "マコト(サマー)", "Makoto(Summer)", "水狼", "浪", "水🐺", "泳狼", "泳月", "泳月月", "泳朋", "水月", "水月月", "水朋", "👙🐺"],
    1105: ["香织(夏日)", "カオリ(サマー)", "Kaori(Summer)", "水狗", "泃", "水🐶", "水🐕", "泳狗"],
    1106: ["真步(夏日)", "マホ(サマー)", "Maho(Summer)", "水狐狸", "水狐", "水壶", "水真步", "水maho", "氵🦊", "水🦊", "💧🦊"],
    1107: ["碧(插班生)", "アオイ(編入生)", "Aoi(Hennyuusei)", "生菜", "插班碧"],
    1108: ["克萝依", "クロエ", "Kuroe", "华哥", "黑江", "黑江花子", "花子"],
    1109: ["琪爱儿", "チエル", "Chieru", "切露", "茄露", "茄噜", "切噜"],
    1110: ["优妮", "ユニ", "Yuni", "真行寺由仁", "由仁", "优尼", "u2", "优妮辈先", "辈先", "书记", "uni", "先辈", "仙贝", "油腻", "优妮先辈", "学姐", "18岁黑丝学姐"],
    1111: ["镜华(万圣节)", "キョウカ(ハロウィン)", "Kyouka(Halloween)", "万圣镜华", "万圣小仓唯", "万圣xcw", "猫仓唯", "黑猫仓唯", "mcw", "猫唯", "猫仓", "喵唯"],
    1112: ["禊(万圣节)", "ミソギ(ハロウィン)", "Misogi(Halloween)", "万圣禊", "万圣炸弹人", "瓜炸弹人", "万圣炸弹", "万圣炸", "瓜炸", "南瓜炸", "🎃💣"],
    1113: ["美美(万圣节)", "ミミ(ハロウィン)", "Mimi(Halloween)", "万圣兔", "万圣兔子", "万圣兔兔", "绷带兔", "绷带兔子", "万圣美美", "绷带美美", "万圣🐰", "绷带🐰", "🎃🐰", "万圣🐇", "绷带🐇", "🎃🐇"],
    1114: ["露娜", "ルナ", "Runa", "Luna", "露仓唯", "露cw"],
    1115: ["克莉丝提娜(圣诞节)", "クリスティーナ(クリスマス)", "Kurisutiina(Xmas)", "Christina(Xmas)", "Cristina(Xmas)", "圣诞克", "圣诞克总", "圣诞女帝", "蛋克", "圣克", "必胜客"],
    1116: ["望(圣诞节)", "ノゾミ(クリスマス)", "Nozomi(Xmas)", "圣诞望", "圣诞偶像", "蛋偶像", "蛋望"],
    1117: ["伊莉亚(圣诞节)", "イリヤ(クリスマス)", "Iriya(Xmas)", "圣诞伊莉亚", "圣诞伊利亚", "圣诞伊莉雅", "圣诞伊利雅", "圣诞yly", "圣诞吸血鬼", "圣伊", "圣yly"],

    1119: ["可可萝(新年)", "コッコロ(ニューイヤー)", "Kokkoro(NewYear)", "春可可", "春白", "新年妈", "春妈"],
    1120: ["凯留(新年)", "キャル(ニューイヤー)", "Kyaru(NewYear)", "凯露(新年)", "春凯留", "春黑猫", "春黑", "春臭鼬", "新年凯留", "新年黑猫", "新年臭鼬", "唯一神"],
    1121: ["铃莓(新年)", "スズメ(ニューイヤー)", "Suzume(NewYear)", "春铃莓", "春女仆", "春妹抖", "新年铃莓", "新年女仆", "新年妹抖"],
    1122: ["霞(魔法少女)", "カスミ(マジカル)", "Kasumi(MagiGirl)", "魔法少女霞", "魔法侦探", "魔法杜宾犬", "魔法驴", "魔法驴子", "魔驴", "魔法霞", "魔法少驴"],
    1123: ["栞(魔法少女)", "シオリ(マジカル)", "Shiori(MagiGirl)", "魔法少女栞", "魔法tp弓", "魔法小栞", "魔法白虎弓", "魔法白虎妹", "魔法白虎", "魔栞"],
    1124: ["卯月(NGs)", "ウヅキ(デレマス)", "Udsuki(DEREM@S)", "卯月", "卵用", "Udsuki(DEREMAS)", "岛村卯月"],
    1125: ["凛(NGs)", "リン(デレマス)", "Rin(DEREM@S)", "凛", "Rin(DEREMAS)", "涩谷凛", "西部凛"],
    1126: ["未央(NGs)", "ミオ(デレマス)", "Mio(DEREM@S)", "未央", "Mio(DEREMAS)", "本田未央"],
    1127: ["铃(游侠)", "リン(レンジャー)", "Rin(Ranger)", "骑兵松鼠", "游侠松鼠", "游骑兵松鼠", "护林员松鼠", "护林松鼠", "游侠🐿️", "武松"],
    1128: ["真阳(游侠)", "マヒル(レンジャー)", "Mahiru(Ranger)", "骑兵奶牛", "游侠奶牛", "游骑兵奶牛", "护林员奶牛", "护林奶牛", "游侠🐄", "游侠🐮", "牛叉"],
    1129: ["璃乃(奇幻)", "リノ(ワンダー)", "Rino(Wonder)", "璃乃(奇境)", "璃乃(仙境)", "爽弓", "爱丽丝弓", "爱弓", "兔弓", "奇境妹弓", "奇幻妹弓", "奇幻璃乃", "仙境妹弓", "白丝妹弓"],
    1130: ["步未(奇幻)", "アユミ(ワンダー)", "Ayumi(Wonder)", "步未(奇境)", "步未(仙境)", "路人兔", "兔人妹", "爱丽丝路人", "奇境路人", "奇幻路人", "奇幻步未", "仙境路人"],
    1131: ["流夏(夏日)", "ルカ(サマー)", "Ruka(Summer)", "泳装流夏", "水流夏", "泳装刘夏", "水刘夏", "泳装大姐", "泳装大姐头", "水大姐", "水大姐头", "水儿力", "泳装儿力", "水流"],
    1132: ["杏奈(夏日)", "アンナ(サマー)", "Anna(Summer)", "泳装中二", "泳装煤气罐", "水中二", "水煤气罐", "冲", "冲二"],
    1133: ["七七香(夏日)", "ナナカ(サマー)", "Nanaka(Summer)", "泳装娜娜卡", "泳装77k", "泳装77香", "水娜娜卡", "水77k", "水77香", "水七七香", "泳装七七香"],
    1134: ["初音(夏日)", "ハツネ(サマー)", "Hatsune(Summer)", "水星", "海星", "水hego", "水星法", "泳装星法", "水⭐法", "水睡法", "湦"],
    1135: ["美里(夏日)", "ミサト(サマー)", "Misato(Summer)", "水母", "泳装圣母", "水圣母"],
    1136: ["纯(夏日)", "ジュン(サマー)", "Jun(Summer)", "泳装黑骑", "水黑骑", "泳装纯", "水纯", "小次郎"],
    1137: ["茜里(天使)", "アカリ(エンジェル)", "Akari(Angel)", "天使妹法", "天使茜里", "丘比特妹法"],
    1138: ["依里(天使)", "ヨリ(エンジェル)", "Yori(Angel)", "天使姐法", "天使依里", "丘比特姐法"],
    1139: ["纺希(万圣节)", "ツムギ(ハロウィン)", "Tsumugi(Halloween)", "万圣裁缝", "万圣蜘蛛侠", "🎃🕷️", "🎃🕸️", "万裁", "瓜裁", "鬼裁", "鬼才"],
    1140: ["怜(万圣节)", "レイ(ハロウィン)", "Rei(Halloween)", "万圣剑圣", "万剑", "瓜剑", "瓜怜", "万圣怜"],
    1141: ["茉莉(万圣节)", "マツリ(ハロウィン)", "Matsuri(Halloween)", "万圣跳跳虎", "万圣老虎", "瓜虎", "🎃🐅"],








    # =================================== #
    1701: ["环奈", "カンナ", "Kanna", "桥本环奈", "毛大力", "毛小力", "毛六力", "可大萝", "大可萝", "缝合怪"],








    # =================================== #

    1802: ["优衣(公主)", "ユイ(プリンセス)", "Yui(Princess)", "公主优衣", "公主yui", "公主种田", "公主田", "公主ue", "掉毛优衣", "掉毛yui", "掉毛ue", "掉毛", "飞翼优衣", "飞翼ue", "飞翼", "飞翼高达", "飞田"],

    1804: ["贪吃佩可(公主)", "ペコリーヌ(プリンセス)", "Pekoriinu(Princess)", "公主吃", "公主饭", "公主吃货", "公主佩可", "公主饭团", "公主🍙", "命运高达", "高达", "命运公主", "高达公主", "命吃", "春哥高达", "🤖🍙", "🤖"],
    1805: ["可可萝(公主)", "コッコロ（プリンセス）", "Kokkoro(Princess)", "公主妈", "月光妈", "蝶妈", "蝴蝶妈", "月光蝶妈", "公主可", "公主可萝", "公主可可萝", "月光可", "月光可萝", "月光可可萝", "蝶可", "蝶可萝", "蝶可可萝"],



    # =================================== #
    1900: ["爱梅斯", "アメス", "Amesu", "菲欧", "フィオ", "Fio"],






    1907: ["大古", "タイゴ", "Taigo", "大吾", "鬼道大吾"],
    1908: ["花凛", "カリン", "Karin", "绿毛恶魔"],
    1909: ["涅比亚", "ネビア", "Nevia", "Nebia"],
    1910: ["真崎", "マサキ", "Masaki"],
    1911: ["米涅尔β", "ミネルβ", "MineruBeta", "米涅尔", "ミネル", "Mineru"],


    1914: ["豪绅", "ゴウシン", "Goushin"],
    1915: ["克里吉塔", "クレジック", "Kurejikku"],
    1916: ["基洛", "キイロ", "Kiiro"],
    1917: ["善", "ゼーン", "Seen"],
    1918: ["兰法", "ランファ", "Ranfa"],
    1919: ["阿佐尔德", "アンゾールド", "Anzoorudo"],
    1920: ["美空", "ミソラ", "Misora"],









    # =================================== #
    4031: ["骷髅", "髑髏", "Dokuro", "骷髅老爹", "老爹"],
 
    9000: ["祐树", "ユウキ", "Yuuki", "骑士", "骑士君"],
    #赛马新增
    9601: ["01", "001", "one"],
    9602: ["02", "002", "two"],
    9603: ["03", "003", "three"],
    9604: ["04", "004", "four"]
}

# 名字, 公会, 生日, 年龄, 身高, 体重, 血型, 种族, 喜好, 声优
CHARA_DATA= {
    1001: ["日和", "破晓之星", "8月27日", "16", "155", "44", "A", "兽人族", "助人、打气加油", "东山奈央"],
    1002: ["优衣", "破晓之星", "4月5日", "17", "158", "47", "O", "人族", "料理、观察人类", "种田梨沙"],
    1003: ["怜", "破晓之星", "1月12日", "18", "163", "46", "B", "魔族", "读书、骑马、茶", "早见沙织"],
    1004: ["禊", "小小甜心", "8月10日", "9", "128", "27", "O", "人族", "恶作剧、探险", "诸星堇"],
    1005: ["茉莉", "王宫骑士团", "11月25日", "12", "146", "40", "O", "兽人族", "英雄扮演游戏", "下田麻美"],
    1006: ["茜里", "恶魔伪王国军", "11月22日", "13", "150", "42", "O", "魔族", "萨克斯风", "浅仓杏美"],
    1007: ["宫子", "恶魔伪王国军", "1月23日", "14", "130", "32", "B", "魔族", "吃布丁", "雨宫天"],
    1008: ["雪", "纯白之翼 兰德索尔分部", "10月10日", "14", "150", "40", "AB", "精灵族", "欣赏镜中的自己", "大空直美"],
    1009: ["杏奈", "暮光流星群", "7月5日", "17", "159", "45", "A", "魔族", "写小说", "高野麻美"],
    1010: ["真步", "自卫团", "9月22日", "16", "155", "42", "O", "兽人族", "幻想、收集玩偶", "内田真礼"],
    1011: ["璃乃", "拉比林斯", "8月25日", "15", "156", "44", "A", "人族", "裁缝", "阿澄佳奈"],
    1012: ["初音", "森林守卫", "12月24日", "17", "156", "46", "A", "精灵族", "和妹妹一起玩、回笼觉、午睡、早睡", "大桥彩香"],
    1013: ["七七香", "暮光流星群", "8月21日", "18", "166", "55", "O", "魔族", "读书、魔法", "佳村遥"],
    1014: ["霞", "自卫团", "11月3日", "15", "152", "41", "AB", "兽人族", "读书、推理", "水濑祈"],
    1015: ["美里", "森林守卫", "9月5日", "21", "165", "54", "O", "精灵族", "制作绘本", "国府田麻理子"],
    1016: ["铃奈", "月光学院", "4月10日", "18", "167", "48", "O", "魔族", "时尚", "上坂堇"],
    1017: ["香织", "自卫团", "7月7日", "19", "158", "53", "A", "兽人族", "跳舞、空手道", "高森奈津美"],
    1018: ["伊绪", "月光学院", "8月14日", "23", "162", "52", "B", "魔族", "看恋爱小说、恋爱剧、恋爱漫画", "伊藤静"],

    1020: ["美美", "小小甜心", "4月3日", "10", "117", "21", "O", "兽人族", "收集可爱的东西", "日高里菜"],
    1021: ["胡桃", "咲恋救济院", "6月9日", "12", "150", "40", "B", "人族", "看戏、扮家家酒", "植田佳奈"],
    1022: ["依里", "恶魔伪王国军", "11月22日", "13", "150", "40", "O", "魔族", "所有游戏", "原纱友里"],
    1023: ["绫音", "咲恋救济院", "5月10日", "14", "148", "38", "B", "人族", "能在房间里玩的游戏", "芹泽优"],

    1025: ["铃莓", "咲恋救济院", "12月12日", "15", "154", "43", "O", "人族", "服侍", "悠木碧"],
    1026: ["铃", "伊丽莎白牧场", "1月1日", "17", "144", "42", "B", "兽人族", "红豆面包", "小岩井小鸟"],
    1027: ["惠理子", "暮光流星群", "7月30日", "16", "154", "43", "B", "魔族", "实验、裁缝、料理", "桥本千波"],
    1028: ["咲恋", "咲恋救济院", "10月4日", "17", "156", "43", "A", "精灵族", "经营、茶会", "堀江由衣"],
    1029: ["望", "慈乐之音", "1月24日", "17", "157", "40", "B", "人族", "看舞台剧、跳舞", "日笠阳子"],
    1030: ["妮诺", "纯白之翼 兰德索尔分部", "8月31日", "16", "163", "51", "O", "人族", "忍术开发", "佐藤聪美"],
    1031: ["忍", "恶魔伪王国军", "12月22日", "18", "157", "42", "AB", "魔族", "占卜", "大坪由佳"],
    1032: ["秋乃", "墨丘利财团", "3月12日", "18", "157", "45", "AB", "人族", "慈善事业", "松嵜丽"],
    1033: ["真阳", "伊丽莎白牧场", "3月3日", "20", "142", "35", "B", "人族", "相声", "新田惠海"],
    1034: ["优花梨", "墨丘利财团", "3月16日", "22", "164", "55", "A", "精灵族", "随意逛街", "今井麻美"],

    1036: ["镜华", "小小甜心", "2月2日", "8", "118", "21", "A", "精灵族", "读书", "小仓唯"],
    1037: ["智", "王宫骑士团", "8月11日", "13", "149", "43", "A", "人族", "剑术、戏弄长者", "茅原实里"],
    1038: ["栞", "伊丽莎白牧场", "11月3日", "14", "153", "40", "A", "兽人族", "读书、散步", "小清水亚美"],

    1040: ["碧", "森林守卫", "6月6日", "13", "158", "44", "AB", "精灵族", "交朋友的想象训练", "花泽香菜"],
    
    1042: ["千歌", "慈乐之音", "6月3日", "17", "163", "46", "O", "人族", "各种乐器", "福原绫香"],
    1043: ["真琴", "自卫团", "8月9日", "17", "168", "54", "O", "兽人族", "做点心", "小松未可子"],
    1044: ["伊莉亚", "恶魔伪王国军", "5月5日", "???", "172", "50", "A", "魔族", "征服世界", "丹下樱"],
    1045: ["空花", "纯白之翼 兰德索尔分部", "11月19日", "18", "157", "49", "AB", "人族", "阅读小说", "长妻树里"],
    1046: ["珠希", "墨丘利财团", "3月1日", "18", "158", "48", "AB", "兽人族", "与猫咪玩耍", "沼仓爱美"],
    1047: ["纯", "王宫骑士团", "10月25日", "25", "171", "50", "A", "人族", "格斗技、入浴", "川澄绫子"],
    1048: ["美冬", "墨丘利财团", "11月11日", "20", "163", "49", "O", "人族", "佣兵等等的打工", "田所梓"],
    1049: ["静流", "拉比林斯", "10月24日", "18", "168", "54", "O", "人族", "所有家事", "天生目仁美"],
    1050: ["美咲", "月光学院", "1月3日", "11", "120", "22", "A", "魔族", "阅读流行杂志、搜集化妆品", "久野美咲"],
    1051: ["深月", "暮光流星群", "3月7日", "27", "166", "53", "A", "人族", "研究、实验", "三石琴乃"],
    1052: ["莉玛", "伊丽莎白牧场", "3月14日", "18", "150", "100", "A", "兽人族", "理毛、聊天", "德井青空"],
    1053: ["莫妮卡", "纯白之翼 兰德索尔分部", "7月28日", "18", "140", "33", "A", "人族", "逛糖果店", "辻亚由美"],
    1054: ["纺希", "慈乐之音", "9月7日", "14", "153", "45", "AB", "人族", "裁缝", "木户衣吹"],
    1055: ["步未", "纯白之翼 兰德索尔分部", "4月7日", "16", "155", "43", "O", "精灵族", "观察", "大关英里"],
    1056: ["流夏", "暮光流星群", "7月11日", "25", "167", "54", "B", "人族", "钓鱼", "佐藤利奈"],
    1057: ["吉塔", "???", "3月10日", "17", "156", "45", "O", "人族", "冒险、聊天", "金元寿子"],
    1058: ["贪吃佩可", "美食殿堂", "3月31日", "17", "156", "46", "O", "人族", "边走边吃、料理", "M·A·O"],
    1059: ["可可萝", "美食殿堂", "5月11日", "11", "140", "35", "B", "精灵族", "冥想、养育动植物", "伊藤美来"],
    1060: ["凯留", "美食殿堂", "9月2日", "14", "152", "39", "A", "兽人族", "和猫咪玩耍", "立花理香"],
    1061: ["矛依未", "???", "8月11日", "16", "148", "40", "O", "人族", "冒险、回忆故事", "潘惠美"],

    1063: ["亚里莎", "???", "6月17日", "15", "155", "42", "O", "精灵族", "搜集漂亮的叶子", "优木加奈"],

    1065: ["嘉夜", "龙族巢穴", "6月25日", "16", "156", "???", "B", "龙人族", "格斗技", "小市真琴"],
    1066: ["祈梨", "龙族巢穴", "9月29日", "13", "145", "???", "AB", "龙人族", "游戏", "藤田茜"],
    
    1070: ["似似花", "???", "3月24日", "24", "149", "???", "O", "精灵族", "模仿、艺术欣赏", "井口裕香"],
    1071: ["克莉丝提娜", "王宫骑士团", "2月7日", "27", "165", "???", "O", "人族", "和强敌之间的竞争", "高桥智秋"],
    
    1092: ["安", "???", "12月1日", "17", "156", "55", "AB", "人族", "读书", "日笠阳子"],
    1093: ["露", "???", "2月4日", "15", "144", "45", "O", "人族", "吃饭、睡觉", "古山贵实子"],
    1094: ["古蕾娅", "???", "11月3日", "17", "167", "67", "B", "半人半龙", "钢琴", "福原绫香"],

    1097: ["雷姆", "???", "2月2日", "17", "154", "???", "???", "鬼族", "戏剧欣赏、诗和散文", "水濑祈"],
    1098: ["拉姆", "???", "2月2日", "17", "154", "???", "???", "鬼族", "读书", "村川梨衣"],
    1099: ["爱蜜莉雅", "???", "9月23日", "114", "164", "???", "???", "半精灵族", "帮帕克梳理毛发、念书", "高桥李依"],
    
    1108: ["克萝依", "圣特蕾莎女子学院(好朋友社)", "8月7日", "17", "154", "42", "O", "精灵族", "飞镖", "种崎敦美"],
    1109: ["琪爱儿", "圣特蕾莎女子学院(好朋友社)", "9月15日", "16", "156", "46", "O", "人族", "跳舞、卡拉OK", "佐仓绫音"],
    1110: ["优妮", "圣特蕾莎女子学院(好朋友社)", "2月28日", "18", "142", "36", "O", "人族", "读书", "小原好美"],
  
    1114: ["露娜", "???", "???", "???", "142", "28", "???", "人族", "找「朋友」之事", "小仓唯"],

    1124: ["卯月(偶像大师)", "new generations", "4月24日", "17", "159", "45", "O", "人族", "和朋友打长电话", "大桥彩香"],
    1125: ["凛(偶像大师)", "new generations", "8月10日", "15", "165", "44", "B", "人族", "带狗散步", "福原绫香"],
    1126: ["未央(偶像大师)", "new generations", "12月1日", "15", "161", "46", "B", "人族", "购物", "原纱友里"],
    }
    
# 数据来自兰德索尔图书馆
total_mana = {1:0, 2:960, 3:1920, 4:2880, 5:3840, 6:4800, 7:5760, 8:6720, 9:7680, 10:8640, 11:9600, 12:11040, 13:12480, 14:13920, 15:15360, 16:17200, 17:19440, 18:22080, 19:25120, 20:28560, 21:32400, 22:36640, 23:41280, 24:46320, 25:51760, 26:57600, 27:63840, 28:70480, 29:77520, 30:84960, 31:92800, 32:101840, 33:112080, 34:123520, 35:136160, 36:150000, 37:165040, 38:184080, 39:207120, 40:234160, 41:265200, 42:300240, 43:339280, 44:382320, 45:429760, 46:481600, 47:537840, 48:598480, 49:663520, 50:732960, 51:806800, 52:885040, 53:967680, 54:1053560, 55:1142640, 56:1234920, 57:1330400, 58:1429080, 59:1530960, 60:1636040, 61:1744320, 62:1855800, 63:1970480, 64:2088360, 65:2209440, 66:2333720, 67:2461200, 68:2591880, 69:2725760, 70:2862840, 71:3003120, 72:3146600, 73:3293280, 74:3443160, 75:3596240, 76:3752520, 77:3912000, 78:4074680, 79:4240560, 80:4409640, 81:4581920, 82:4757400, 83:4936080, 84:5117960, 85:5303040, 86:5491320, 87:5682800, 88:5877480, 89:6075360, 90:6276440, 91:6480720, 92:6688200, 93:6898880, 94:7112760, 95:7329840, 96:7550120, 97:7773600, 98:8000280, 99:8230160, 100:8463240, 101:8699520, 102:8939000, 103:9181680, 104:9427560, 105:9676640, 106:9928920, 107:10184400, 108:10443080, 109:10704960, 110:10970040, 111:11238320, 112:11509800, 113:11784480, 114:12062360, 115:12343440, 116:12627720, 117:12915200, 118:13205880, 119:13499760, 120:13796840, 121:14097120, 122:14400600, 123:14707280, 124:15017160, 125:15330240, 126:15646520, 127:15966000, 128:16288680, 129:16614560, 130:16943640, 131:17275920, 132:17611400, 133:17950080, 134:18291960, 135:18637040, 136:18985320, 137:19336800, 138:19691480, 139:20049360, 140:20410440, 141:20774720, 142:21142200, 143:21512880, 144:21886760, 145:22263840, 146:22644120, 147:23027600, 148:23414280, 149:23804160, 150:24197240, 151:24593520, 152:24993000, 153:25395680, 154:25801560, 155:26210640, 156:26622920, 157:27038400, 158:27457080, 159:27878960, 160:28304040, 161:28732320, 162:29163800, 163:29598480, 164:30036360, 165:30477440, 166:30921720, 167:31369200, 168:31819880, 169:32273760}

total_exp = {1:0, 2:24, 3:72, 4:120, 5:168, 6:216, 7:288, 8:360, 9:432, 10:504, 11:576, 12:648, 13:720, 14:792, 15:864, 16:956, 17:1068, 18:1200, 19:1352, 20:1524, 21:1716, 22:1928, 23:2142, 24:2358, 25:2576, 26:2796, 27:3019, 28:3245, 29:3474, 30:3706, 31:3948, 32:4200, 33:4462, 34:4734, 35:5016, 36:5308, 37:5610, 38:5962, 39:6364, 40:6816, 41:7318, 42:7870, 43:8622, 44:9574, 45:10726, 46:12078, 47:13630, 48:15382, 49:17534, 50:20086, 51:23038, 52:26390, 53:30142, 54:34394, 55:39146, 56:44398, 57:50150, 58:56402, 59:63154, 60:70406, 61:78158, 62:86410, 63:95162, 64:104514, 65:114466, 66:125018, 67:136170, 68:147922, 69:160274, 70:173226, 71:186778, 72:200930, 73:215682, 74:231034, 75:246986, 76:263538, 77:280690, 78:298442, 79:316794, 80:335746, 81:355298, 82:375450, 83:396202, 84:417554, 85:439506, 86:462058, 87:485210, 88:508962, 89:533314, 90:558266, 91:583818, 92:609970, 93:636722, 94:664074, 95:692026, 96:720578, 97:749730, 98:779482, 99:809834, 100:840786, 101:872338, 102:904490, 103:937242, 104:970594, 105:1004546, 106:1039098, 107:1074250, 108:1110002, 109:1146354, 110:1183306, 111:1220858, 112:1259010, 113:1297762, 114:1337114, 115:1377066, 116:1417618, 117:1458770, 118:1500522, 119:1542874, 120:1585826, 121:1629378, 122:1673530, 123:1718282, 124:1763634, 125:1809586, 126:1856138, 127:1903290, 128:1951042, 129:1999394, 130:2048346, 131:2097898, 132:2148050, 133:2198802, 134:2250154, 135:2302106, 136:2354658, 137:2407810, 138:2461562, 139:2515914, 140:2570866, 141:2626418, 142:2682570, 143:2739322, 144:2796674, 145:2854626, 146:2913178, 147:2972330, 148:3032082, 149:3092434, 150:3153386, 151:3214938, 152:3277090, 153:3339842, 154:3403194, 155:3467146, 156:3531698, 157:3596850, 158:3662602, 159:3728954, 160:3795906, 161:3863458, 162:3931610, 163:4000362, 164:4069714, 165:4139666, 166:4210218, 167:4281370, 168:4353122, 169:4425474, 170:4498426}
