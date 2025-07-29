import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class prm_race_table(Base):
	
	# テーブル名
	__tablename__ = 'prm_race_table'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	horse_no = fld.NumericFields(2,0,primary_key=True,default=0)
	frame_no = fld.NumericFields(2,0,default=0)
	horse_id = fld.CharFields(10,default=Null)
	horse_nm_en = fld.CharFields(30,default='')
	sex_age = fld.CharFields(10,default='')
	weight = fld.NumericFields(3,0,default=0)
	jockey_id = fld.CharFields(5,default='')
	horse_weight = fld.NumericFields(3,0,default=0)
	weight_diff = fld.NumericFields(2,0,default=0)
	win_odds = fld.NumericFields(5,2,default=0)
	popular = fld.NumericFields(2,0,default=0)
	trainer_id = fld.CharFields(5,default='')
	updinfo = fld.CharFields(40,default='')
