import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class prm_race_info(Base):
	
	# テーブル名
	__tablename__ = 'prm_race_info'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	race_no = fld.NumericFields(2,0,default=0)
	race_nm = fld.CharFields(100,default='')
	grade = fld.NumericFields(1,0,default=0)
	race_summary1 = fld.CharFields(100,default='')
	race_summary2 = fld.CharFields(100,default='')
	race_summary3 = fld.CharFields(100,default='')
	direction = fld.CharFields(4,default='')
	distance = fld.NumericFields(4,0,default=0)
	ground_kbn = fld.NumericFields(1,0,default=0)
	weather = fld.CharFields(3,default='')
	ground_cond = fld.CharFields(3,default='')
	ground_cond_d = fld.CharFields(3,default='')
	race_time = fld.CharFields(5,default='')
	race_date = fld.DateFields(default=Null)
	head_count = fld.NumericFields(2,0,default=0)
	racecourse_id = fld.CharFields(2,default='')
	updinfo = fld.CharFields(40,default='')
