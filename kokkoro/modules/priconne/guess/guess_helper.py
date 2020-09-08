import os
import sqlite3

from .. import chara

class WinnerJudger:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_chara_id = {}
    
    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)
        
    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''
        
    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False
    
    def set_correct_chara_id(self, gid, cid):
        self.correct_chara_id[gid] = cid
    
    def get_correct_chara_id(self, gid):
        return self.correct_chara_id[gid] if self.correct_chara_id.get(gid) is not None else chara.UNKNOWN
    
    def turn_on(self, gid):
        self.on[gid] = True
        
    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_chara_id[gid] = chara.UNKNOWN

class WinningCounter:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()


    def _connect(self):
        return sqlite3.connect(self.db_path)


    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS WINNINGCOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           COUNT           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')
    
    
    def _record_winning(self, gid, uid):
        try:
            winning_number = self._get_winning_number(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO WINNINGCOUNTER (GID,UID,COUNT) \
                                VALUES (?,?,?)", (gid, uid, winning_number+1))
            conn.commit()       
        except:
            raise Exception('更新表发生错误')


    def _get_winning_number(self, gid, uid):
        try:
            r = self._connect().execute("SELECT COUNT FROM WINNINGCOUNTER WHERE GID=? AND UID=?",(gid,uid)).fetchone()        
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')
  